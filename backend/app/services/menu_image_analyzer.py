import base64
import json
import logging
from typing import Dict, List, Optional, Any
from PIL import Image
import io
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

logger = logging.getLogger(__name__)

class MenuImageAnalyzer:
    def __init__(self):
        self.bedrock_client = self._setup_bedrock_client()
        self.model_id = "amazon.nova-pro-v1:0"
    
    def _setup_bedrock_client(self):
        """Setup AWS Bedrock client with AWS credentials for Amazon Nova"""
        try:
            return boto3.client(
                'bedrock-runtime',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
        except Exception as e:
            logger.error(f"Failed to setup Bedrock client: {e}")
            raise
    
    def _encode_image(self, image_bytes: bytes) -> str:
        """Encode image bytes to base64"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def _prepare_image(self, image_bytes: bytes) -> bytes:
        """Prepare and resize image if needed"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (max 20MB for Bedrock)
            max_size = (2048, 2048)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert back to bytes
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            return buffer.getvalue()
        
        except Exception as e:
            logger.error(f"Error preparing image: {e}")
            raise
    
    def _create_analysis_prompt(self) -> str:
        """Create the prompt for menu analysis"""
        return """
        You are an expert menu data extraction agent. Analyze this restaurant menu image and extract structured data.

        Extract the following information from the menu:
        
        1. **Menu Items**: For each item, extract:
           - name: The dish/item name
           - description: Brief description (if available)
           - price: Price in decimal format
           - category: Type of item (appetizer, main course, dessert, beverage, etc.)
           - allergens: List of allergens mentioned (nuts, dairy, gluten, etc.)
           - ingredients: Key ingredients mentioned
           - modifiers: Available modifications (size options, spice level, extras, etc.)
           - combos: If item is part of a combo or meal deal
           - sizes: Available sizes and their prices
           
        2. **Restaurant Information**:
           - restaurant_name: Name of the restaurant (if visible)
           - cuisine_type: Type of cuisine
           
        Return the data in the following JSON format:
        
        {
            "restaurant_info": {
                "restaurant_name": "Restaurant Name",
                "cuisine_type": "Type of cuisine"
            },
            "menu_items": [
                {
                    "name": "Item Name",
                    "description": "Item description",
                    "price": 12.99,
                    "category": "main course",
                    "allergens": ["nuts", "dairy"],
                    "ingredients": ["chicken", "rice", "vegetables"],
                    "modifiers": [
                        {
                            "type": "size",
                            "options": [
                                {"name": "Regular", "price": 0},
                                {"name": "Large", "price": 3.00}
                            ]
                        },
                        {
                            "type": "spice_level",
                            "options": [
                                {"name": "Mild", "price": 0},
                                {"name": "Medium", "price": 0},
                                {"name": "Hot", "price": 0}
                            ]
                        }
                    ],
                    "combos": [
                        {
                            "name": "Lunch Special",
                            "includes": ["main dish", "rice", "drink"],
                            "price": 15.99
                        }
                    ],
                    "sizes": [
                        {"name": "Regular", "price": 12.99},
                        {"name": "Large", "price": 15.99}
                    ]
                }
            ]
        }
        
        Important guidelines:
        - Extract ALL visible menu items
        - If price is not clearly visible, set to null
        - If allergens are not mentioned, use empty array
        - For modifiers, only include those explicitly mentioned
        - Ensure all prices are in decimal format
        - Be thorough but accurate - don't make up information not visible in the image
        """
    
    async def analyze_menu_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """Analyze menu image and extract structured data using Amazon Nova"""
        try:
            # Prepare the image
            prepared_image = self._prepare_image(image_bytes)
            encoded_image = self._encode_image(prepared_image)
            
            # Create the prompt
            prompt = self._create_analysis_prompt()
            
            # Prepare the request body for Amazon Nova
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt
                            },
                            {
                                "image": {
                                    "format": "jpeg",
                                    "source": {
                                        "bytes": encoded_image
                                    }
                                }
                            }
                        ]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 4000,
                    "temperature": 0.1,
                    "topP": 0.9
                }
            }
            
            # Make the request to Bedrock
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_body)
            )
            
            # Parse the response for Amazon Nova
            response_body = json.loads(response['body'].read())
            
            if 'output' in response_body and 'message' in response_body['output'] and 'content' in response_body['output']['message']:
                content_list = response_body['output']['message']['content']
                # Find the text content in the response
                content = ""
                for item in content_list:
                    if 'text' in item:
                        content = item['text']
                        break
                
                # Extract JSON from the response
                try:
                    # Look for JSON content between ```json and ``` or { and }
                    if '```json' in content:
                        json_start = content.find('```json') + 7
                        json_end = content.find('```', json_start)
                        json_content = content[json_start:json_end].strip()
                    elif content.strip().startswith('{'):
                        json_content = content.strip()
                    else:
                        # Try to find the first { and last }
                        start = content.find('{')
                        end = content.rfind('}') + 1
                        if start != -1 and end != 0:
                            json_content = content[start:end]
                        else:
                            raise ValueError("No JSON found in response")
                    
                    result = json.loads(json_content)
                    
                    # Validate the structure
                    if 'menu_items' not in result:
                        result['menu_items'] = []
                    if 'restaurant_info' not in result:
                        result['restaurant_info'] = {}
                    
                    logger.info(f"Successfully analyzed menu image, found {len(result['menu_items'])} items")
                    return result
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from response: {e}")
                    logger.error(f"Response content: {content}")
                    raise ValueError(f"Invalid JSON response from AI model: {e}")
            else:
                raise ValueError("No content in Amazon Nova response")
                
        except ClientError as e:
            logger.error(f"AWS Bedrock error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error analyzing menu image: {e}")
            raise
    
    async def validate_menu_data(self, menu_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the extracted menu data"""
        try:
            validated_items = []
            
            for item in menu_data.get('menu_items', []):
                # Ensure required fields
                if not item.get('name'):
                    continue
                
                validated_item = {
                    'name': str(item['name']).strip(),
                    'description': str(item.get('description', '')).strip() or None,
                    'price': float(item['price']) if item.get('price') is not None else None,
                    'category': str(item.get('category', 'other')).lower().strip(),
                    'allergens': item.get('allergens', []) if isinstance(item.get('allergens'), list) else [],
                    'ingredients': item.get('ingredients', []) if isinstance(item.get('ingredients'), list) else [],
                    'modifiers': item.get('modifiers', []) if isinstance(item.get('modifiers'), list) else [],
                    'combos': item.get('combos', []) if isinstance(item.get('combos'), list) else [],
                    'sizes': item.get('sizes', []) if isinstance(item.get('sizes'), list) else []
                }
                
                validated_items.append(validated_item)
            
            return {
                'restaurant_info': menu_data.get('restaurant_info', {}),
                'menu_items': validated_items
            }
            
        except Exception as e:
            logger.error(f"Error validating menu data: {e}")
            raise