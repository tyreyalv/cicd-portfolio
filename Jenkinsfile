// Return Repository Name
String getRepoName() {
    // This is a more robust way to get the repository name.
    // It finds the last '/' in the URL and takes the part after it,
    // then removes the '.git' extension.
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
        // Create a unique, versioned tag using the build number, e.g., v1.1, v1.2 etc.
        IMAGE_TAG = "v1.${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Notify Build Started') {
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
        
        stage('Checkout Repository') {
            steps {
                checkout scm
                script {
                    env.repoName = getRepoName()
                }
            }
        }
        
        stage('Build and Push with Kaniko') {
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

        stage('Update Ansible Config in Git (Handoff to Argo CD)') {
            steps {
                container(name: 'git-tools') {
                    script {
                        // Use a "Username with password" credential.
                        // The ID 'GitHub-jenkins' should now point to a credential with your
                        // GitHub username and a Personal Access Token as the password.
                        withCredentials([usernamePassword(credentialsId: 'GitHub-jenkins', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                            
                            // Mark the repository directory as safe for Git to fix ownership errors
                            sh "git config --global --add safe.directory ${env.WORKSPACE}"

                            // Configure git user identity
                            sh "git config --global user.email 'jenkins@tyreyalv.com'"
                            sh "git config --global user.name 'Jenkins CI'"
                            
                            // Install yq to safely edit the YAML file
                            sh "apk add --no-cache yq"
                            
                            // Modify the Ansible variables file with the new image tag and app version
                            sh "yq e '.image_tag = \"${IMAGE_TAG}\"' -i ansible/group_vars/all.yml"
                            sh "yq e '.app_version = \"${IMAGE_TAG}\"' -i ansible/group_vars/all.yml"
                            
                            // Commit and push the change using the PAT
                            sh "git add ansible/group_vars/all.yml"
                            sh "git commit -m 'ci: Update image tag to ${IMAGE_TAG}'"
                            sh "git push https://${GIT_USER}:${GIT_TOKEN}@github.com/tyreyalv/${repoName}.git HEAD:${env.GIT_BRANCH}"
                        }
                    }
                }
            }
        }
    }
    
    post {
        success {
            script {
                // Correctly report the unique tag that was just built and pushed
                discordSend description: "✅ **Successfully built and pushed image**\nRepository: `${env.repoName}`\nBranch: `${env.GIT_BRANCH}`\nTag: `${IMAGE_TAG}`\nDestination: `https://registry.tyreyalv.com/jenkins/${env.repoName}:${IMAGE_TAG}`", 
                          footer: "Build #${env.BUILD_NUMBER} • Completed in ${currentBuild.durationString.replace(' and counting', '')}", 
                          link: env.BUILD_URL, 
                          result: "SUCCESS", // Green color
                          title: "✅ Build Successful", 
                          webhookURL: DISCORD_WEBHOOK
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
