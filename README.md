# CI/CD Portfolio

## CI/CD Portfolio Project: A GitOps Workflow with Jenkins and Argo CD

This repository contains a complete, end-to-end CI/CD pipeline that demonstrates a modern GitOps workflow. It builds a simple Python Flask web application, containerizes it, and deploys it to a Kubernetes cluster using a combination of Jenkins for Continuous Integration and Argo CD for Continuous Deployment.

## Workflow Overview

This project implements a "push-then-pull" model, where CI and CD are two distinct, decoupled processes that communicate through Git.

### CI (Push): Jenkins is responsible for building the application artifact

- A developer pushes a code change to the `/app` directory
- Jenkins builds a new, uniquely tagged Docker image
- Jenkins pushes the image to a container registry
- Jenkins "hands off" to the CD process by pushing a configuration change (the new image tag) back to this Git repository

### CD (Pull): Argo CD is responsible for synchronizing the application state in the cluster

- Argo CD continuously monitors the Git repository
- It detects the new commit made by Jenkins
- It recognizes that the live application is out of sync with the desired state in Git
- It automatically runs an Ansible playbook to apply the new configuration, updating the application in Kubernetes to the new version

## Workflow Diagram

```text
+-----------+      +----------------+      +-------------+      +------------------+
| Developer |----->|   GitHub Repo  |<-----|   Jenkins   |<-----|  Docker Registry |
+-----------+      +----------------+      +-------------+      +------------------+
      |                    ^                      |                      ^
      | 1. Code Push       | 4. Config Push       | 3. Image Push        |
      |                    |                      |                      |
      v                    |                      v                      |
+-----------+      +----------------+      +-------------+      +------------------+
|  Webhook  |----->|   Jenkins      |----->|  Build & Test |----->|  Push to Registry|
+-----------+      |   Pipeline     |      +-------------+      +------------------+
                     +----------------+

---------------------------(Git is the Source of Truth)---------------------------

+----------------+      +-------------+      +-----------------+      +-------------+
|   GitHub Repo  |<-----|   Argo CD   |----->|  Ansible Playbook |----->| Kubernetes  |
+----------------+      +-------------+      +-----------------+      +-------------+
      ^                      |                      |                      |
      | 5. Detects Change    | 6. Syncs State       | 7. Deploys App       |
      |                      |                      |                      |
      +----------------------+----------------------+----------------------+
```

## Technologies Used

- **CI/CD Orchestration**: Jenkins
- **GitOps Controller**: Argo CD
- **Infrastructure as Code**: Ansible
- **Containerization**: Docker, Kaniko
- **Container Registry**: Harbor (or any other OCI-compliant registry)
- **Platform**: Kubernetes
- **Application**: Python (Flask)

## How It Works in Detail

### The CI Pipeline (Jenkinsfile)

The Jenkins pipeline is responsible for the "build" half of the workflow.

- **Trigger**: A webhook on this repository triggers the Jenkins pipeline upon a push to the main branch
- **Checkout & Check**: The pipeline first checks out the code. It then immediately inspects the commit message. If the message starts with `ci:`, it means the commit was made by Jenkins itself, and the pipeline stops gracefully to prevent an infinite build loop
- **Build**: A Kaniko container is used to build a new Docker image from the `app/Dockerfile`. This is a secure, daemonless approach to building images inside a Kubernetes pod
- **Tag & Push**: The new image is tagged with a unique version (e.g., `v1.123` based on the Jenkins build number) and pushed to the configured container registry
- **Handoff**: The final stage uses a separate git-tools container to perform the handoff. It:
  - Checks out the repository again
  - Uses `yq` (a YAML processor) to update the `image_tag` and `app_version` variables in `ansible/group_vars/all.yml`
  - Commits this change with the message `ci: Update image tag to ....`
  - Pushes the commit back to this repository

### The CD Workflow (argo-cd/application.yaml)

The Argo CD Application manifest defines the "deployment" half of the workflow.

- **Source of Truth**: It is configured to watch the `/ansible` path of this repository
- **Ansible Plugin**: It uses the built-in Argo CD Ansible plugin to interpret the source. When a sync is required, Argo CD will execute the `ansible/deploy.yml` playbook
- **Sync Policy**: The application is configured with a `selfHeal` and `prune` policy. This means Argo CD will automatically:
  - Apply any changes it detects in Git
  - Correct any manual changes (drift) made directly in the cluster to ensure the live state always matches the Git state
  - Remove any resources from the cluster that are no longer defined in Git

## Repository Structure

```bash
.
├── ansible/          # Contains all Ansible configuration for deployment.
│   ├── group_vars/   # Variables for the deployment (image tag, etc.).
│   └── roles/        # Reusable Ansible roles.
├── app/              # The Python Flask application source code.
│   ├── app.py
│   └── Dockerfile
├── argo-cd/          # Argo CD Application manifest.
│   └── application.yaml
└── Jenkinsfile       # The definition for the Jenkins CI pipeline.
```

## How to Trigger the Workflow

1. Make a code change inside the `/app` directory
2. Commit the change with a standard commit message (e.g., `feat: Add new API endpoint`)
3. Push the commit to the main branch

This will start the Jenkins pipeline, which will build and push the new image, update the Ansible config, and trigger an automatic deployment via Argo CD.
