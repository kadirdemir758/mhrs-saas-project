pipeline {
    agent any

    stages {
        stage('Temizlik (Eski Surumleri Durdur)') {
            steps {
                bat '''
                echo Eski surecler temizleniyor...
                taskkill /F /IM python.exe /T 2>nul || echo Python zaten calismiyor.
                taskkill /F /IM node.exe /T 2>nul || echo Node zaten calismiyor.
                exit /b 0
                '''
            }
        }

        stage('GitHubdan Kodu Cek') {
            steps {
                git branch: 'main', url: 'https://github.com/kadirdemir758/mhrs-saas-project.git'
            }
        }
        
        stage('Backend Hazirlik') {
            steps {
                bat '''
                "C:\\Users\\Kadir\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m venv venv
                venv\\Scripts\\python.exe -m pip install --upgrade pip
                venv\\Scripts\\pip.exe install -r requirements.txt
                '''
            }
        }
        
        stage('Frontend Hazirlik') {
            steps {
                dir('frontend') {
                    bat '''
                    :: Eksik/hatalı modülleri temizlemek için radikal çözüm
                    if exist node_modules (rd /s /q node_modules)
                    if exist package-lock.json (del /f /q package-lock.json)
                    
                    echo Moduller bastan kuruluyor, bu biraz surebilir...
                    npm install
                    npm run build
                    '''
                }
            }
        }

        stage('🚀 CANLIYA AL (Deploy)') {
            steps {
                echo 'Uygulama arka planda baslatiliyor...'
                
                // Backend'i başlat
                bat 'start /B venv\\Scripts\\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000'
                
                // Frontend'i baslat
                dir('frontend') {
                    bat 'start /B npm run dev -- --host'
                }
                
                echo '✅ MHRS Projesi su an canli! http://localhost:8000 ve http://localhost:5173'
            }
        }
    }
}