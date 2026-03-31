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
                bat '''
                :: Python'u tam yoluyla çagırıyoruz
                "C:\\Users\\Kadir\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m venv venv
                
                :: Sanal ortamın içindeki Python ve pip'i direkt kullanarak is garantiye alıyoruz
                venv\\Scripts\\python.exe -m pip install --upgrade pip
                venv\\Scripts\\pip.exe install -r requirements.txt
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