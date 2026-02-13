pipeline {
    agent any
    stages {
        stage ("Preparation"){
            steps {
                sh 'docker network create cmdb || true'
                sh 'docker rm -f $(docker ps -aq) || true'
            }
        }
        stage ("Build Docker Image"){
            steps {
                sh 'cd Docker'
                sh 'docker build -t createcmdb -f Dockerfile .' 
            }
        }
    }
}