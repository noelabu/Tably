#!/usr/bin/env python3
"""
Simple Nova Sonic test to verify the connection works
"""

import asyncio
import json
import os
import uuid

try:
    from aws_sdk_bedrock_runtime.client import BedrockRuntimeClient, InvokeModelWithBidirectionalStreamOperationInput
    from aws_sdk_bedrock_runtime.models import InvokeModelWithBidirectionalStreamInputChunk, BidirectionalInputPayloadPart
    from aws_sdk_bedrock_runtime.config import Config, HTTPAuthSchemeResolver, SigV4AuthScheme
    from smithy_aws_core.credentials_resolvers.environment import EnvironmentCredentialsResolver
except ImportError as e:
    print(f"Missing AWS SDK: {e}")
    print("Install with: uv pip install aws-sdk-bedrock-runtime")
    exit(1)

try:
    from app.agents.config import session
except ImportError:
    print("Could not import session from config")
    exit(1)

async def test_nova_sonic():
    """Test basic Nova Sonic connection"""
    
    # Set up credentials
    try:
        credentials = session.get_credentials()
        os.environ['AWS_ACCESS_KEY_ID'] = credentials.access_key
        os.environ['AWS_SECRET_ACCESS_KEY'] = credentials.secret_key
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    except Exception as e:
        print(f"Error setting credentials: {e}")
        return

    # Initialize client
    config = Config(
        endpoint_uri="https://bedrock-runtime.us-east-1.amazonaws.com",
        region='us-east-1',
        aws_credentials_identity_resolver=EnvironmentCredentialsResolver(),
        http_auth_scheme_resolver=HTTPAuthSchemeResolver(),
        http_auth_schemes={"aws.auth#sigv4": SigV4AuthScheme()}
    )
    
    client = BedrockRuntimeClient(config=config)
    
    try:
        print("Testing Nova Sonic connection...")
        
        # Start the stream
        response = await client.invoke_model_with_bidirectional_stream(
            InvokeModelWithBidirectionalStreamOperationInput(model_id='amazon.nova-sonic-v1:0')
        )
        
        print("✅ Successfully connected to Nova Sonic!")
        
        # Send session start
        session_start = {
            "event": {
                "sessionStart": {
                    "inferenceConfiguration": {
                        "maxTokens": 1024,
                        "topP": 0.9,
                        "temperature": 0.7
                    }
                }
            }
        }
        
        event = InvokeModelWithBidirectionalStreamInputChunk(
            value=BidirectionalInputPayloadPart(bytes_=json.dumps(session_start).encode('utf-8'))
        )
        
        await response.input_stream.send(event)
        print("✅ Session start sent successfully!")
        
        # Try to receive a response
        try:
            output = await response.await_output()
            result = await output[1].receive()
            if result.value and result.value.bytes_:
                response_data = result.value.bytes_.decode('utf-8')
                print(f"✅ Received response: {response_data}")
            else:
                print("No response data received")
        except Exception as e:
            print(f"Error receiving response: {e}")
        
        # Close the stream
        await response.input_stream.close()
        print("✅ Stream closed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing Nova Sonic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_nova_sonic())