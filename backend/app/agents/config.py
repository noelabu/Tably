import boto3
from strands.models import BedrockModel

from app.core.config import settings

# Create a custom boto3 session
session = boto3.Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name='us-east-1'
)

# Create a Bedrock model with the custom session
bedrock_model = BedrockModel(
    model_id="amazon.nova-lite-v1:0",
    boto_session=session
)