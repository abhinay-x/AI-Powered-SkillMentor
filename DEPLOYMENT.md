# SkillMentor AWS Deployment Guide

This guide provides instructions for deploying the SkillMentor application on AWS for scalability and reliability.

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Docker installed locally
- Git repository with your SkillMentor codebase

## Architecture Overview

The SkillMentor platform will be deployed using the following AWS services:

- **EC2**: Host the Flask web application
- **S3**: Store the FAISS index and document dataset
- **SageMaker**: Host the fine-tuned LLaMA model (or alternatively, use AWS Bedrock)
- **CloudWatch**: Monitor performance and errors
- **Auto Scaling**: Scale the application based on traffic

## Deployment Steps

### 1. Set Up EC2 Instance

1. Launch an EC2 instance:
   ```bash
   # Create a security group for the EC2 instance
   aws ec2 create-security-group --group-name skillmentor-sg --description "SkillMentor Security Group"
   
   # Allow HTTP, HTTPS, and SSH traffic
   aws ec2 authorize-security-group-ingress --group-name skillmentor-sg --protocol tcp --port 80 --cidr 0.0.0.0/0
   aws ec2 authorize-security-group-ingress --group-name skillmentor-sg --protocol tcp --port 443 --cidr 0.0.0.0/0
   aws ec2 authorize-security-group-ingress --group-name skillmentor-sg --protocol tcp --port 22 --cidr YOUR_IP_ADDRESS/32
   
   # Launch EC2 instance (t2.medium recommended)
   aws ec2 run-instances --image-id ami-xxxxxxxxxxxxxxxxx --count 1 --instance-type t2.medium --key-name your-key-pair --security-group-ids sg-xxxxxxxxxxxxxxxxx
   ```

2. Connect to your EC2 instance:
   ```bash
   ssh -i /path/to/your-key-pair.pem ec2-user@your-instance-ip
   ```

3. Install Docker on the EC2 instance:
   ```bash
   sudo yum update -y
   sudo amazon-linux-extras install docker
   sudo service docker start
   sudo systemctl enable docker
   sudo usermod -a -G docker ec2-user
   ```

### 2. Prepare S3 Storage

1. Create an S3 bucket for FAISS index and documents:
   ```bash
   aws s3 mb s3://skillmentor-data
   ```

2. Upload your data to S3:
   ```bash
   aws s3 cp data/processed/faiss_index.bin s3://skillmentor-data/faiss_index.bin
   aws s3 cp data/processed/documents.txt s3://skillmentor-data/documents.txt
   ```

### 3. Create Docker Image

1. Create a Dockerfile in your project root:
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   # Download NLTK data
   RUN python -c "import nltk; nltk.download('punkt')"

   # Set environment variables
   ENV FLASK_APP=app.py
   ENV FLASK_ENV=production
   ENV PORT=8080

   # Download index from S3
   CMD aws s3 cp s3://skillmentor-data/faiss_index.bin data/processed/faiss_index.bin && \
       aws s3 cp s3://skillmentor-data/documents.txt data/processed/documents.txt && \
       gunicorn --bind 0.0.0.0:8080 --workers 3 app:app
   ```

2. Build and push Docker image:
   ```bash
   # Build the Docker image
   docker build -t skillmentor:latest .

   # Tag the image for ECR
   docker tag skillmentor:latest ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/skillmentor:latest

   # Login to ECR
   aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com

   # Create ECR repository
   aws ecr create-repository --repository-name skillmentor

   # Push the image to ECR
   docker push ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/skillmentor:latest
   ```

### 4. Deploy the Application

1. Pull and run the Docker image on your EC2 instance:
   ```bash
   # Pull the image from ECR
   docker pull ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/skillmentor:latest

   # Run the container
   docker run -d -p 80:8080 --name skillmentor \
     -e AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY \
     -e AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY \
     -e AWS_REGION=YOUR_REGION \
     ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/skillmentor:latest
   ```

2. Alternatively, use docker-compose:
   ```yaml
   # docker-compose.yml
   version: '3'
   services:
     skillmentor:
       image: ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/skillmentor:latest
       ports:
         - "80:8080"
       environment:
         - AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
         - AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
         - AWS_REGION=YOUR_REGION
       restart: always
   ```

   ```bash
   docker-compose up -d
   ```

### 5. Set Up SageMaker or Bedrock for LLM Inference

#### Option 1: AWS SageMaker

1. Package your model for SageMaker:
   ```python
   # scripts/prepare_sagemaker_model.py
   import tarfile
   import os

   # Create a tar.gz file for SageMaker
   with tarfile.open('model.tar.gz', 'w:gz') as f:
       f.add('models/fine_tuned_llama', arcname='1')
   ```

2. Upload model to S3:
   ```bash
   aws s3 cp model.tar.gz s3://skillmentor-data/models/model.tar.gz
   ```

3. Create SageMaker model:
   ```bash
   aws sagemaker create-model \
       --model-name skillmentor-llm \
       --primary-container Image=763104351884.dkr.ecr.REGION.amazonaws.com/huggingface-pytorch-inference:1.13.1-transformers4.26.0-gpu-py39-cu117-ubuntu20.04,ModelDataUrl=s3://skillmentor-data/models/model.tar.gz
   ```

4. Create SageMaker endpoint configuration:
   ```bash
   aws sagemaker create-endpoint-config \
       --endpoint-config-name skillmentor-llm-config \
       --production-variants VariantName=AllTraffic,ModelName=skillmentor-llm,InstanceType=ml.g4dn.xlarge,InitialInstanceCount=1
   ```

5. Create endpoint:
   ```bash
   aws sagemaker create-endpoint \
       --endpoint-name skillmentor-llm-endpoint \
       --endpoint-config-name skillmentor-llm-config
   ```

6. Update your application to use the SageMaker endpoint for inference.

#### Option 2: AWS Bedrock

1. In your application code, update the AdviceGenerator to use AWS Bedrock instead of local inference:

   ```python
   import boto3

   def generate_advice(self, query, context):
       # Format context as a single string
       context_text = "\n".join(context)
       
       # Create prompt
       prompt = self.prompt_template.format(
           query=query,
           context=context_text
       )
       
       # Create Bedrock client
       bedrock = boto3.client('bedrock-runtime')
       
       # Call Bedrock API for Llama 2 inference
       response = bedrock.invoke_model(
           modelId='meta.llama2-70b-chat-v1',
           body=json.dumps({
               "prompt": prompt,
               "max_gen_len": 512,
               "temperature": 0.7,
               "top_p": 0.95
           })
       )
       
       # Parse response
       response_body = json.loads(response['body'].read())
       advice = response_body['generation']
       
       return advice
   ```

### 6. Set Up Auto Scaling

1. Create an AMI from your running instance:
   ```bash
   aws ec2 create-image --instance-id i-xxxxxxxxxxxxxxxxx --name "SkillMentor-AMI" --description "AMI for SkillMentor auto scaling"
   ```

2. Create a launch configuration:
   ```bash
   aws autoscaling create-launch-configuration \
       --launch-configuration-name skillmentor-lc \
       --image-id ami-xxxxxxxxxxxxxxxxx \
       --instance-type t2.medium \
       --security-groups sg-xxxxxxxxxxxxxxxxx \
       --key-name your-key-pair
   ```

3. Create an Auto Scaling group:
   ```bash
   aws autoscaling create-auto-scaling-group \
       --auto-scaling-group-name skillmentor-asg \
       --launch-configuration-name skillmentor-lc \
       --min-size 1 \
       --max-size 3 \
       --desired-capacity 1 \
       --vpc-zone-identifier "subnet-xxxxxxxxxxxxxxxxx,subnet-yyyyyyyyyyyyyyyyy"
   ```

4. Create scaling policies:
   ```bash
   aws autoscaling put-scaling-policy \
       --auto-scaling-group-name skillmentor-asg \
       --policy-name scale-out \
       --scaling-adjustment 1 \
       --adjustment-type ChangeInCapacity \
       --cooldown 300
   ```

### 7. Set Up CloudWatch Monitoring

1. Create CloudWatch alarms for CPU utilization:
   ```bash
   aws cloudwatch put-metric-alarm \
       --alarm-name SkillMentor-High-CPU \
       --alarm-description "Alarm when CPU exceeds 70%" \
       --metric-name CPUUtilization \
       --namespace AWS/EC2 \
       --statistic Average \
       --period 300 \
       --evaluation-periods 1 \
       --threshold 70 \
       --comparison-operator GreaterThanThreshold \
       --dimensions "Name=AutoScalingGroupName,Value=skillmentor-asg" \
       --alarm-actions [your-scale-out-policy-arn]
   ```

2. Set up CloudWatch logs:
   ```bash
   # Update your docker-compose.yml
   logging:
     driver: awslogs
     options:
       awslogs-group: skillmentor-logs
       awslogs-region: REGION
       awslogs-stream-prefix: web
   ```

## CI/CD Pipeline (Optional)

For continuous deployment, you can set up a CI/CD pipeline using AWS CodePipeline:

1. Set up CodeCommit repository
2. Configure CodeBuild project
3. Create CodePipeline
4. Connect to your GitHub/CodeCommit repository

## Backup and Maintenance

1. Regularly back up your data:
   ```bash
   # Schedule regular S3 backups
   aws s3 sync s3://skillmentor-data s3://skillmentor-backup/$(date +%Y-%m-%d)
   ```

2. Set up log rotation for your containers:
   ```bash
   # Add to your docker-compose.yml
   logging:
     options:
       max-size: "10m"
       max-file: "3"
   ```

## Monitoring and Troubleshooting

1. Monitor application performance:
   ```bash
   # View container logs
   docker logs -f skillmentor
   
   # View CloudWatch logs
   aws logs get-log-events --log-group-name skillmentor-logs --log-stream-name web/skillmentor
   ```

2. Set up alerts for critical errors:
   ```bash
   aws cloudwatch put-metric-alarm \
       --alarm-name SkillMentor-Error-Count \
       --alarm-description "Alarm when error count exceeds threshold" \
       --metric-name ErrorCount \
       --namespace AWS/Logs \
       --statistic Sum \
       --period 300 \
       --evaluation-periods 1 \
       --threshold 5 \
       --comparison-operator GreaterThanThreshold \
       --dimensions "Name=LogGroupName,Value=skillmentor-logs" \
       --alarm-actions [your-sns-topic-arn]
   ```

## Security Considerations

1. Use IAM roles with least privilege
2. Enable security group restrictions
3. Keep your dependencies up to date
4. Implement HTTPS using AWS Certificate Manager
5. Consider using AWS WAF to protect against common web exploits

## Cost Optimization

1. Use Auto Scaling to match capacity with demand
2. Consider using Spot Instances for non-critical workloads
3. Implement proper instance sizing
4. Use S3 lifecycle policies for data storage 