pipeline {
    agent { label 'linux' }

    options {
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup environment') {
            steps {
                sh '''
                    chmod +x scripts/*.sh
                    ./scripts/setup_env.sh
                '''
            }
        }

        stage('Run test suite') {
            steps {
                sh '''
                    . .venv/bin/activate
                    ./scripts/run_tests.sh
                '''
            }
        }
    }

    post {
        always {
            junit 'reports/junit.xml'
            publishHTML(target: [
                reportDir: 'reports',
                reportFiles: 'report.html',
                reportName: 'QA Test Report'
            ])
            archiveArtifacts artifacts: 'reports/**', fingerprint: true
        }
    }
}