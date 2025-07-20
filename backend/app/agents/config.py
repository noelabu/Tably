import boto3
from strands.models import BedrockModel
from botocore.config import Config

from app.core.config import settings

# Create a custom boto3 session with timeout configuration
session = boto3.Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name='us-east-1'
)

# Configure timeouts for AWS Bedrock
bedrock_config = Config(
    read_timeout=120,  # 2 minutes for read operations
    connect_timeout=30,  # 30 seconds for connection
    retries={'max_attempts': 3}  # Retry up to 3 times
)

# Create a Bedrock model with the custom session
bedrock_model = BedrockModel(
    model_id="amazon.nova-lite-v1:0",
    boto_session=session
)

# Nova Sonic model for voice applications
nova_sonic_model = BedrockModel(
    model_id="amazon.nova-sonic-v1:0",
    boto_session=session,
    stream=False  # Disable streaming for Nova Sonic compatibility
)