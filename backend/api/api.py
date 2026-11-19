from datetime import datetime
from typing import List

import weasyprint
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from ninja import Router

from .auth import (
    AuthBearer,
    QueryTokenAuth,
    TokenSchema,
    UserLoginSchema,
    UserRegisterSchema,
    create_access_token,
)
from .models import Client, Proposal, ProposalItem
from .schemas import ProposalIn, ProposalOut

router = Router(tags=["Proposals"])
auth_router = Router(tags=["Auth"])


@auth_router.post("/register", response={200: dict, 400: dict})
def register(request, payload: UserRegisterSchema):
    User = get_user_model()
    if User.objects.filter(username=payload.username).exists():
        return 400, {"error": "Username already exists"}

    user = User.objects.create_user(
        username=payload.username,
        password=payload.password,
        email=payload.email or "",
    )
    return {"message": "User created successfully", "id": user.id}


@auth_router.post("/login", response={200: TokenSchema, 401: dict})
def login(request, payload: UserLoginSchema):
    user = authenticate(username=payload.username, password=payload.password)
    if not user:
        return 401, {"error": "Invalid credentials"}

    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


@router.post("/", response={201: ProposalOut}, auth=AuthBearer())
def create_proposal(request, payload: ProposalIn):
    user = request.auth

    # Clients are scoped per user. Fall back to a default client until
    # the client management screen is available.
    client = Client.objects.filter(id=payload.client_id, user=user).first()
    if client is None:
        client, _ = Client.objects.get_or_create(
            user=user,
            name="Default Client",
            defaults={"email": "client@example.com"},
        )

    with transaction.atomic():
        proposal = Proposal.objects.create(
            user=user,
            client=client,
            title=payload.title,
            description=payload.description,
            tax_rate=payload.tax_rate,
        )
        ProposalItem.objects.bulk_create(
            [ProposalItem(proposal=proposal, **item.dict()) for item in payload.items]
        )

    proposal.refresh_from_db()
    return 201, proposal


@router.get("/", response=List[ProposalOut], auth=AuthBearer())
def list_proposals(request):
    return (
        Proposal.objects.filter(user=request.auth)
        .prefetch_related("items")
        .order_by("-created_at")
    )


@router.delete("/{proposal_id}", response={204: None}, auth=AuthBearer())
def delete_proposal(request, proposal_id: int):
    proposal = get_object_or_404(Proposal, id=proposal_id, user=request.auth)
    proposal.delete()
    return 204, None


@router.get("/{proposal_id}/pdf", auth=[AuthBearer(), QueryTokenAuth()])
def export_proposal_pdf(request, proposal_id: int):
    proposal = get_object_or_404(Proposal, id=proposal_id, user=request.auth)

    html_string = render_to_string(
        "proposal_pdf.html",
        {"proposal": proposal, "date": datetime.now().strftime("%Y-%m-%d")},
    )
    pdf_file = weasyprint.HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="proposal_{proposal.id}.pdf"'
    return response
