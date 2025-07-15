from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal

class StockLevelBase(BaseModel):
  quantity_available: int = Field(..., description="Quantity available of the stock level")
  total_quantity: int = Field(..., description="Total quantity of the stock level")

class StockLevelCreate(StockLevelBase):
  pass
  
