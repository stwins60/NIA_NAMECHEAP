pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('1686a704-e66e-40f8-ac04-771a33b6256d')
        SCANNER_HOME= tool 'sonar-scanner'
        DOCKERHUB_USERNAME = 'idrisniyi94'
        DEPLOYMENT_NAME = 'nia-deployment'
        IMAGE_TAG = "v.0.${env.BUILD_NUMBER}"
        IMAGE_NAME = "${DOCKERHUB_USERNAME}/${DEPLOYMENT_NAME}:${IMAGE_TAG}"
        NAMESPACE = 'nia-site'
        BRANCH_NAME = "${GIT_BRANCH.split('/')[1]}"
        SMTP_SERVER_PASS = credentials('2c133af2-e9eb-4073-b032-00ddcd7366a4')
        PORT = '465'
        SMTP_SERVER = 'smtp.sendgrid.net'
        EMAIL = 'apikey'
        SENTRY_AUTH_TOKEN = credentials('e4ccf9be-902b-4c22-8705-6617c5cce5af')
        SENTRY_ORG = 'sentry'
        SENTRY_PROJECT = 'nigerian-islamic-association'
        SENTRY_ENV = 'production'
    }

    stages {
        stage('Clean workspace') {
            steps {
                cleanWs()
            }
        }
        stage('Checkout') {
            steps {
                git branch: 'master', url: 'https://github.com/stwins60/NIA_NAMECHEAP.git'
            }
        }
        stage('Pytest') {
            steps {
                script {
                    sh "python3 -m pip install -r requirements.txt --no-cache-dir --break-system-packages"
                    sh "pytest --cov=app --cov-report=xml:test-reports/coverage.xml"
                    junit 'test-reports/*.xml'
                }
            }
        }
        stage('Sonarqube Analysis') {
            steps {
                script {
                    withSonarQubeEnv('sonar-server') {
                        sh "$SCANNER_HOME/bin/sonar-scanner -Dsonar.projectKey=nia -Dsonar.projectName=nia"
                    }
                }
            }
        }
        stage('Quality Gate') {
            steps {
                script {
                    withSonarQubeEnv('sonar-server') {
                        waitForQualityGate abortPipeline: false, credentialsId: 'sonar-token'
                    }
                }
            }
        }
        stage('OWASP') {
            steps {
                dependencyCheck additionalArguments: '--scan ./ --disableYarnAudit --disableNodeAudit --nvdApiKey 24d49913-f86d-4c46-a43c-49388a3383ef', odcInstallation: 'DP-Check'
                dependencyCheckPublisher pattern: '**/dependency-check-report.xml'
            }
        }
        stage('Trivy FS Scan') {
            steps {
                script {
                    sh "trivy fs ."
                }
            }
        }
        stage("Login to DockerHub") {
            steps {
                echo "Docker Login"
                sh "echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin"
                echo "Login Successful"
            }
        }
        stage("Docker Build") {
            steps {
                script {
                    echo "Building Image"
                    sh "docker build -t $IMAGE_NAME --build-arg EMAIL=$EMAIL --build-arg SMTP_SERVER=$SMTP_SERVER --build-arg PORT=$PORT --build-arg SMTP_SERVER_PASS=$SMTP_SERVER_PASS ."
                    echo "Image built successful"
                }
            }
        }
        stage("Trivy Image Scan") {
            steps {
                script {
                    sh "trivy image $IMAGE_NAME"
                }
            }
        }
        stage("Docker Push") {
            steps {
                script {
                    sh "docker push $IMAGE_NAME"
                }
            }
        }
        stage("Deploy") {
            steps {
                script {
                    dir('./k8s') {
                        withKubeCredentials(kubectlCredentials: [[caCertificate: '', clusterName: '', contextName: '', credentialsId: 'fff8a37d-0976-4787-a985-a82f34d8db40', namespace: '', serverUrl: '']]) {
                            sh "sed -i 's|IMAGE_NAME|${env.IMAGE_NAME}|g' deployment.yaml"
                            sh "kubectl apply -f deployment.yaml"
                            sh "kubectl apply -f service.yaml"
                        }
                        withKubeCredentials(kubectlCredentials: [[caCertificate: '', clusterName: '', contextName: '', credentialsId: 'fff8a37d-0976-4787-a985-a82f34d8db40', namespace: '', serverUrl: '']]) {
                            def rolloutStatus = sh(script: 'kubectl rollout status deploy $DEPLOYMENT_NAME -n $NAMESPACE', returnStatus: true)
                            if (rolloutStatus != 0) {
                                // Get the rollout status as a text and send it to Slack
                                def deploymentRolloutStatus = sh(script: "kubectl rollout status deploy ${DEPLOYMENT_NAME} -n ${NAMESPACE}", returnStdout: true).trim()
                                
                                // Get the last error logs
                                def podName = sh(script: "kubectl get pods -n ${NAMESPACE} -l app=${DEPLOYMENT_NAME} -o jsonpath='{.items[-1:].metadata.name}'", returnStdout: true).trim()
                                def lastErrorLogs = sh(script: "kubectl logs ${podName} -n ${NAMESPACE} --tail=50", returnStdout: true).trim()
                                
                                // Send the Slack message with rollout status and last error logs
                                slackSend channel: '#alerts', color: 'danger', message: """Deployment to Kubernetes failed. Check the logs for more information. 
                                More Info: ${env.BUILD_URL} 
                                Rollout Status: ${deploymentRolloutStatus} 
                                Last Error Logs: ${lastErrorLogs}"""
                            }
                            else {
                                slackSend channel: '#alerts', color: 'good', message: "Deployment to Kubernetes was successful and currently running on https://nigeriaislamicassociation.org/"
                            }
                        }
                    }
                }
            }
        }
        stage("Release Sentry") {
            steps {
                script {
                    sh "command -v sentry-cli || curl -sL https://sentry.io/get-cli/ | bash"
                    sh """
                        export SENTRY_RELEASE=\$(sentry-cli releases \${env.BUILD_NUMBER})
                        sentry-cli releases new -p \$SENTRY_PROJECT \$SENTRY_RELEASE
                        sentry-cli releases set-commits --auto \$SENTRY_RELEASE
                        sentry-cli releases finalize \$SENTRY_RELEASE
                        sentry-cli releases deploys \$SENTRY_RELEASE new -e \$SENTRY_ENV
                    """
                }
            }
        }
    }
    post {
        success {
           
            slackSend channel: '#alerts', color: 'good', message: "${currentBuild.currentResult}: \nJOB_NAME: ${env.JOB_NAME} \nBUILD_NUMBER: ${env.BUILD_NUMBER} \nBRANCH_NAME: ${env.BRANCH_NAME}. \n More Info ${env.BUILD_URL}"
        }
        failure {

            slackSend channel: '#alerts', color: 'danger', message: "${currentBuild.currentResult}: \nJOB_NAME: ${env.JOB_NAME} \nBUILD_NUMBER: ${env.BUILD_NUMBER} \nBRANCH_NAME: ${env.BRANCH_NAME}. \n More Info ${env.BUILD_URL}"
        }
    }
}