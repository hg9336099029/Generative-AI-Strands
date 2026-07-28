# App AgentCore — Deployment

A Strands Agent wrapped for deployment on **Amazon Bedrock AgentCore Runtime**, containerized with Docker and pushed to Amazon ECR.

## Overview

This service exposes a Strands-based agent (with a sample `get_status` tool) through the `BedrockAgentCoreApp` runtime wrapper, so it can be invoked via AgentCore's standard `/invocations` and `/ping` endpoints once deployed.

## Project Structure

```
app_agentcore/
├── app.py              # AgentCore entrypoint — wraps the agent with BedrockAgentCoreApp
├── agent.py             # Strands Agent definition + tools
├── requirements.txt      # Python dependencies
└── Dockerfile            # ARM64 container build for AgentCore Runtime
```

## Requirements

- Python 3.12+
- Docker Desktop (with `buildx` support)
- AWS CLI configured with credentials (`aws sts get-caller-identity` should succeed)
- An AWS account with access to Amazon Bedrock AgentCore and ECR

## Local Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run locally:

```bash
python app.py
```

## Docker Build

> **Note:** AgentCore Runtime requires **ARM64** containers, exposing **port 8080**, with `/ping` (GET) and `/invocations` (POST) endpoints. `BedrockAgentCoreApp` handles the endpoints and port binding automatically — you only need to make sure the container itself is built for `linux/arm64`.

Build the image:

```bash
docker buildx build --platform linux/arm64 -t app-agentcore .
```

If you hit `Network is unreachable` errors during `pip install` (common with QEMU emulation + corporate VPNs), build with host networking:

```bash
docker buildx build --platform linux/arm64 --network=host -t app-agentcore .
```

## Test Locally

Run the container:

```bash
docker run -p 8080:8080 app-agentcore
```

Health check:

```bash
curl http://localhost:8080/ping
```

Invoke the agent:

```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "check status of server-a"}'
```

## Push to Amazon ECR

1. Create the ECR repository (skip if it already exists):

   ```bash
   aws ecr create-repository --repository-name app-agentcore --region us-east-1
   ```

2. Authenticate Docker to ECR:

   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   ```

3. Build and push (ARM64):

   ```bash
   docker buildx build --platform linux/arm64 \
     -t <account-id>.dkr.ecr.us-east-1.amazonaws.com/app-agentcore:latest \
     --push .
   ```

## Register as an AgentCore Runtime

Once the image is in ECR, create the runtime via `boto3`:

```python
import boto3

client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
response = client.create_agent_runtime(
    agentRuntimeName='app_agentcore',
    agentRuntimeArtifact={
        'containerConfiguration': {
            'containerUri': '<account-id>.dkr.ecr.us-east-1.amazonaws.com/app-agentcore:latest'
        }
    },
    networkConfiguration={"networkMode": "PUBLIC"},
    roleArn='arn:aws:iam::<account-id>:role/AgentRuntimeRole',
    lifecycleConfiguration={
        'idleRuntimeSessionTimeout': 300,
        'maxLifetime': 1800
    },
)
print(response['agentRuntimeArn'])
```

## Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| `failed to resolve source metadata for public.ecr.aws/...` | Network can't reach the AWS ECR public mirror (common on corporate networks/VPNs) | Switch base image to `python:3.12-slim` (Docker Hub) instead of the `public.ecr.aws` mirror |
| `Network is unreachable` during `pip install` in build | Broken networking under QEMU ARM64 emulation | Add `--network=host` to the `docker buildx build` command |
| `docker build` can't find Dockerfile | Wrong working directory, or file misnamed | Confirm you're in the folder containing `Dockerfile` (exact name, no extension) |
| Import errors on startup | `agent.py` and `app.py` module names mismatched | Ensure `app.py` imports with `from agent import agent` |
