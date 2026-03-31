pipeline {
    agent any
    environment {
        // Jenkins'in süreçleri build bitince öldürmemesi için kritik ayar
        JENKINS_NODE_COOKIE = 'dontKillMe'
    }

    stages {
        stage('Temizlik') {
            steps {
                bat '''
                echo Eski surecler temizleniyor...
                taskkill /F /IM python.exe /T 2>nul || echo Python zaten kapali.
                taskkill /F /IM node.exe /T 2>nul || echo Node zaten kapali.
                exit /b 0
                '''
            }
        }

        stage('Elasticsearch Kontrol') {
            steps {
                script {
                    echo 'Elasticsearch ayaga kaldiriliyor (Docker)...'
                    // Docker üzerinden Elasticsearch'ü başlatıyoruz
                    bat 'docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" docker.elastic.co/elasticsearch/elasticsearch:8.12.0 2>nul || docker start elasticsearch'
                }
            }
        }

        stage('Backend & Frontend Hazirlik') {
            steps {
                bat '''
                "C:\\Users\\Kadir\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m venv venv
                
                :: Eksik kütüphaneleri yüklüyoruz
                venv\\Scripts\\python.exe -m pip install --upgrade pip
                venv\\Scripts\\pip.exe install email-validator reportlab
                venv\\Scripts\\pip.exe install -r requirements.txt
                '''
                dir('frontend') {
                    bat 'if not exist node_modules (npm install)'
                }
            }
        }

        stage('🚀 CANLIYA AL (Deploy)') {
            steps {
                echo 'Uygulamalar arka planda baslatiliyor...'
                
                // Backend'i başlat ve hataları logla
                bat 'start /B venv\\Scripts\\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend_hata.log 2>&1'
                
                dir('frontend') {
                    bat 'start /B npm run dev -- --host'
                }
                
                echo 'Sistemin oturmasi icin 15 saniye bekleniyor...'
                sleep 15
                
                echo '--- BACKEND DURUMU ---'
                bat 'if exist backend_hata.log (type backend_hata.log)'
                
                echo '✅ Islem Tamam! http://localhost:8000/docs ve http://localhost:5173 adreslerini kontrol et.'
            }
        }
    }
}