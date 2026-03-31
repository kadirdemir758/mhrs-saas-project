stage('Backend & Frontend Hazirlik') {
            steps {
                bat '''
                "C:\\Users\\Kadir\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m venv venv
                
                :: Eksik olan kütüphaneyi ve gereksinimleri kuruyoruz
                venv\\Scripts\\python.exe -m pip install --upgrade pip
                venv\\Scripts\\pip.exe install email-validator
                venv\\Scripts\\pip.exe install -r requirements.txt
                '''
                dir('frontend') {
                    bat 'if not exist node_modules (npm install)'
                }
            }
        }