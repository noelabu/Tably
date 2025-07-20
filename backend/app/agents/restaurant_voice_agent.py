#!/usr/bin/env python3
"""
Real-Time Voice Restaurant Ordering Assistant

This script demonstrates real-time voice conversation using Nova Sonic's 
bidirectional streaming API for natural restaurant ordering interactions.
"""

import os
import asyncio
import base64
import json
import uuid
import warnings
import pyaudio
import pytz
import random
import hashlib
import datetime
import time
import inspect
from typing import Dict, List, Optional, Any
from decimal import Decimal
# Load environment variables with explicit path
try:
    from dotenv import load_dotenv
    import pathlib
    
    # Try to find .env file in current directory or parent directories
    current_dir = pathlib.Path(__file__).parent
    env_file = None
    
    # Check current directory and up to 3 parent directories
    for i in range(4):
        potential_env = current_dir / '.env'
        if potential_env.exists():
            env_file = potential_env
            break
        current_dir = current_dir.parent
    
    if env_file:
        load_dotenv(env_file)
        print(f"Loaded .env from: {env_file}")
    else:
        # Try the default
        load_dotenv()
        print("Loaded .env from default location")
    
    # If still no credentials, try to load from known .env location
    if not os.getenv('AWS_ACCESS_KEY_ID'):
        backend_env = pathlib.Path(__file__).parent.parent.parent / '.env'
        if backend_env.exists():
            load_dotenv(backend_env, override=True)
            print(f"Loaded .env from: {backend_env}")
        
except ImportError:
    # If dotenv is not available, try to load from os.environ
    print("dotenv not available, using system environment")
    pass

try:
    from aws_sdk_bedrock_runtime.client import BedrockRuntimeClient, InvokeModelWithBidirectionalStreamOperationInput
    from aws_sdk_bedrock_runtime.models import InvokeModelWithBidirectionalStreamInputChunk, BidirectionalInputPayloadPart
    from aws_sdk_bedrock_runtime.config import Config, HTTPAuthSchemeResolver, SigV4AuthScheme
    from smithy_aws_core.credentials_resolvers.environment import EnvironmentCredentialsResolver
    AWS_SDK_AVAILABLE = True
except ImportError as e:
    print(f"Missing required AWS SDK: {e}")
    print("Install with: pip install aws-sdk-bedrock-runtime")
    AWS_SDK_AVAILABLE = False
    
    # Create mock classes to prevent import errors
    class BedrockRuntimeClient:
        def __init__(self, *args, **kwargs):
            pass
    
    class InvokeModelWithBidirectionalStreamOperationInput:
        def __init__(self, *args, **kwargs):
            pass
    
    class Config:
        def __init__(self, *args, **kwargs):
            pass
    
    class HTTPAuthSchemeResolver:
        pass
    
    class SigV4AuthScheme:
        pass
    
    class EnvironmentCredentialsResolver:
        pass

# Import your existing restaurant logic
try:
    from app.db.menu_items import MenuItemsConnection
    from app.db.orders import OrdersConnection
    from app.models.orders import OrderCreate, OrderItemCreate
    from app.agents.config import session
except ImportError as e:
    print(f"Missing restaurant modules: {e}")
    print("Make sure you're running from the backend directory")
    exit(1)

# Suppress warnings
warnings.filterwarnings("ignore")

# Audio configuration
INPUT_SAMPLE_RATE = 16000
OUTPUT_SAMPLE_RATE = 24000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK_SIZE = 1024

# Debug mode flag
DEBUG = True

def debug_print(message):
    """Print only if debug mode is enabled"""
    if DEBUG:
        functionName = inspect.stack()[1].function
        if functionName == 'time_it' or functionName == 'time_it_async':
            functionName = inspect.stack()[2].function
        print('{:%Y-%m-%d %H:%M:%S.%f}'.format(datetime.datetime.now())[:-3] + ' ' + functionName + ' ' + message)

def time_it(label, methodToRun):
    start_time = time.perf_counter()
    result = methodToRun()
    end_time = time.perf_counter()
    debug_print(f"Execution time for {label}: {end_time - start_time:.4f} seconds")
    return result

async def time_it_async(label, methodToRun):
    start_time = time.perf_counter()
    result = await methodToRun()
    end_time = time.perf_counter()
    debug_print(f"Execution time for {label}: {end_time - start_time:.4f} seconds")
    return result

class RestaurantToolProcessor:
    """Processes restaurant-specific tools for ordering."""
    
    def __init__(self, business_id: str, cart_event_callback=None):
        self.business_id = business_id
        self.menu_db = MenuItemsConnection()
        self.orders_db = OrdersConnection()
        self.current_order: List[Dict] = []
        self.customer_info: Dict[str, Any] = {}
        self.tasks = {}
        self.cart_event_callback = cart_event_callback
    
    async def emit_cart_event(self, action: str, item: Dict = None, cart_items: List[Dict] = None):
        """Emit cart update event to WebSocket if callback is available"""
        if self.cart_event_callback:
            total = sum(item["unit_price"] * item["quantity"] for item in self.current_order)
            cart_event = {
                "type": "cart_updated",
                "action": action,  # add, remove, update, clear
                "item": item,
                "cart_items": cart_items or self.current_order,
                "cart_total": total,
                "item_count": len(self.current_order)
            }
            try:
                await self.cart_event_callback(cart_event)
                debug_print(f"Emitted cart event: {action}")
            except Exception as e:
                debug_print(f"Error emitting cart event: {e}")
    
    async def process_tool_async(self, tool_name, tool_content):
        """Process a tool call asynchronously and return the result"""
        task_id = str(uuid.uuid4())
        task = asyncio.create_task(self._run_tool(tool_name, tool_content))
        self.tasks[task_id] = task
        
        try:
            result = await task
            return result
        finally:
            if task_id in self.tasks:
                del self.tasks[task_id]
    
    async def _run_tool(self, tool_name, tool_content):
        """Internal method to execute the tool logic"""
        debug_print(f"Processing restaurant tool: {tool_name}")
        tool = tool_name.lower()
        
        try:
            content = tool_content.get("content", {})
            if isinstance(content, str):
                content_data = json.loads(content)
            else:
                content_data = content
        except (json.JSONDecodeError, KeyError):
            content_data = {}
        
        if tool == "getmenuitemstool":
            return await self._get_menu_items(content_data)
        elif tool == "searchmenuitemstool":
            return await self._search_menu_items(content_data)
        elif tool == "additemtoordertool":
            return await self._add_item_to_order(content_data)
        elif tool == "removeitemfromordertool":
            return await self._remove_item_from_order(content_data)
        elif tool == "viewcurrentordertool":
            return await self._view_current_order()
        elif tool == "calculateordertotaltool":
            return await self._calculate_order_total()
        elif tool == "confirmordertool":
            return await self._confirm_order(content_data)
        elif tool == "getbusinesshourstool":
            return await self._get_business_hours()
        else:
            return {"error": f"Unsupported tool: {tool_name}"}
    
    async def _get_menu_items(self, params):
        """Get menu items for the restaurant"""
        try:
            category = params.get("category")
            debug_print(f"Getting menu items for business {self.business_id}, category: {category}")
            
            result = await self.menu_db.get_menu_items_by_business(
                business_id=self.business_id,
                page=1,
                page_size=50,
                available_only=True
            )
            
            debug_print(f"Menu DB result: {result}")
            
            if not result or not result.get("items"):
                debug_print("No menu items found in database")
                return {"message": "No menu items available right now"}
            
            items = result["items"]
            
            if category:
                items = [item for item in items if item.get("category", "").lower() == category.lower()]
                if not items:
                    return {"message": f"No items in the {category} category"}
            
            # Format for voice response
            menu_items = []
            for item in items:
                menu_items.append({
                    "name": item["name"],
                    "price": float(item["price"]),
                    "description": item.get("description", ""),
                    "category": item.get("category", "Other")
                })
            
            return {"menu_items": menu_items}
            
        except Exception as e:
            debug_print(f"Exception in _get_menu_items: {e}")
            return {"error": f"Error getting menu items: {str(e)}"}
    
    async def _search_menu_items(self, params):
        """Search for menu items"""
        try:
            search_term = params.get("search_term", "").lower()
            if not search_term:
                return {"error": "Search term is required"}
            
            debug_print(f"Searching for: {search_term}")
            
            try:
                items = await self.menu_db.search_menu_items(
                    business_id=self.business_id,
                    search_term=search_term,
                    available_only=True,
                    limit=10
                )
            except Exception as db_error:
                debug_print(f"Database search failed: {db_error}")
                items = []
            
            
            if not items:
                return {"message": f"No items found matching '{search_term}'"}
            
            found_items = []
            for item in items:
                found_items.append({
                    "name": item["name"],
                    "price": float(item["price"]),
                    "description": item.get("description", ""),
                    "id": item.get("id", "sample")
                })
            
            return {"found_items": found_items}
            
        except Exception as e:
            debug_print(f"Exception in _search_menu_items: {e}")
            return {"error": f"Error searching menu: {str(e)}"}
    
    async def _add_item_to_order(self, params):
        """Add an item to the current order"""
        try:
            item_name = params.get("item_name", "")
            quantity = params.get("quantity", 1)
            special_instructions = params.get("special_instructions")
            
            if not item_name:
                return {"error": "Item name is required"}
            
            # Search for the item
            items = await self.menu_db.search_menu_items(
                business_id=self.business_id,
                search_term=item_name,
                available_only=True,
                limit=5
            )
            
            if not items:
                return {"error": f"Could not find '{item_name}' on the menu"}
            
            # Find exact match or use first result
            selected_item = None
            for item in items:
                if item["name"].lower() == item_name.lower():
                    selected_item = item
                    break
            
            if not selected_item:
                if len(items) == 1:
                    selected_item = items[0]
                else:
                    options = [item["name"] for item in items[:3]]
                    return {
                        "clarification_needed": True,
                        "message": f"Found multiple items: {', '.join(options)}. Which one?",
                        "options": options
                    }
            
            # Add to order
            order_item = {
                "menu_item_id": selected_item["id"],
                "name": selected_item["name"],
                "quantity": quantity,
                "unit_price": float(selected_item["price"]),
                "special_instructions": special_instructions
            }
            
            # Check if item already exists
            existing_index = None
            for i, existing in enumerate(self.current_order):
                if existing["menu_item_id"] == order_item["menu_item_id"]:
                    existing_index = i
                    break
            
            if existing_index is not None:
                self.current_order[existing_index]["quantity"] += quantity
                action = "updated"
            else:
                self.current_order.append(order_item)
                action = "added"
            
            # Emit cart event
            await self.emit_cart_event("add", order_item)
            
            total_price = order_item["unit_price"] * quantity
            
            return {
                "success": True,
                "action": action,
                "item_name": selected_item["name"],
                "quantity": quantity,
                "total_price": total_price,
                "special_instructions": special_instructions
            }
            
        except Exception as e:
            return {"error": f"Error adding item: {str(e)}"}
    
    async def _remove_item_from_order(self, params):
        """Remove an item from the current order"""
        try:
            item_name = params.get("item_name", "")
            quantity = params.get("quantity")
            
            if not self.current_order:
                return {"message": "Order is currently empty"}
            
            # Find item in order
            for i, order_item in enumerate(self.current_order):
                if order_item["name"].lower() == item_name.lower():
                    if quantity is None or quantity >= order_item["quantity"]:
                        removed_quantity = order_item["quantity"]
                        removed_item = order_item.copy()
                        self.current_order.pop(i)
                        # Emit cart event for removal
                        await self.emit_cart_event("remove", removed_item)
                        return {
                            "success": True,
                            "message": f"Removed all {removed_quantity} {order_item['name']} from order"
                        }
                    else:
                        original_quantity = order_item["quantity"]
                        order_item["quantity"] -= quantity
                        # Emit cart event for quantity update
                        await self.emit_cart_event("update", order_item)
                        return {
                            "success": True,
                            "message": f"Removed {quantity} {order_item['name']}. {order_item['quantity']} remaining"
                        }
            
            return {"error": f"'{item_name}' not found in your order"}
            
        except Exception as e:
            return {"error": f"Error removing item: {str(e)}"}
    
    async def _view_current_order(self):
        """View the current order"""
        try:
            if not self.current_order:
                return {"message": "Order is currently empty"}
            
            order_items = []
            total = 0.0
            
            for item in self.current_order:
                item_total = item["unit_price"] * item["quantity"]
                total += item_total
                
                order_items.append({
                    "name": item["name"],
                    "quantity": item["quantity"],
                    "unit_price": item["unit_price"],
                    "total_price": item_total,
                    "special_instructions": item.get("special_instructions")
                })
            
            return {
                "order_items": order_items,
                "total_amount": total,
                "item_count": len(self.current_order)
            }
            
        except Exception as e:
            return {"error": f"Error viewing order: {str(e)}"}
    
    async def _calculate_order_total(self):
        """Calculate order total"""
        try:
            if not self.current_order:
                return {"total": 0.0, "message": "Order is empty"}
            
            total = sum(item["unit_price"] * item["quantity"] for item in self.current_order)
            item_count = sum(item["quantity"] for item in self.current_order)
            
            return {
                "total": total,
                "item_count": item_count
            }
            
        except Exception as e:
            return {"error": f"Error calculating total: {str(e)}"}
    
    async def _confirm_order(self, params):
        """Confirm and place the order"""
        try:
            customer_name = params.get("customer_name", "")
            customer_phone = params.get("customer_phone")
            special_requests = params.get("special_requests")
            
            if not self.current_order:
                return {"error": "Cannot confirm empty order"}
            
            if not customer_name.strip():
                return {"error": "Customer name is required"}
            
            # Create order items
            order_items = []
            for item in self.current_order:
                order_items.append(OrderItemCreate(
                    menu_item_id=item["menu_item_id"],
                    quantity=item["quantity"],
                    unit_price=Decimal(str(item["unit_price"])),
                    special_instructions=item.get("special_instructions")
                ))
            
            total_amount = sum(item.unit_price * item.quantity for item in order_items)
            
            # Create order
            order_data = OrderCreate(
                business_id=self.business_id,
                customer_name=customer_name,
                customer_phone=customer_phone,
                total_amount=total_amount,
                special_requests=special_requests,
                items=order_items
            )
            
            # Save to database
            created_order = await self.orders_db.create_order_with_items(order_data.dict())
            
            if created_order:
                order_id = created_order.get("id", "Unknown")
                # Clear current order
                self.current_order = []
                self.customer_info = {}
                
                # Emit cart clear event
                await self.emit_cart_event("clear", cart_items=[])
                
                return {
                    "success": True,
                    "order_id": order_id,
                    "customer_name": customer_name,
                    "total_amount": float(total_amount)
                }
            else:
                return {"error": "Failed to place order"}
                
        except Exception as e:
            return {"error": f"Error confirming order: {str(e)}"}
    
    async def _get_business_hours(self):
        """Get business hours"""
        return {
            "hours": "Monday through Friday from 11 AM to 9 PM, Saturday through Sunday from 10 AM to 10 PM"
        }

class RestaurantStreamManager:
    """Manages bidirectional streaming with AWS Bedrock for restaurant ordering"""
    
    # Event templates (same as original but with restaurant tools)
    START_SESSION_EVENT = '''{
        "event": {
            "sessionStart": {
            "inferenceConfiguration": {
                "maxTokens": 1024,
                "topP": 0.9,
                "temperature": 0.7
                }
            }
        }
    }'''

    CONTENT_START_EVENT = '''{
        "event": {
            "contentStart": {
                "promptName": "%s",
                "contentName": "%s",
                "type": "AUDIO",
                "interactive": true,
                "role": "USER",
                "audioInputConfiguration": {
                    "mediaType": "audio/lpcm",
                    "sampleRateHertz": 16000,
                    "sampleSizeBits": 16,
                    "channelCount": 1,
                    "audioType": "SPEECH",
                    "encoding": "base64"
                }
            }
        }
    }'''

    AUDIO_EVENT_TEMPLATE = '''{
        "event": {
            "audioInput": {
            "promptName": "%s",
            "contentName": "%s",
            "content": "%s"
            }
        }
    }'''

    TEXT_CONTENT_START_EVENT = '''{
        "event": {
            "contentStart": {
            "promptName": "%s",
            "contentName": "%s",
            "type": "TEXT",
            "role": "%s",
            "interactive": true,
                "textInputConfiguration": {
                    "mediaType": "text/plain"
                }
            }
        }
    }'''

    TEXT_INPUT_EVENT = '''{
        "event": {
            "textInput": {
            "promptName": "%s",
            "contentName": "%s",
            "content": "%s"
            }
        }
    }'''

    TOOL_CONTENT_START_EVENT = '''{
        "event": {
            "contentStart": {
                "promptName": "%s",
                "contentName": "%s",
                "interactive": false,
                "type": "TOOL",
                "role": "TOOL",
                "toolResultInputConfiguration": {
                    "toolUseId": "%s",
                    "type": "TEXT",
                    "textInputConfiguration": {
                        "mediaType": "text/plain"
                    }
                }
            }
        }
    }'''

    CONTENT_END_EVENT = '''{
        "event": {
            "contentEnd": {
            "promptName": "%s",
            "contentName": "%s"
            }
        }
    }'''

    PROMPT_END_EVENT = '''{
        "event": {
            "promptEnd": {
            "promptName": "%s"
            }
        }
    }'''

    SESSION_END_EVENT = '''{
        "event": {
            "sessionEnd": {}
        }
    }'''
    
    def __init__(self, business_id: str, model_id='amazon.nova-sonic-v1:0', region='us-east-1'):
        """Initialize the stream manager."""
        self.business_id = business_id
        self.model_id = model_id
        self.region = region
        
        # Replace RxPy subjects with asyncio queues
        self.audio_input_queue = asyncio.Queue()
        self.audio_output_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()
        
        self.response_task = None
        self.stream_response = None
        self.is_active = False
        self.barge_in = False
        self.bedrock_client = None
        
        # Audio playback components
        self.audio_player = None
        
        # Text response components
        self.display_assistant_text = False
        self.role = None

        # Session information
        self.prompt_name = str(uuid.uuid4())
        self.content_name = str(uuid.uuid4())
        self.audio_content_name = str(uuid.uuid4())
        self.toolUseContent = ""
        self.toolUseId = ""
        self.toolName = ""

        # Add restaurant tool processor with cart event callback
        self.tool_processor = RestaurantToolProcessor(business_id, self.emit_cart_event)
        
        # Add tracking for in-progress tool calls
        self.pending_tool_tasks = {}
        
        # Conversation management
        self.last_interaction_time = None
        self.idle_timeout = 30  # 30 seconds of silence before prompting

    async def emit_cart_event(self, cart_data):
        """Emit cart event to WebSocket output queue"""
        try:
            await self.output_queue.put(cart_data)
            debug_print(f"Cart event emitted: {cart_data.get('action', 'unknown')}")
        except Exception as e:
            debug_print(f"Error emitting cart event: {e}")

    def _initialize_client(self):
        """Initialize the Bedrock client."""
        debug_print("Checking AWS SDK availability")
        # Check if AWS SDK is available
        if not AWS_SDK_AVAILABLE:
            debug_print("AWS SDK not available")
            raise ValueError("AWS SDK for Bedrock Runtime is not installed. Install with: pip install aws-sdk-bedrock-runtime")
        
        debug_print("AWS SDK available, checking credentials")
        # Check if AWS credentials are available
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        debug_print(f"AWS_ACCESS_KEY_ID: {'***' if aws_access_key else 'NOT SET'}")
        debug_print(f"AWS_SECRET_ACCESS_KEY: {'***' if aws_secret_key else 'NOT SET'}")
        
        if not aws_access_key or not aws_secret_key:
            debug_print("Missing AWS credentials")
            raise ValueError("AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are required")
        
        debug_print(f"Creating Bedrock client config for region: {self.region}")
        config = Config(
            endpoint_uri=f"https://bedrock-runtime.{self.region}.amazonaws.com",
            region=self.region,
            aws_credentials_identity_resolver=EnvironmentCredentialsResolver(),
            http_auth_scheme_resolver=HTTPAuthSchemeResolver(),
            http_auth_schemes={"aws.auth#sigv4": SigV4AuthScheme()}
        )
        debug_print("Creating BedrockRuntimeClient")
        self.bedrock_client = BedrockRuntimeClient(config=config)
        debug_print("Bedrock client created successfully")
    
    def start_prompt(self):
        """Create a promptStart event with restaurant tools"""
        
        # Restaurant tool schemas
        menu_schema = json.dumps({
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Optional category to filter by (appetizers, mains, desserts, etc.)"
                }
            }
        })

        search_schema = json.dumps({
            "type": "object",
            "properties": {
                "search_term": {
                    "type": "string",
                    "description": "The term to search for in menu items"
                }
            },
            "required": ["search_term"]
        })

        add_item_schema = json.dumps({
            "type": "object",
            "properties": {
                "item_name": {
                    "type": "string",
                    "description": "Name of the menu item to add"
                },
                "quantity": {
                    "type": "integer",
                    "description": "Quantity of the item",
                    "default": 1
                },
                "special_instructions": {
                    "type": "string",
                    "description": "Any special instructions for the item"
                }
            },
            "required": ["item_name"]
        })

        remove_item_schema = json.dumps({
            "type": "object",
            "properties": {
                "item_name": {
                    "type": "string",
                    "description": "Name of the menu item to remove"
                },
                "quantity": {
                    "type": "integer",
                    "description": "Quantity to remove (if not specified, removes all)"
                }
            },
            "required": ["item_name"]
        })

        confirm_order_schema = json.dumps({
            "type": "object",
            "properties": {
                "customer_name": {
                    "type": "string",
                    "description": "Customer's name for the order"
                },
                "customer_phone": {
                    "type": "string",
                    "description": "Customer's phone number"
                },
                "special_requests": {
                    "type": "string",
                    "description": "Any special requests for the entire order"
                }
            },
            "required": ["customer_name"]
        })

        prompt_start_event = {
            "event": {
                "promptStart": {
                    "promptName": self.prompt_name,
                    "textOutputConfiguration": {
                        "mediaType": "text/plain"
                    },
                    "audioOutputConfiguration": {
                        "mediaType": "audio/lpcm",
                        "sampleRateHertz": 24000,
                        "sampleSizeBits": 16,
                        "channelCount": 1,
                        "voiceId": "matthew",
                        "encoding": "base64",
                        "audioType": "SPEECH"
                    },
                    "toolUseOutputConfiguration": {
                        "mediaType": "application/json"
                    },
                    "toolConfiguration": {
                        "tools": [
                            {
                                "toolSpec": {
                                    "name": "getMenuItemsTool",
                                    "description": "Get menu items for the restaurant, optionally filtered by category",
                                    "inputSchema": {"json": menu_schema}
                                }
                            },
                            {
                                "toolSpec": {
                                    "name": "searchMenuItemsTool",
                                    "description": "Search for menu items by name or description",
                                    "inputSchema": {"json": search_schema}
                                }
                            },
                            {
                                "toolSpec": {
                                    "name": "addItemToOrderTool",
                                    "description": "Add an item to the current order",
                                    "inputSchema": {"json": add_item_schema}
                                }
                            },
                            {
                                "toolSpec": {
                                    "name": "removeItemFromOrderTool",
                                    "description": "Remove an item from the current order",
                                    "inputSchema": {"json": remove_item_schema}
                                }
                            },
                            {
                                "toolSpec": {
                                    "name": "viewCurrentOrderTool",
                                    "description": "View the current order with items and total cost",
                                    "inputSchema": {"json": json.dumps({"type": "object", "properties": {}})}
                                }
                            },
                            {
                                "toolSpec": {
                                    "name": "calculateOrderTotalTool",
                                    "description": "Calculate the total cost of the current order",
                                    "inputSchema": {"json": json.dumps({"type": "object", "properties": {}})}
                                }
                            },
                            {
                                "toolSpec": {
                                    "name": "confirmOrderTool",
                                    "description": "Confirm and place the order",
                                    "inputSchema": {"json": confirm_order_schema}
                                }
                            },
                            {
                                "toolSpec": {
                                    "name": "getBusinessHoursTool",
                                    "description": "Get the business hours for the restaurant",
                                    "inputSchema": {"json": json.dumps({"type": "object", "properties": {}})}
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        return json.dumps(prompt_start_event)
    
    def tool_result_event(self, content_name, content, role):
        """Create a tool result event"""
        if isinstance(content, dict):
            content_json_string = json.dumps(content)
        else:
            content_json_string = content
            
        tool_result_event = {
            "event": {
                "toolResult": {
                    "promptName": self.prompt_name,
                    "contentName": content_name,
                    "content": content_json_string
                }
            }
        }
        return json.dumps(tool_result_event)
    
    # [Include all the other methods from the original BedrockStreamManager here...]
    # For brevity, I'll include the key methods. The rest are identical to the original.
    
    async def initialize_stream(self):
        """Initialize the bidirectional stream with Bedrock."""
        debug_print("Starting stream initialization")
        if not self.bedrock_client:
            debug_print("Initializing Bedrock client")
            self._initialize_client()
        
        try:
            debug_print("Calling Bedrock invoke_model_with_bidirectional_stream")
            self.stream_response = await time_it_async("invoke_model_with_bidirectional_stream", lambda: self.bedrock_client.invoke_model_with_bidirectional_stream(InvokeModelWithBidirectionalStreamOperationInput(model_id=self.model_id)))
            self.is_active = True
            debug_print("Stream response created, setting is_active = True")
            
            # Restaurant-specific system prompt - Simplified for better responsiveness
            restaurant_system_prompt = """You are a friendly voice ordering assistant for a restaurant. 

            CRITICAL MENU GUARDRAILS - STRICTLY FOLLOW THESE RULES:
            1. NEVER recommend any item without first checking if it exists using getMenuItemsTool or searchMenuItemsTool
            2. ONLY suggest items that you have confirmed are available in the current menu
            3. If a customer asks for something not on the menu, say "I'm sorry, we don't have [item] on our menu today. Let me show you what we do have..." then use getMenuItemsTool
            4. Before making ANY recommendation, you MUST first search the menu to verify the item exists
            5. If unsure about any item, always check the menu first rather than guessing

            CONVERSATION FLOW:
            - Greet: "Hi! Welcome to our restaurant. How can I help you today?"
            - When customers ask for items: First search menu, then recommend only confirmed items
            - Keep responses SHORT and conversational
            - Always verify menu availability before suggestions

            ABSOLUTE RULE: Zero tolerance for recommending non-menu items. Always check first."""
            
            # Send initialization events
            prompt_event = self.start_prompt()
            text_content_start = self.TEXT_CONTENT_START_EVENT % (self.prompt_name, self.content_name, "SYSTEM")
            # Properly escape the content for JSON
            escaped_prompt = restaurant_system_prompt.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            text_content = self.TEXT_INPUT_EVENT % (self.prompt_name, self.content_name, escaped_prompt)
            text_content_end = self.CONTENT_END_EVENT % (self.prompt_name, self.content_name)
            
            init_events = [self.START_SESSION_EVENT, prompt_event, text_content_start, text_content, text_content_end]
            
            for event in init_events:
                await self.send_raw_event(event)
                await asyncio.sleep(0.1)
            
            # Start listening for responses
            self.response_task = asyncio.create_task(self._process_responses())
            
            # Start processing audio input
            asyncio.create_task(self._process_audio_input())
            
            await asyncio.sleep(0.1)
            debug_print("Restaurant stream initialized successfully")
            return self
        except Exception as e:
            self.is_active = False
            print(f"Failed to initialize stream: {str(e)}")
            raise
    
    async def send_raw_event(self, event_json):
        """Send a raw event JSON to the Bedrock stream."""
        if not self.stream_response or not self.is_active:
            debug_print("Stream not initialized or closed")
            return
       
        # Validate the JSON before sending
        try:
            parsed_event = json.loads(event_json)
            debug_print(f"Sending valid JSON event: {list(parsed_event.get('event', {}).keys())}")
        except json.JSONDecodeError as e:
            debug_print(f"Invalid JSON being sent: {e}")
            debug_print(f"Invalid JSON content: {event_json[:500]}...")
            return
        
        event = InvokeModelWithBidirectionalStreamInputChunk(
            value=BidirectionalInputPayloadPart(bytes_=event_json.encode('utf-8'))
        )
        
        try:
            await self.stream_response.input_stream.send(event)
            debug_print(f"Successfully sent event")
        except Exception as e:
            debug_print(f"Error sending event: {str(e)}")
            debug_print(f"Exception type: {type(e)}")
            
            # Handle specific AWS stream errors
            if "No open content found" in str(e) or "content name" in str(e).lower():
                debug_print("AWS stream content already ended - marking stream inactive")
                self.is_active = False
                return
            
            if "parse" in str(e).lower():
                debug_print(f"Parse error on event: {event_json[:200]}...")
            
            if DEBUG:
                import traceback
                traceback.print_exc()
    
    async def send_audio_content_start_event(self):
        """Send a content start event to the Bedrock stream."""
        content_start_event = self.CONTENT_START_EVENT % (self.prompt_name, self.audio_content_name)
        await self.send_raw_event(content_start_event)
    
    async def _process_audio_input(self):
        """Process audio input from the queue and send to Bedrock."""
        audio_content_active = False
        last_audio_time = None
        
        while self.is_active:
            try:
                data = await self.audio_input_queue.get()
                
                audio_bytes = data.get('audio_bytes')
                if not audio_bytes:
                    debug_print("No audio bytes received")
                    continue
                
                # Ensure audio is in the correct format (16-bit PCM)
                if len(audio_bytes) == 0:
                    debug_print("Empty audio bytes")
                    continue
                
                # Validate audio data
                if len(audio_bytes) % 2 != 0:
                    debug_print(f"Invalid audio data length: {len(audio_bytes)} (not multiple of 2)")
                    continue
                
                debug_print(f"Processing audio chunk: {len(audio_bytes)} bytes")
                
                # Start audio content if not already started
                if not audio_content_active:
                    debug_print("Starting audio content")
                    await self.send_audio_content_start_event()
                    audio_content_active = True
                
                blob = base64.b64encode(audio_bytes)
                audio_event = self.AUDIO_EVENT_TEMPLATE % (
                    self.prompt_name, 
                    self.audio_content_name, 
                    blob.decode('utf-8')
                )
                
                debug_print(f"Sending audio event with {len(blob)} encoded bytes")
                await self.send_raw_event(audio_event)
                
                # Update last audio time
                import time
                last_audio_time = time.time()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                debug_print(f"Error processing audio: {e}")
                if DEBUG:
                    import traceback
                    traceback.print_exc()
    
    
    def add_audio_chunk(self, audio_bytes):
        """Add an audio chunk to the queue."""
        self.audio_input_queue.put_nowait({
            'audio_bytes': audio_bytes,
            'prompt_name': self.prompt_name,
            'content_name': self.audio_content_name
        })
    
    async def send_audio_content_end_event(self):
        """Send a content end event to the Bedrock stream."""
        if not self.is_active:
            debug_print("Stream is not active")
            return
        
        content_end_event = self.CONTENT_END_EVENT % (self.prompt_name, self.audio_content_name)
        await self.send_raw_event(content_end_event)
        debug_print("Audio ended")
    
    async def send_tool_start_event(self, content_name, tool_use_id):
        """Send a tool content start event to the Bedrock stream."""
        content_start_event = self.TOOL_CONTENT_START_EVENT % (self.prompt_name, content_name, tool_use_id)
        debug_print(f"Sending tool start event: {content_start_event}")  
        await self.send_raw_event(content_start_event)

    async def send_tool_result_event(self, content_name, tool_result):
        """Send a tool content event to the Bedrock stream."""
        tool_result_event = self.tool_result_event(content_name=content_name, content=tool_result, role="TOOL")
        debug_print(f"Sending tool result event: {tool_result_event}")
        await self.send_raw_event(tool_result_event)
    
    async def send_tool_content_end_event(self, content_name):
        """Send a tool content end event to the Bedrock stream."""
        tool_content_end_event = self.CONTENT_END_EVENT % (self.prompt_name, content_name)
        debug_print(f"Sending tool content event: {tool_content_end_event}")
        await self.send_raw_event(tool_content_end_event)
    
    async def send_prompt_end_event(self):
        """Close the stream and clean up resources."""
        if not self.is_active:
            debug_print("Stream is not active")
            return
        
        prompt_end_event = self.PROMPT_END_EVENT % (self.prompt_name)
        await self.send_raw_event(prompt_end_event)
        debug_print("Prompt ended")
        
    async def send_session_end_event(self):
        """Send a session end event to the Bedrock stream."""
        if not self.is_active:
            debug_print("Stream is not active")
            return

        await self.send_raw_event(self.SESSION_END_EVENT)
        self.is_active = False
        debug_print("Session ended")
    
    async def _handle_json_event(self, json_data):
        """Handle a single JSON event from the stream."""
        try:
            if 'event' in json_data:
                if 'completionStart' in json_data['event']:
                    debug_print(f"completionStart: {json_data['event']}")
                elif 'contentStart' in json_data['event']:
                    debug_print("Content start detected")
                    content_start = json_data['event']['contentStart']
                    self.role = content_start['role']
                    if 'additionalModelFields' in content_start:
                        try:
                            additional_fields = json.loads(content_start['additionalModelFields'])
                            if additional_fields.get('generationStage') == 'SPECULATIVE':
                                debug_print("Speculative content detected")
                                self.display_assistant_text = True
                            else:
                                self.display_assistant_text = False
                        except json.JSONDecodeError:
                            debug_print("Error parsing additionalModelFields")
                elif 'textOutput' in json_data['event']:
                    text_content = json_data['event']['textOutput']['content']
                    role = json_data['event']['textOutput']['role']
                    if '{ "interrupted" : true }' in text_content:
                        debug_print("Barge-in detected. Stopping audio output.")
                        self.barge_in = True

                    if (self.role == "ASSISTANT" and self.display_assistant_text):
                        print(f"Assistant: {text_content}")
                        # Also send text response to output queue for WebSocket forwarding
                        await self.output_queue.put({
                            "type": "text_output",
                            "content": text_content,
                            "role": "assistant"
                        })
                    elif (self.role == "USER"):
                        print(f"User: {text_content}")
                        self.last_interaction_time = time.time()
                elif 'audioOutput' in json_data['event']:
                    audio_content = json_data['event']['audioOutput']['content']
                    audio_bytes = base64.b64decode(audio_content)
                    await self.audio_output_queue.put(audio_bytes)
                elif 'toolUse' in json_data['event']:
                    self.toolUseContent = json_data['event']['toolUse']
                    self.toolName = json_data['event']['toolUse']['toolName']
                    self.toolUseId = json_data['event']['toolUse']['toolUseId']
                    debug_print(f"Tool use detected: {self.toolName}, ID: {self.toolUseId}")
                elif 'contentEnd' in json_data['event'] and json_data['event'].get('contentEnd', {}).get('type') == 'TOOL':
                    debug_print("Processing tool use and sending result")
                    self.handle_tool_request(self.toolName, self.toolUseContent, self.toolUseId)
                    debug_print("Processing tool use asynchronously")
                elif 'contentEnd' in json_data['event']:
                    debug_print("Content end")
                elif 'completionEnd' in json_data['event']:
                    debug_print("End of response sequence")
                elif 'usageEvent' in json_data['event']:
                    debug_print(f"UsageEvent: {json_data['event']}")
            
            await self.output_queue.put(json_data)
        except Exception as e:
            debug_print(f"Error handling JSON event: {e}")
            debug_print(f"Problematic JSON: {json.dumps(json_data, indent=2)}")

    async def _process_responses(self):
        """Process incoming responses from Bedrock."""
        try:            
            while self.is_active:
                try:
                    debug_print("Waiting for stream output...")
                    output = await self.stream_response.await_output()
                    debug_print("Got stream output, receiving result...")
                    result = await output[1].receive()
                    debug_print(f"Received result: {type(result)}")
                    if result.value and result.value.bytes_:
                        try:
                            response_data = result.value.bytes_.decode('utf-8')
                            debug_print(f"Raw response data: {response_data[:200]}...")
                            
                            # Handle potential multiple JSON objects in one chunk
                            if response_data.strip():
                                # Split by newlines and try to parse each line separately
                                lines = response_data.strip().split('\n')
                                for line in lines:
                                    line = line.strip()
                                    if line:
                                        try:
                                            json_data = json.loads(line)
                                            await self._handle_json_event(json_data)
                                        except json.JSONDecodeError as e:
                                            debug_print(f"Failed to parse JSON line: {line[:100]}... Error: {e}")
                                            continue
                        except json.JSONDecodeError as e:
                            debug_print(f"Failed to parse entire response as JSON: {e}")
                            debug_print(f"Raw response: {response_data[:500]}...")
                            await self.output_queue.put({"error": "json_decode_error", "raw_data": response_data[:1000]})
                except StopAsyncIteration:
                    break
                except Exception as e:
                    error_str = str(e)
                    if "ValidationException" in error_str:
                        print(f"Validation error: {error_str}")
                        debug_print(f"Validation exception details: {e}")
                    elif "Unable to parse input chunk" in error_str:
                        print(f"Parse input chunk error: {error_str}")
                        debug_print(f"Parse error details: {e}")
                        debug_print(f"Exception type: {type(e)}")
                        # This error might come from the AWS SDK itself
                        if hasattr(e, '__cause__'):
                            debug_print(f"Caused by: {e.__cause__}")
                        if hasattr(e, '__context__'):
                            debug_print(f"Context: {e.__context__}")
                    else:
                        print(f"Error receiving response: {e}")
                        debug_print(f"Exception type: {type(e)}")
                        debug_print(f"Exception details: {e}")
                    
                    # Only break on critical errors, continue on recoverable ones
                    if "Connection" in error_str or "Stream" in error_str or "closed" in error_str.lower():
                        debug_print("Critical stream error, terminating response processing")
                        break
                    else:
                        debug_print("Non-critical error, continuing response processing")
                        continue
                    
        except Exception as e:
            print(f"Response processing error: {e}")
        finally:
            self.is_active = False

    def handle_tool_request(self, tool_name, tool_content, tool_use_id):
        """Handle a tool request asynchronously"""
        tool_content_name = str(uuid.uuid4())
        task = asyncio.create_task(self._execute_tool_and_send_result(
            tool_name, tool_content, tool_use_id, tool_content_name))
        self.pending_tool_tasks[tool_content_name] = task
        task.add_done_callback(
            lambda t: self._handle_tool_task_completion(t, tool_content_name))
    
    def _handle_tool_task_completion(self, task, content_name):
        """Handle the completion of a tool task"""
        if content_name in self.pending_tool_tasks:
            del self.pending_tool_tasks[content_name]
        
        if task.done() and not task.cancelled():
            exception = task.exception()
            if exception:
                debug_print(f"Tool task failed: {str(exception)}")
    
    async def _execute_tool_and_send_result(self, tool_name, tool_content, tool_use_id, content_name):
        """Execute a tool and send the result"""
        try:
            debug_print(f"Starting tool execution: {tool_name}")
            
            tool_result = await self.tool_processor.process_tool_async(tool_name, tool_content)
            
            await self.send_tool_start_event(content_name, tool_use_id)
            await self.send_tool_result_event(content_name, tool_result)
            await self.send_tool_content_end_event(content_name)
            
            debug_print(f"Tool execution complete: {tool_name}")
        except Exception as e:
            debug_print(f"Error executing tool {tool_name}: {str(e)}")
            try:
                error_result = {"error": f"Tool execution failed: {str(e)}"}
                await self.send_tool_start_event(content_name, tool_use_id)
                await self.send_tool_result_event(content_name, error_result)
                await self.send_tool_content_end_event(content_name)
            except Exception as send_error:
                debug_print(f"Failed to send error response: {str(send_error)}")
    
    async def close(self):
        """Close the stream properly."""
        if not self.is_active:
            return
        
        for task in self.pending_tool_tasks.values():
            task.cancel()

        if self.response_task and not self.response_task.done():
            self.response_task.cancel()

        try:
            await self.send_audio_content_end_event()
            await self.send_prompt_end_event()
            await self.send_session_end_event()
        except Exception as e:
            debug_print(f"Error during stream end events: {e}")
            self.is_active = False

        if self.stream_response:
            try:
                await self.stream_response.input_stream.close()
            except Exception as e:
                debug_print(f"Error closing stream input: {e}")

class AudioStreamer:
    """Handles continuous microphone input and audio output using separate streams."""
    
    def __init__(self, stream_manager):
        self.stream_manager = stream_manager
        self.is_streaming = False
        self.loop = asyncio.get_event_loop()

        debug_print("AudioStreamer Initializing PyAudio...")
        self.p = time_it("AudioStreamerInitPyAudio", pyaudio.PyAudio)
        debug_print("AudioStreamer PyAudio initialized")

        debug_print("Opening input audio stream...")
        self.input_stream = time_it("AudioStreamerOpenAudio", lambda: self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=INPUT_SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
            stream_callback=self.input_callback
        ))
        debug_print("input audio stream opened")

        debug_print("Opening output audio stream...")
        self.output_stream = time_it("AudioStreamerOpenAudio", lambda: self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=OUTPUT_SAMPLE_RATE,
            output=True,
            frames_per_buffer=CHUNK_SIZE
        ))
        debug_print("output audio stream opened")

    def input_callback(self, in_data, frame_count, time_info, status):
        """Callback function that schedules audio processing in the asyncio event loop"""
        if self.is_streaming and in_data:
            # Convert float32 audio data to int16 (16-bit PCM) as expected by Nova Sonic
            try:
                # PyAudio gives us bytes already in int16 format, so we can use directly
                asyncio.run_coroutine_threadsafe(
                    self.process_input_audio(in_data), 
                    self.loop
                )
            except Exception as e:
                if DEBUG:
                    debug_print(f"Error in input callback: {e}")
        return (None, pyaudio.paContinue)

    async def process_input_audio(self, audio_data):
        """Process a single audio chunk directly"""
        try:
            # Ensure we have valid audio data
            if audio_data and len(audio_data) > 0:
                self.stream_manager.add_audio_chunk(audio_data)
        except Exception as e:
            if self.is_streaming:
                print(f"Error processing input audio: {e}")
    
    async def play_output_audio(self):
        """Play audio responses from Nova Sonic"""
        while self.is_streaming:
            try:
                if self.stream_manager.barge_in:
                    while not self.stream_manager.audio_output_queue.empty():
                        try:
                            self.stream_manager.audio_output_queue.get_nowait()
                        except asyncio.QueueEmpty:
                            break
                    self.stream_manager.barge_in = False
                    await asyncio.sleep(0.05)
                    continue
                
                audio_data = await asyncio.wait_for(
                    self.stream_manager.audio_output_queue.get(),
                    timeout=0.1
                )
                
                if audio_data and self.is_streaming:
                    chunk_size = CHUNK_SIZE
                    
                    for i in range(0, len(audio_data), chunk_size):
                        if not self.is_streaming:
                            break
                        
                        end = min(i + chunk_size, len(audio_data))
                        chunk = audio_data[i:end]
                        
                        def write_chunk(data):
                            return self.output_stream.write(data)
                        
                        await asyncio.get_event_loop().run_in_executor(None, write_chunk, chunk)
                        await asyncio.sleep(0.001)
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                if self.is_streaming:
                    print(f"Error playing output audio: {str(e)}")
                await asyncio.sleep(0.05)
    
    async def start_streaming(self):
        """Start streaming audio."""
        if self.is_streaming:
            return
        
        print("🎤 Real-time voice ordering started!")
        print("🗣️  Speak naturally to place your order...")
        print("⏎  Press Enter to stop...")
        
        await time_it_async("send_audio_content_start_event", lambda: self.stream_manager.send_audio_content_start_event())
        
        self.is_streaming = True
        
        if not self.input_stream.is_active():
            self.input_stream.start_stream()
        
        self.output_task = asyncio.create_task(self.play_output_audio())
        
        await asyncio.get_event_loop().run_in_executor(None, input)
        
        await self.stop_streaming()
    
    async def stop_streaming(self):
        """Stop streaming audio."""
        if not self.is_streaming:
            return
            
        self.is_streaming = False

        tasks = []
        if hasattr(self, 'input_task') and not self.input_task.done():
            tasks.append(self.input_task)
        if hasattr(self, 'output_task') and not self.output_task.done():
            tasks.append(self.output_task)
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        if self.input_stream:
            if self.input_stream.is_active():
                self.input_stream.stop_stream()
            self.input_stream.close()
        if self.output_stream:
            if self.output_stream.is_active():
                self.output_stream.stop_stream()
            self.output_stream.close()
        if self.p:
            self.p.terminate()
        
        await self.stream_manager.close()

async def main(business_id: str, debug=False):
    """Main function to run the restaurant voice ordering application."""
    global DEBUG
    DEBUG = debug

    print("🎙️  Real-Time Restaurant Voice Ordering Assistant")
    print("=" * 60)
    print(f"Business ID: {business_id}")
    print("🎤 Speak naturally to place your order!")
    print("🔇 Press Enter to end conversation")
    print("=" * 60)

    # Create stream manager
    stream_manager = RestaurantStreamManager(business_id=business_id, model_id='amazon.nova-sonic-v1:0', region='us-east-1')

    # Create audio streamer
    audio_streamer = AudioStreamer(stream_manager)

    # Initialize the stream
    await time_it_async("initialize_stream", stream_manager.initialize_stream)

    try:
        # This will run until the user presses Enter
        await audio_streamer.start_streaming()
        
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        # Clean up
        await audio_streamer.stop_streaming()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Restaurant Voice Ordering with Nova Sonic')
    parser.add_argument('business_id', nargs='?', default='5eff8f12-7d43-4b0d-b3f7-e762a7903a82', help='Business ID for the restaurant')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    # Set AWS credentials from your config
    try:
        credentials = session.get_credentials()
        os.environ['AWS_ACCESS_KEY_ID'] = credentials.access_key
        os.environ['AWS_SECRET_ACCESS_KEY'] = credentials.secret_key
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    except Exception as e:
        print(f"Error setting AWS credentials: {e}")
        print("Make sure your AWS credentials are configured properly")
        exit(1)

    # Run the main function
    try:
        asyncio.run(main(args.business_id, debug=args.debug))
    except Exception as e:
        print(f"Application error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()