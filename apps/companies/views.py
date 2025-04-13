from django.db import transaction
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import Company
from .serializers import CompanySerializer
from .utils import send_deactivation_emails
from ..users.permissions import IsOwner
from ..users.models import UserRoles
from ..external_tables.models import Terminal, Agent



class CompanyViewSet(ModelViewSet):
    permission_classes = [IsOwner]
    queryset = Company.objects.none()
    serializer_class = CompanySerializer
    http_method_names = [
        m for m in ModelViewSet.http_method_names if m not in ["patch"]
    ]

    def get_queryset(self):
        try:
            return Company.objects.filter(
                id=self.request.user.company.id, is_active=True
            ).select_related("owner")
        except AttributeError:
            return Company.objects.none()

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        company = self.get_object()

        Agent.objects.filter(
            company=company, user__role=UserRoles.AGENT
        ).update(
            role=UserRoles.CUSTOMER
        )

        Terminal.objects.filter(
            company=company.id
        ).update(
            is_active=False
        )

        company.owner.role=UserRoles.CUSTOMER
        company.owner.save(update_fields=["role"])

        company.deactivate()

        # Delay sending emails till changes commited to dB
        transaction.on_commit(
            lambda: send_deactivation_emails(company, request.user)
        )
        return Response(
            {
                "detail": "Company deactivated successfully",
                "actions": {
                    "agents_downgraded": Agent.objects.filter(
                        company=company,
                        user__role=UserRoles.CUSTOMER
                    ).count(),
                    "terminals_deactivated": Terminal.objects.filter(
                        company_id=company.id,
                        is_active=False
                    ).count()
                }
            },
            status=status.HTTP_200_OK
        )
