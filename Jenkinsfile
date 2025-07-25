// Return Repository Name
String getRepoName() {
    def userRemoteConfigs = scm.getUserRemoteConfigs()
    if (userRemoteConfigs && !userRemoteConfigs.isEmpty()) {
        def repoUrl = userRemoteConfigs[0].getUrl()
        if (repoUrl) {
            def repoPart = repoUrl.substring(repoUrl.lastIndexOf('/') + 1)
            return repoPart.split("\\.")[0]
        }
    }
    // If we can't figure out the name, fail the build with a clear error.
    error("Could not determine repository name from SCM configuration.")
    return null
}

pipeline {
    agent {
        kubernetes {
            defaultContainer 'kaniko'
            workspaceVolume genericEphemeralVolume(storageClassName: 'truenas-nfs-csi',  accessModes: 'ReadWriteMany', requestsSize: "50Gi")
            yaml """
kind: Pod
metadata:
  name: kaniko-pod
spec:
  containers:
  - name: kaniko
    image: gcr.io/kaniko-project/executor:debug
    imagePullPolicy: Always
    command:
    - /busybox/cat
    envFrom:
      - secretRef:
          name: registry-jenkins-url
    tty: true
    volumeMounts:
      - name: jenkins-docker-cfg
        mountPath: /kaniko/.docker
  - name: git-tools
    image: alpine/git # A small image with git for the handoff step
    command: ["sleep", "9999"] # Keep the container running
    tty: true
  volumes:
  - name: jenkins-docker-cfg
    projected:
      sources:
      - secret:
          name: jenkins-registry
          items:
            - key: .dockerconfigjson
              path: config.json
"""
        }
    }
    
    environment {
        DISCORD_WEBHOOK = credentials('discord-webhook-url')
        IMAGE_TAG = "v1.${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout Repository') {
            steps {
                checkout scm
                script {
                    env.repoName = getRepoName()
                }
            }
        }

        // STAGE TO PREVENT BUILD LOOPS
        stage('Check Commit Message') {
            steps {
                // Explicitly run this stage in the 'git-tools' container
                container('git-tools') {
                    script {
                        // Mark the repository directory as safe for Git BEFORE running any git commands
                        sh "git config --global --add safe.directory ${env.WORKSPACE}"

                        // Get the commit message and clean it up
                        def commitMsg = sh(script: 'git log -1 --pretty=format:"%s"', returnStdout: true).trim()
                        echo "Raw commit message: '${commitMsg}'"
                        
                        // Also check the author to be extra sure
                        def commitAuthor = sh(script: 'git log -1 --pretty=format:"%an"', returnStdout: true).trim()
                        echo "Commit author: '${commitAuthor}'"
                        
                        // Check if this commit was made by Jenkins CI
                        if (commitMsg.startsWith('ci:') || commitAuthor == 'Jenkins CI') {
                            echo "CI-generated commit detected. Setting SKIP_BUILD=true to prevent build loop."
                            echo "Commit message: ${commitMsg}"
                            echo "Commit author: ${commitAuthor}"
                            env.SKIP_BUILD = "true"
                        } else {
                            echo "Developer commit detected. Proceeding with build."
                            echo "Commit message: ${commitMsg}"
                            echo "Commit author: ${commitAuthor}"
                            env.SKIP_BUILD = "false"
                        }
                    }
                }
            }
        }

        stage('Notify Build Started') {
            when { 
                not { 
                    environment name: 'SKIP_BUILD', value: 'true' 
                } 
            }
            steps {
                script {
                    discordSend description: "🔄 **Building Docker image**\nBranch: `${env.GIT_BRANCH}`\nBuild: `#${env.BUILD_NUMBER}`", 
                              footer: "Started at ${new Date().format('yyyy-MM-dd HH:mm:ss')}", 
                              link: env.BUILD_URL, 
                              result: "UNSTABLE", // Yellow color for "in progress"
                              title: "🚀 Build Started: ${env.JOB_NAME}", 
                              webhookURL: DISCORD_WEBHOOK
                }
            }
        }
        
        stage('Build and Push with Kaniko') {
            when { 
                not { 
                    environment name: 'SKIP_BUILD', value: 'true' 
                } 
            }
            steps {
                container(name: 'kaniko', shell: '/busybox/sh') {
                    withEnv(['PATH+EXTRA=/busybox']) {
                        sh '''#!/busybox/sh
                          # Use the unique IMAGE_TAG for the destination
                          /kaniko/executor -f app/Dockerfile -c `pwd` --destination=$HARBOR/jenkins/$repoName:$IMAGE_TAG
                        '''
                    }
                }
            }
        }

        stage('Update Helm Config in Git (Handoff to Argo CD)') {
            when { 
                not { 
                    environment name: 'SKIP_BUILD', value: 'true' 
                } 
            }
            steps {
                container(name: 'git-tools') {
                    script {
                        withCredentials([usernamePassword(credentialsId: 'GitHub-jenkins', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                            
                            // Configure git user identity
                            sh "git config --global user.email 'jenkins@tyreyalv.com'"
                            sh "git config --global user.name 'Jenkins CI'"
                            
                            // Install yq to safely edit the YAML file
                            sh "apk add --no-cache yq"
                            
                            // Modify the Helm values file with the new image tag and app version
                            sh "yq e '.image.tag = \"${IMAGE_TAG}\"' -i helm/values.yaml"
                            sh "yq e '.appVersion = \"${IMAGE_TAG}\"' -i helm/values.yaml"
                            
                            // Commit and push the change using the PAT.
                            // Using single quotes prevents the Groovy interpolation warning.
                            sh 'git add helm/values.yaml'
                            // The commit message starts with 'ci:' which is what we check for.
                            sh 'git commit -m "ci: Update image tag to ${IMAGE_TAG}"'
                            sh 'git push https://${GIT_USER}:${GIT_TOKEN}@github.com/tyreyalv/${repoName}.git HEAD:${GIT_BRANCH}'
                        }
                    }
                }
            }
        }
        stage('Trigger Argo CD Sync') {
            when { 
                not { 
                    environment name: 'SKIP_BUILD', value: 'true' 
                } 
            }
            steps {
                container(name: 'git-tools') {
                    script {
                        try {
                            // Wait for git push to propagate
                            echo "Waiting for git changes to propagate..."
                            sleep(time: 15, unit: 'SECONDS')
                            
                            // Check if kubectl can access the argo namespace
                            sh "kubectl get namespace argo"
                            
                            // Trigger Argo CD refresh and sync
                            echo "Triggering Argo CD application refresh..."
                            
                            sh '''
                                kubectl annotate application cicd-portfolio-app -n argo \\
                                    argocd.argoproj.io/refresh=normal \\
                                    --overwrite=true
                            '''
                            
                            sleep(time: 5, unit: 'SECONDS')
                            
                            sh '''
                                kubectl patch application cicd-portfolio-app -n argo \\
                                    --type='merge' \\
                                    -p='{"operation":{"initiatedBy":{"username":"jenkins"},"sync":{"revision":"HEAD"}}}'
                            '''
                            
                            echo "Waiting for Argo CD sync to complete..."
                            timeout(time: 5, unit: 'MINUTES') {
                                script {
                                    def syncComplete = false
                                    def attempts = 0
                                    def maxAttempts = 30 // 5 minutes with 10-second intervals
                                    
                                    while (!syncComplete && attempts < maxAttempts) {
                                        def syncStatus = sh(
                                            script: '''kubectl get application cicd-portfolio-app -n argo -o jsonpath='{.status.sync.status}' 2>/dev/null || echo "Unknown"''',
                                            returnStdout: true
                                        ).trim()
                                        
                                        def healthStatus = sh(
                                            script: '''kubectl get application cicd-portfolio-app -n argo -o jsonpath='{.status.health.status}' 2>/dev/null || echo "Unknown"''',
                                            returnStdout: true
                                        ).trim()
                                        
                                        echo "Sync Status: ${syncStatus}, Health Status: ${healthStatus}"
                                        
                                        if (syncStatus == 'Synced' && healthStatus == 'Healthy') {
                                            syncComplete = true
                                            echo "Argo CD sync completed successfully!"
                                        } else {
                                            sleep(time: 10, unit: 'SECONDS')
                                            attempts++
                                        }
                                    }
                                    
                                    if (!syncComplete) {
                                        echo "Warning: Argo CD sync did not complete within timeout, but continuing..."
                                    }
                                }
                            }
                            
                        } catch (Exception e) {
                            // Don't fail the build if Argo CD sync fails
                            echo "Warning: Failed to trigger Argo CD sync: ${e.getMessage()}"
                            echo "The deployment will still be picked up by Argo CD's normal polling cycle."
                        }
                    }
                }
            }
        }
        
    }
    
    post {
        success {
            script {
                if (env.SKIP_BUILD == 'true') {
                    discordSend description: "✅ **Build loop prevented**\nCommit was generated by CI/CD.", 
                                footer: "Build #${env.BUILD_NUMBER} • Completed in ${currentBuild.durationString.replace(' and counting', '')}", 
                                link: env.BUILD_URL, 
                                result: "SUCCESS", 
                                title: "✅ Build Skipped", 
                                webhookURL: DISCORD_WEBHOOK
                } else {
                    discordSend description: "✅ **Successfully built and pushed image**\nRepository: `${env.repoName}`\nBranch: `${env.GIT_BRANCH}`\nTag: `${IMAGE_TAG}`\nDestination: `https://registry.tyreyalv.com/jenkins/${env.repoName}:${IMAGE_TAG}`", 
                                footer: "Build #${env.BUILD_NUMBER} • Completed in ${currentBuild.durationString.replace(' and counting', '')}", 
                                link: env.BUILD_URL, 
                                result: "SUCCESS", 
                                title: "✅ Build Successful", 
                                webhookURL: DISCORD_WEBHOOK
                }
            }
        }
        
        failure {
            script {
                discordSend description: "❌ **Build failed**\nRepository: `${env.repoName}`\nBranch: `${env.GIT_BRANCH}`\n\nCheck the logs for details.", 
                          footer: "Build #${env.BUILD_NUMBER} • Failed after ${currentBuild.durationString.replace(' and counting', '')}", 
                          link: env.BUILD_URL, 
                          result: "FAILURE", // Red color
                          title: "❌ Build Failed", 
                          webhookURL: DISCORD_WEBHOOK
            }
        }
        
        aborted {
            script {
                discordSend description: "⚠️ **Build aborted**\nRepository: `${env.repoName}`\nBranch: `${env.GIT_BRANCH}`", 
                          footer: "Build #${env.BUILD_NUMBER}", 
                          link: env.BUILD_URL, 
                          result: "ABORTED", // Grey color
                          title: "⚠️ Build Aborted", 
                          webhookURL: DISCORD_WEBHOOK
            }
        }
    }
}
