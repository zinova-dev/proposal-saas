from ninja import Router
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from typing import List
from datetime import datetime
import weasyprint

from .models import Proposal, Client, ProposalItem
from .schemas import ProposalIn, ProposalOut

router = Router(tags=["Proposals"])

@router.post("/", response={201: ProposalOut})
def create_proposal(request, payload: ProposalIn):
    User = get_user_model()
    user = User.objects.first()
    if not user:
        user = User.objects.create_user(username='devadmin', password='devpassword123')

    client, _ = Client.objects.get_or_create(
        id=payload.client_id, 
        user=user,
        defaults={'name': 'Test Client', 'email': 'test@client.com'}
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

@router.get("/", response=List[ProposalOut])
def list_proposals(request):
    User = get_user_model()
    user = User.objects.first()
    return Proposal.objects.filter(user=user).prefetch_related('items').order_by('-created_at')

@router.get("/{proposal_id}/pdf")
def export_proposal_pdf(request, proposal_id: int):
    """
    Generates a PDF version of the proposal using WeasyPrint.
    Renders a HTML template to ensure consistent formatting.
    """
    proposal = get_object_or_404(Proposal, id=proposal_id)
    
    html_string = render_to_string('proposal_pdf.html', {
        'proposal': proposal,
        'date': datetime.now().strftime('%Y-%m-%d')
    })
    
    pdf_file = weasyprint.HTML(string=html_string).write_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="proposal_{proposal.id}.pdf"'
    return response
