pipeline {
    agent any

    environment {
        NETWORK_NAME = "cmdb-net"
        MYSQL_CONTAINER = "cmdb-mysql"
        APP_CONTAINER = "cmdb-app"
        PHPMYADMIN_CONTAINER = "cmdb-phpmyadmin"
        MYSQL_ROOT_PASSWORD = "StrongPassword123!"
    }

    stages {

        stage('Cleanup') {
            steps {
                sh '''
                docker rm -f $MYSQL_CONTAINER $APP_CONTAINER $PHPMYADMIN_CONTAINER || true
                docker network rm $NETWORK_NAME || true
                docker rmi cmdb-app-image || true
                '''
            }
        }

        stage('Create Network') {
            steps {
                sh 'docker network create $NETWORK_NAME'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t cmdb-app-image .'
            }
        }

        stage('Start MySQL') {
            steps {
                sh '''
                docker run -d \
                  --name $MYSQL_CONTAINER \
                  --network $NETWORK_NAME \
                  -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD \
                  -e MYSQL_DATABASE=NetworkDevicesCMDB \
                  -e MYSQL_USER=cmdbuser \
                  -e MYSQL_PASSWORD=cmdbpass \
                  mysql:8.3
                '''
            }
        }

        stage('Wait for MySQL') {
            steps {
                sh '''
                echo "Waiting for MySQL..."
                for i in $(seq 1 30); do
                  if docker exec $MYSQL_CONTAINER mysqladmin ping -h "localhost" --silent; then
                    echo "MySQL is ready! Waiting extra time..."
                    sleep 10
                    exit 0
                  fi
                  echo "Still waiting..."
                  sleep 2
                done

                echo "MySQL failed to start in time"
                exit 1
                '''
            }
        }

        stage('Fix MySQL Permissions') {
            steps {
                sh '''
                 docker exec $MYSQL_CONTAINER mysql -uroot -p$MYSQL_ROOT_PASSWORD -e "
                 DROP USER IF EXISTS 'cmdbuser'@'%';
                 CREATE USER 'cmdbuser'@'%' IDENTIFIED WITH mysql_native_password BY 'cmdbpass';
                 GRANT ALL PRIVILEGES ON NetworkDevicesCMDB.* TO 'cmdbuser'@'%';
                 FLUSH PRIVILEGES;
                "
                '''
            }
        }
        
        stage('Run CMDB Script') {
            steps {
                sh '''
                docker run --rm \
                  --name $APP_CONTAINER \
                  --network $NETWORK_NAME \
                  cmdb-app-image \
                  python Python/createcmdb.py
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                docker run --rm \
                  --name ${APP_CONTAINER}_tests \
                  --network $NETWORK_NAME \
                  cmdb-app-image \
                  python -m unittest Python/test_insert.py
                '''
            }
        }

        stage('Start phpMyAdmin') {
            steps {
                sh '''
                docker run -d \
                  --name $PHPMYADMIN_CONTAINER \
                  --network $NETWORK_NAME \
                  -p 8081:80 \
                  -e PMA_HOST=$MYSQL_CONTAINER \
                  -e PMA_PORT=3306 \
                  phpmyadmin/phpmyadmin
                '''
            }
        }

        stage('Check Docker Desktop') {
            steps {
                sh 'docker ps -a'
            }
        }
    }

    post {
        success {
            echo "CMDB running - open http://localhost:8081"
        }
        failure {
            echo "Pipeline failed - check logs"
        }
    }
}