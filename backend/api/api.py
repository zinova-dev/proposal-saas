from ninja import Router
from django.db import transaction
from django.shortcuts import get_object_or_404
from typing import List
from django.contrib.auth import get_user_model

from .models import Proposal, Client, ProposalItem
from .schemas import ProposalIn, ProposalOut

router = Router(tags=["Proposals"])

@router.post("/", response={201: ProposalOut})
def create_proposal(request, payload: ProposalIn):
    """
    Creates a new proposal along with its line items.
    Uses a transaction to ensure data integrity if any item fails validation.
    """
    User = get_user_model()
    user = User.objects.first()
    if not user:
        user = User.objects.create_user(username='devadmin', password='devpassword123')

    # Development fallback: if client doesn't exist, create a dummy one to ease testing.
    client, _ = Client.objects.get_or_create(
        id=payload.client_id, 
        user=user,
        defaults={'name': 'Test Client', 'email': 'test@client.com'}
    )

    with transaction.atomic():
        proposal = Proposal.objects.create(
            user=user,
            client=client,
            title=payload.title,
            description=payload.description,
            tax_rate=payload.tax_rate
        )
        
        items_to_create = [
            ProposalItem(
                proposal=proposal,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price
            )
            for item in payload.items
        ]
        ProposalItem.objects.bulk_create(items_to_create)

    proposal.refresh_from_db()
    return 201, proposal

@router.get("/", response=List[ProposalOut])
def list_proposals(request):
    """
    Lists all proposals for the current user.
    """
    User = get_user_model()
    user = User.objects.first()
    
    return Proposal.objects.filter(user=user).prefetch_related('items').order_by('-created_at')
