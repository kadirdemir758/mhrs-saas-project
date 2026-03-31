// ════════════════════════════════════════════════════════════════════════════
//  MHRS SaaS — Jenkinsfile
//  Pipeline: Checkout → Test → Build Image → Deploy to Ubuntu VM
// ════════════════════════════════════════════════════════════════════════════

pipeline {
    agent any

    environment {
        // Jenkins Credentials — configure these in Jenkins → Manage Credentials
        APP_ENV         = 'production'
        DOCKER_IMAGE    = "mhrs-saas"
        DOCKER_TAG      = "${env.BUILD_NUMBER}"
        VM_HOST         = credentials('MHRS_VM_HOST')       // Ubuntu VM IP
        VM_USER         = credentials('MHRS_VM_USER')       // SSH username
        VM_DEPLOY_PATH  = '/opt/mhrs-saas'
    }

    stages {

        // ── Stage 1: Checkout ─────────────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo '📦 Checking out source code...'
                checkout scm
            }
        }

        // ── Stage 2: Install Dependencies ────────────────────────────────────
        stage('Install Dependencies') {
            steps {
                echo '📚 Installing Python dependencies...'
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        // ── Stage 3: Run PyTest ───────────────────────────────────────────────
        stage('Run Tests') {
            steps {
                echo '🧪 Running unit tests...'
                sh '''
                    . .venv/bin/activate
                    python -m pytest tests/ \
                        -v \
                        --tb=short \
                        --junitxml=test-results/junit.xml \
                        -p no:warnings
                '''
            }
            post {
                always {
                    junit 'test-results/junit.xml'
                }
            }
        }

        // ── Stage 4: Build Docker Image ───────────────────────────────────────
        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                sh """
                    docker build \
                        -t ${DOCKER_IMAGE}:${DOCKER_TAG} \
                        -t ${DOCKER_IMAGE}:latest \
                        .
                """
            }
        }

        // ── Stage 5: Deploy to Ubuntu VM ──────────────────────────────────────
        stage('Deploy to Ubuntu VM') {
            steps {
                echo "🚀 Deploying to Ubuntu VM at ${VM_HOST}..."
                sshagent(credentials: ['MHRS_SSH_KEY']) {
                    sh """
                        # 1. Save Docker image as tarball
                        docker save ${DOCKER_IMAGE}:${DOCKER_TAG} | gzip > mhrs-saas-${DOCKER_TAG}.tar.gz

                        # 2. Copy tarball + compose files to VM
                        scp -o StrictHostKeyChecking=no \\
                            mhrs-saas-${DOCKER_TAG}.tar.gz \\
                            docker-compose.yml \\
                            .env.example \\
                            ${VM_USER}@${VM_HOST}:${VM_DEPLOY_PATH}/

                        # 3. SSH into VM: load image and restart services
                        ssh -o StrictHostKeyChecking=no ${VM_USER}@${VM_HOST} << 'EOF'
                            set -e
                            cd ${VM_DEPLOY_PATH}

                            # Load the new image
                            docker load < mhrs-saas-${DOCKER_TAG}.tar.gz

                            # Tag as latest
                            docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest

                            # Restart app container (keeps MariaDB/RabbitMQ/ES running)
                            docker-compose up -d --no-deps --build app

                            # Health check
                            sleep 10
                            curl -f http://localhost:8000/health || exit 1

                            echo "✅ Deployment successful — build ${DOCKER_TAG}"
EOF
                        # 4. Clean up local tarball
                        rm -f mhrs-saas-${DOCKER_TAG}.tar.gz
                    """
                }
            }
        }
    }

    // ── Post Actions ────────────────────────────────────────────────────────
    post {
        success {
            echo "✅ Pipeline succeeded! Build ${DOCKER_TAG} deployed to ${VM_HOST}"
        }
        failure {
            echo "❌ Pipeline FAILED at stage: ${STAGE_NAME}. Check console output."
        }
        always {
            cleanWs()
        }
    }
}
