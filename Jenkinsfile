pipeline {
    agent any

    stages {
        stage('GitHubdan Kodu Cek') {
            steps {
                git branch: 'main', url: 'https://github.com/kadirdemir758/mhrs-saas-project.git'
            }
        }
        
        stage('Backend Kurulumu') {
            steps {
                // Windows'ta bat kullanılır ve venv yolu Scripts klasörüdür
                bat '''
                python -m venv venv
                call venv\\Scripts\\activate
                pip install -r requirements.txt
                '''
            }
        }
        
        stage('Frontend Derleme') {
            steps {
                dir('frontend') {
                    bat '''
                    npm install
                    npm run build
                    '''
                }
            }
        }
    }
}