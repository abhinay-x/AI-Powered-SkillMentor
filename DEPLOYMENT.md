# Deployment Guide for AI-Powered SkillMentor

## Prerequisites
- Docker installed
- Docker Hub account
- GitHub account
- Render account

## Deployment Steps

### 1. Docker Image Preparation
1. Build the Docker image locally:
   ```bash
   docker build -t skillmentor-app .
   ```

2. Test the Docker image:
   ```bash
   docker run -p 5000:5000 skillmentor-app
   ```

### 2. GitHub Actions CI/CD Setup
1. Create Docker Hub access token:
   - Go to Docker Hub
   - Account Settings → Security
   - Create Access Token

2. Add GitHub Secrets
   In your GitHub repository:
   - Settings → Secrets and Variables → Actions
   - Add two secrets:
     - `DOCKER_USERNAME`: Your Docker Hub username
     - `DOCKER_PASSWORD`: Your Docker Hub access token

### 3. Render Deployment
1. Log in to Render (https://render.com)
2. Create New Web Service
   - Connect GitHub repository
   - Choose `AI-Powered-SkillMentor`
   - Environment: Docker
   - Name: skillmentor-service
   - Region: Closest to you
   - Start Command: `python app.py`

### 4. Continuous Deployment
- Every push to `main` branch triggers:
  - Docker image build
  - Image push to Docker Hub
  - Automatic Render deployment

## Troubleshooting
- Verify Docker build works locally
- Check GitHub Actions logs
- Ensure all secrets are correctly set
- Confirm Render service configuration

## Security Notes
- Never commit secrets to repository
- Rotate access tokens periodically
- Use read-only tokens when possible 