import logging
from typing import Dict, List, Optional, Any
from decimal import Decimal

from strands.core import Agent
from strands.tools.base import tool
from pydantic import BaseModel

from app.agents.config import nova_sonic_model
from app.db.menu_items import MenuItemsConnection
from app.db.orders import OrdersConnection
from app.models.orders import OrderCreate, OrderItemCreate

logger = logging.getLogger(__name__)

class MenuItem(BaseModel):
    id: str
    name: str
    description: Optional[str]
    price: Decimal
    category: Optional[str]
    available: bool

class OrderItem(BaseModel):
    menu_item_id: str
    quantity: int
    special_instructions: Optional[str] = None

class Order(BaseModel):
    items: List[OrderItem]
    customer_name: str
    customer_phone: Optional[str] = None
    special_requests: Optional[str] = None

class VoiceOrderingAgent:
    def __init__(self, business_id: str):
        self.business_id = business_id
        self.menu_db = MenuItemsConnection()
        self.orders_db = OrdersConnection()
        self.current_order: List[OrderItem] = []
        self.customer_info: Dict[str, Any] = {}
        
        # Initialize the Strands agent with Nova Sonic model
        self.agent = Agent(
            name="Voice Ordering Assistant",
            model=nova_sonic_model,
            instructions=self._get_system_prompt(),
            tools=[
                self.get_menu_items,
                self.search_menu_items,
                self.add_item_to_order,
                self.remove_item_from_order,
                self.view_current_order,
                self.calculate_order_total,
                self.confirm_order,
                self.get_business_hours
            ]
        )

    def _get_system_prompt(self) -> str:
        return """You are a friendly, efficient voice ordering assistant for a restaurant. Your goal is to help customers place orders through natural conversation.

Key responsibilities:
1. Greet customers warmly and ask how you can help
2. Present menu items clearly when asked
3. Help customers add items to their order
4. Handle modifications and special requests
5. Confirm order details before finalizing
6. Collect customer information (name, phone)
7. Be conversational and helpful

Guidelines:
- Speak naturally and conversationally
- Ask clarifying questions when items are ambiguous
- Suggest popular items or categories when customers seem unsure
- Always confirm quantities and special instructions
- Be patient with changes to the order
- Provide clear pricing information
- Keep responses concise but friendly

When the customer seems ready to order, guide them through the process step by step."""

    @tool
    async def get_menu_items(self, category: Optional[str] = None) -> str:
        """Get menu items for the restaurant, optionally filtered by category.
        
        Args:
            category: Optional category to filter by (e.g., 'appetizers', 'mains', 'desserts')
        """
        try:
            result = await self.menu_db.get_menu_items_by_business(
                business_id=self.business_id,
                page=1,
                page_size=50,
                available_only=True
            )
            
            if not result or not result["items"]:
                return "I'm sorry, but we don't have any menu items available right now."
            
            items = result["items"]
            
            # Filter by category if provided
            if category:
                items = [item for item in items if item.get("category", "").lower() == category.lower()]
                if not items:
                    return f"I don't see any items in the {category} category right now."
            
            # Format menu items for voice presentation
            menu_text = "Here are our available items:\n\n"
            current_category = None
            
            for item in items:
                item_category = item.get("category", "Other")
                if item_category != current_category:
                    current_category = item_category
                    menu_text += f"\n**{item_category}:**\n"
                
                price = f"${float(item['price']):.2f}"
                menu_text += f"- {item['name']} - {price}"
                if item.get("description"):
                    menu_text += f" - {item['description']}"
                menu_text += "\n"
            
            return menu_text
            
        except Exception as e:
            logger.error(f"Error getting menu items: {str(e)}")
            return "I'm having trouble accessing our menu right now. Please try again in a moment."

    @tool
    async def search_menu_items(self, search_term: str) -> str:
        """Search for menu items by name or description.
        
        Args:
            search_term: The term to search for in menu item names and descriptions
        """
        try:
            items = await self.menu_db.search_menu_items(
                business_id=self.business_id,
                search_term=search_term,
                available_only=True,
                limit=10
            )
            
            if not items:
                return f"I couldn't find any menu items matching '{search_term}'. Would you like me to show you our full menu?"
            
            menu_text = f"Here are the items I found for '{search_term}':\n\n"
            for item in items:
                price = f"${float(item['price']):.2f}"
                menu_text += f"- {item['name']} - {price}"
                if item.get("description"):
                    menu_text += f" - {item['description']}"
                menu_text += "\n"
            
            return menu_text
            
        except Exception as e:
            logger.error(f"Error searching menu items: {str(e)}")
            return "I'm having trouble searching our menu right now. Please try again."

    @tool
    async def add_item_to_order(self, item_name: str, quantity: int = 1, special_instructions: Optional[str] = None) -> str:
        """Add an item to the current order.
        
        Args:
            item_name: Name of the menu item to add
            quantity: Quantity of the item (default: 1)
            special_instructions: Any special instructions for the item
        """
        try:
            # Search for the item
            items = await self.menu_db.search_menu_items(
                business_id=self.business_id,
                search_term=item_name,
                available_only=True,
                limit=5
            )
            
            if not items:
                return f"I couldn't find '{item_name}' on our menu. Would you like me to show you our available items?"
            
            # If multiple matches, try to find exact match first
            exact_match = None
            for item in items:
                if item["name"].lower() == item_name.lower():
                    exact_match = item
                    break
            
            if exact_match:
                selected_item = exact_match
            elif len(items) == 1:
                selected_item = items[0]
            else:
                # Multiple potential matches
                options = ", ".join([item["name"] for item in items[:3]])
                return f"I found several items that might match '{item_name}': {options}. Which one would you like?"
            
            # Add to current order
            order_item = OrderItem(
                menu_item_id=selected_item["id"],
                quantity=quantity,
                special_instructions=special_instructions
            )
            
            # Check if item already exists in order
            existing_item = None
            for i, existing in enumerate(self.current_order):
                if existing.menu_item_id == order_item.menu_item_id:
                    existing_item = i
                    break
            
            if existing_item is not None:
                self.current_order[existing_item].quantity += quantity
                if special_instructions:
                    current_instructions = self.current_order[existing_item].special_instructions or ""
                    self.current_order[existing_item].special_instructions = f"{current_instructions}; {special_instructions}".strip("; ")
                action = "updated"
            else:
                self.current_order.append(order_item)
                action = "added"
            
            price = float(selected_item["price"])
            total_price = price * quantity
            
            response = f"Great! I've {action} {quantity} {selected_item['name']} to your order for ${total_price:.2f}"
            if special_instructions:
                response += f" with special instructions: {special_instructions}"
            response += ". Is there anything else you'd like to add?"
            
            return response
            
        except Exception as e:
            logger.error(f"Error adding item to order: {str(e)}")
            return "I'm having trouble adding that item to your order. Please try again."

    @tool
    async def remove_item_from_order(self, item_name: str, quantity: Optional[int] = None) -> str:
        """Remove an item from the current order.
        
        Args:
            item_name: Name of the menu item to remove
            quantity: Quantity to remove (if not specified, removes all of that item)
        """
        try:
            if not self.current_order:
                return "Your order is currently empty. There's nothing to remove."
            
            # Find the item in current order
            item_found = False
            for i, order_item in enumerate(self.current_order):
                # Get menu item details to compare names
                menu_item = await self.menu_db.get_menu_item_by_id(order_item.menu_item_id)
                if menu_item and menu_item["name"].lower() == item_name.lower():
                    item_found = True
                    if quantity is None or quantity >= order_item.quantity:
                        # Remove entire item
                        removed_quantity = order_item.quantity
                        self.current_order.pop(i)
                        return f"I've removed all {removed_quantity} {menu_item['name']} from your order."
                    else:
                        # Reduce quantity
                        order_item.quantity -= quantity
                        return f"I've removed {quantity} {menu_item['name']} from your order. You still have {order_item.quantity} remaining."
            
            if not item_found:
                return f"I don't see '{item_name}' in your current order. Would you like me to show you what's currently in your order?"
            
        except Exception as e:
            logger.error(f"Error removing item from order: {str(e)}")
            return "I'm having trouble removing that item from your order. Please try again."

    @tool
    async def view_current_order(self) -> str:
        """View the current order with items and total cost."""
        try:
            if not self.current_order:
                return "Your order is currently empty. What would you like to add?"
            
            order_text = "Here's your current order:\n\n"
            total = Decimal("0.00")
            
            for order_item in self.current_order:
                menu_item = await self.menu_db.get_menu_item_by_id(order_item.menu_item_id)
                if menu_item:
                    item_price = Decimal(str(menu_item["price"]))
                    item_total = item_price * order_item.quantity
                    total += item_total
                    
                    order_text += f"- {order_item.quantity}x {menu_item['name']} - ${float(item_total):.2f}"
                    if order_item.special_instructions:
                        order_text += f" (Note: {order_item.special_instructions})"
                    order_text += "\n"
            
            order_text += f"\nOrder Total: ${float(total):.2f}"
            order_text += "\n\nWould you like to add anything else, make changes, or are you ready to confirm your order?"
            
            return order_text
            
        except Exception as e:
            logger.error(f"Error viewing current order: {str(e)}")
            return "I'm having trouble displaying your current order. Please try again."

    @tool
    async def calculate_order_total(self) -> str:
        """Calculate the total cost of the current order."""
        try:
            if not self.current_order:
                return "Your order is currently empty, so the total is $0.00."
            
            total = Decimal("0.00")
            item_count = 0
            
            for order_item in self.current_order:
                menu_item = await self.menu_db.get_menu_item_by_id(order_item.menu_item_id)
                if menu_item:
                    item_price = Decimal(str(menu_item["price"]))
                    item_total = item_price * order_item.quantity
                    total += item_total
                    item_count += order_item.quantity
            
            return f"Your order total is ${float(total):.2f} for {item_count} item(s)."
            
        except Exception as e:
            logger.error(f"Error calculating order total: {str(e)}")
            return "I'm having trouble calculating your order total. Please try again."

    @tool
    async def confirm_order(self, customer_name: str, customer_phone: Optional[str] = None, special_requests: Optional[str] = None) -> str:
        """Confirm and place the order.
        
        Args:
            customer_name: Customer's name for the order
            customer_phone: Customer's phone number (optional)
            special_requests: Any special requests for the entire order
        """
        try:
            if not self.current_order:
                return "I can't confirm an empty order. Please add some items first."
            
            if not customer_name.strip():
                return "I need a name for the order. What name should I put this under?"
            
            # Create order items for database
            order_items = []
            for order_item in self.current_order:
                menu_item = await self.menu_db.get_menu_item_by_id(order_item.menu_item_id)
                if menu_item:
                    order_items.append(OrderItemCreate(
                        menu_item_id=order_item.menu_item_id,
                        quantity=order_item.quantity,
                        unit_price=Decimal(str(menu_item["price"])),
                        special_instructions=order_item.special_instructions
                    ))
            
            # Calculate total
            total_amount = sum(item.unit_price * item.quantity for item in order_items)
            
            # Create the order
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
                # Clear current order
                self.current_order = []
                self.customer_info = {}
                
                order_id = created_order.get("id", "Unknown")
                return f"Perfect! Your order has been confirmed and placed. Your order number is {order_id}. Thank you, {customer_name}! We'll have your order ready soon."
            else:
                return "I'm sorry, there was an issue placing your order. Please try again or contact us directly."
            
        except Exception as e:
            logger.error(f"Error confirming order: {str(e)}")
            return "I'm sorry, there was an issue confirming your order. Please try again."

    @tool
    async def get_business_hours(self) -> str:
        """Get the business hours for the restaurant."""
        # This could be expanded to fetch from database
        return "We're open Monday through Friday from 11 AM to 9 PM, and Saturday through Sunday from 10 AM to 10 PM."

    async def process_voice_input(self, audio_input: str) -> str:
        """Process voice input and return response."""
        try:
            response = await self.agent.run(audio_input)
            return response.content
        except Exception as e:
            logger.error(f"Error processing voice input: {str(e)}")
            return "I'm sorry, I didn't catch that. Could you please repeat?"

    def reset_order(self):
        """Reset the current order and customer info."""
        self.current_order = []
        self.customer_info = {}