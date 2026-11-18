from ninja import Schema
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class ProposalItemIn(Schema):
    description: str
    quantity: int = 1
    unit_price: Decimal

class ProposalItemOut(Schema):
    id: int
    description: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal

class ProposalIn(Schema):
    client_id: int
    title: str
    description: Optional[str] = None
    tax_rate: Decimal = Decimal('0.00')
    items: List[ProposalItemIn]

class ProposalOut(Schema):
    id: int
    title: str
    description: Optional[str]          
    status: str
    tax_rate: Decimal
    subtotal: Decimal
    total: Decimal
    created_at: datetime
    items: List[ProposalItemOut]
    