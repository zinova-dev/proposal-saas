from ninja import Router
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model, authenticate
from typing import List
from datetime import datetime
import weasyprint

from .models import Proposal, Client, ProposalItem
from .schemas import ProposalIn, ProposalOut
from .auth import (
    UserRegisterSchema, UserLoginSchema, TokenSchema, 
    AuthBearer, create_access_token
)

router = Router(tags=["Proposals"])
auth_router = Router(tags=["Auth"])

# --- Auth Endpoints ---

@auth_router.post("/register")
def register(request, payload: UserRegisterSchema):
    User = get_user_model()
    if User.objects.filter(username=payload.username).exists():
        return 400, {"error": "Username already exists"}
    
    user = User.objects.create_user(
        username=payload.username, 
        password=payload.password, 
        email=payload.email
    )
    return {"message": "User created successfully", "id": user.id}

@auth_router.post("/login", response=TokenSchema)
def login(request, payload: UserLoginSchema):
    user = authenticate(username=payload.username, password=payload.password)
    if not user:
        return 401, {"error": "Invalid credentials"}
    
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}

# --- Protected Proposal Endpoints ---

@router.post("/", response={201: ProposalOut}, auth=AuthBearer())
def create_proposal(request, payload: ProposalIn):
    user = request.auth  # This is the authenticated user

    # Client is tied to the authenticated user now
    client, _ = Client.objects.get_or_create(
        id=payload.client_id, 
        user=user,
        defaults={'name': 'Default Client', 'email': 'client@example.com'}
    )

    with transaction.atomic():
        proposal = Proposal.objects.create(
            user=user, client=client, title=payload.title,
            description=payload.description, tax_rate=payload.tax_rate
        )
        items = [ProposalItem(proposal=proposal, **item.dict()) for item in payload.items]
        ProposalItem.objects.bulk_create(items)

    proposal.refresh_from_db()
    return 201, proposal

@router.get("/", response=List[ProposalOut], auth=AuthBearer())
def list_proposals(request):
    user = request.auth  # Only lists proposals for this user
    return Proposal.objects.filter(user=user).prefetch_related('items').order_by('-created_at')

@router.get("/{proposal_id}/pdf", auth=AuthBearer())
def export_proposal_pdf(request, proposal_id: int):
    user = request.auth
    proposal = get_object_or_404(Proposal, id=proposal_id, user=user)
    
    html_string = render_to_string('proposal_pdf.html', {
        'proposal': proposal,
        'date': datetime.now().strftime('%Y-%m-%d')
    })
    
    pdf_file = weasyprint.HTML(string=html_string).write_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="proposal_{proposal.id}.pdf"'
    return response
