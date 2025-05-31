pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-northeast-2'
        AWS_ACCESS_KEY_ID = credentials('ecr-login')
        AWS_SECRET_ACCESS_KEY = credentials('ecr-login')
        ECR_REGISTRY = '341162387145.dkr.ecr.ap-northeast-2.amazonaws.com'
        APP_REPO_NAME = 'nsa'
        S3_BUCKET = 'webgoat-nsa-codeql'
        LAMBDA_NAME = 'trigger-codeql-analysis-ssm'
    }

    stages {
        stage('Checkout') {
            steps {
                deleteDir()
                git branch: 'main',
                    url: 'https://github.com/nsa0320/javulna.git',
                    credentialsId: '1'
            }
        }

        stage('Upload Source for CodeQL') {
            steps {
                sh """
                echo "[📦] 소스코드 압축 중..."
                zip -r source.zip . -x "*.git*" "*.idea*" "target/*"

                echo "[☁️] S3에 업로드 중..."
                aws s3 cp source.zip s3://\$S3_BUCKET/source.zip
                """
            }
        }

        stage('Run CodeQL via Lambda') {
            steps {
                script {
                    def START = System.currentTimeMillis()
                    sh """
                    echo "[🚀] Lambda로 CodeQL 실행 요청 중..."
                    aws lambda invoke \
                      --function-name \$LAMBDA_NAME \
                      --payload '{"s3_key":"source.zip"}' \
                      --region \$AWS_REGION \
                      --cli-binary-format raw-in-base64-out \
                      lambda_output.json

                    echo "[📄] Lambda 응답:"
                    cat lambda_output.json
                    """
                    def END = System.currentTimeMillis()
                    echo "⏱️ CodeQL 분석 요청 소요 시간: ${(END - START) / 1000.0}초"
                }
            }
        }

        stage('Wait for CodeQL SARIF') {
            steps {
                script {
                    echo "[⏳] SARIF 결과 생성 대기 중..."
                    def retries = 60  // 최대 10분 대기
                    def interval = 10 // 초 단위
                    def fileFound = false

                    for (int i = 0; i < retries; i++) {
                        def result = sh(
                            script: "aws s3 ls s3://$S3_BUCKET/result/result.sarif",
                            returnStatus: true
                        )
                        if (result == 0) {
                            echo "[✅] result.sarif 파일이 확인되었습니다."
                            fileFound = true
                            break
                        } else {
                            echo "[⏱️] 아직 result.sarif 없음. ${interval}초 후 재시도..."
                            sleep(interval)
                        }
                    }

                    if (!fileFound) {
                        error("❌ result.sarif 파일을 ${retries * interval}초 동안 찾지 못했습니다.")
                    }
                }
            }
        }

        stage('Download and Publish CodeQL Report') {
            steps {
                sh """
                echo "[📥] 분석 결과 다운로드..."
                aws s3 cp s3://\$S3_BUCKET/result/result.sarif result.sarif

                echo "[📄] SARIF 리포트 HTML 변환"
                python3 scripts/sarif-to-html.py > codeql-report.html
                """
            }
        }

        stage('Publish CodeQL HTML Report') {
            steps {
                publishHTML([
                    reportDir: '.',
                    reportFiles: 'codeql-report.html',
                    reportName: 'CodeQL 분석 리포트',
                    keepAll: true,
                    allowMissing: true,
                    alwaysLinkToLastBuild: true
                ])
            }
        }

        stage('Build JAR') {
            steps {
                sh 'mvn clean package -DskipTests'
            }
        }
    }

    post {
        always {
            echo "🧹 도커 이미지 정리 중..."
            sh 'docker image prune -af || true'
        }
    }
}
