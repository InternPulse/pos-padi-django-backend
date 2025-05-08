import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.db.models import (
    Q,
    Sum,
    Count,
    Case,
    When,
    Value,
    IntegerField,
    DecimalField,
)
from django.db.models.functions import Coalesce
from rest_framework.generics import RetrieveAPIView, ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Agent
from .serializers import AgentSerializer
from ..users.permissions import (
    IsOwnerOrSuperuser,
    IsOwnerOrAgentOrSuperuser,
    IsAgentOrSuperuser,
)
from ..users.models import User
from ..external_tables.models import Transaction


class AgentListCreateView(ListCreateAPIView):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [IsOwnerOrSuperuser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Agent.objects.all()
        elif self.request.user.role == "owner":
            return Agent.objects.filter(company=self.request.user.company)
        return Agent.objects.none()

    @swagger_auto_schema(
        operation_summary="List or create agents",
        operation_description="Retrieve a list of agents or create a new agent for the authenticated user's company.",
        responses={
            200: "List of agents retrieved successfully.",
            201: "Agent created successfully.",
            400: "Invalid data provided.",
            403: "Permission denied.",
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new agent",
        operation_description="Create a new agent by providing the required details.",
        request_body=AgentSerializer,
        responses={
            201: "Agent created successfully.",
            400: "Invalid data provided.",
            403: "Permission denied.",
        },
    )
    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            user = response.data.get("user_id")
            user_email = user.get("email")
            token = jwt.encode(
                {"email": user_email, "exp": datetime.now() + timedelta(hours=24)},
                settings.SECRET_KEY,
                algorithm="HS256",
            )
            reset_url = request.build_absolute_uri(
                f"https://pos-padi.netlify.app/agent-complete-signup/{token}/"
            )
            send_mail(
                subject="POS-Padi Onboarding",
                message=f"Click the link to complete your onboarding: {reset_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
            )
        return response


class AgentOnboardView(APIView):
    permission_classes = [AllowAny]
    queryset = Agent.objects.all()

    @swagger_auto_schema(
        operation_summary="Onboard an agent",
        operation_description="Complete the onboarding process for an agent by setting a password. Requires a valid token provided in the query parameters.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The password to set for the agent."
                ),
                "confirm_password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Confirmation of the password. Must match the password."
                ),
            },
            required=["password", "confirm_password"],
        ),
        manual_parameters=[
            openapi.Parameter(
                "token",
                openapi.IN_QUERY,
                description="The token required for onboarding, provided in the query parameters.",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: "Password set successfully. You can now log in.",
            400: "Invalid token, missing fields, or passwords do not match.",
        },
    )
    def post(self, request, *args, **kwargs):
        token = request.query_params.get("token")

        if not token:
            return Response(
                {"error": "Token not provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            email = payload.get("email")
        except jwt.ExpiredSignatureError:
            return Response(
                {"error": "Token expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.InvalidTokenError:
            return Response({"error": "Invalid token"})

        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if not password or not confirm_password:
            return Response(
                {"error": "Password and confirm password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if password != confirm_password:
            return Response(
                {"error": "Passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(password)
        user.is_verified = True
        user.save()

        return Response(
            {"message": "Password set successfully. You can now log in."},
            status=status.HTTP_200_OK,
        )


class AgentRetrieveUpdateView(RetrieveUpdateAPIView):
    queryset = Agent.objects.none()
    serializer_class = AgentSerializer
    permission_classes = [IsOwnerOrAgentOrSuperuser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "is_superuser", False):
            return Agent.objects.all()
        elif getattr(user, "role", None) == "agent":
            return Agent.objects.filter(user_id=user)
        elif getattr(user, "role", None) == "owner":
            return Agent.objects.filter(company=user.company)
        return Agent.objects.none()

    @swagger_auto_schema(
        operation_summary="Retrieve a specific agent",
        operation_description="Retrieve details of a specific agent by their ID.",
        responses={
            200: "Agent details retrieved successfully.",
            404: "Agent not found.",
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        """
        Update agent status
        """
        if request.data:
            return Response(
                {"error": "This endpoint does not accept any data in the request"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        agent = self.get_object()
    
        # Toggle the status (no frontend input needed)
        agent.status = "inactive" if agent.status == "active" else "active"
        agent.save()
        
        return Response(
            {"status": f"Agent status updated to {agent.status}"},
            status=status.HTTP_200_OK,
        )
        


class AgentMetricsView(APIView):
    permission_classes = [IsAgentOrSuperuser]

    @swagger_auto_schema(
        operation_summary="Retrieve agent metrics",
        operation_description="Retrieve metrics for a specific agent, optionally filtered by date range.",
        manual_parameters=[
            openapi.Parameter(
                "start_date",
                openapi.IN_QUERY,
                description="Start date for filtering metrics (YYYY-MM-DD).",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "end_date",
                openapi.IN_QUERY,
                description="End date for filtering metrics (YYYY-MM-DD).",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: "Metrics retrieved successfully.",
            400: "Invalid date format or other errors.",
            404: "Agent not found.",
        },
    )
    def get(self, request, *args, **kwargs):
        agent = get_object_or_404(Agent, user_id=self.request.user)

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        try:
            if start_date and end_date:
                start_date_obj = parse_date(start_date)
                end_date_obj = parse_date(end_date)

                if start_date_obj > end_date_obj:
                    return Response(
                        {
                            "message": "Date error",
                            "error": "Start date cannot be after End date",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                date_range = [start_date_obj, end_date_obj]

            elif start_date:
                start_date_obj = parse_date(start_date)
                date_range = [start_date_obj]

            elif end_date:
                end_date_obj = parse_date(end_date)
                date_range = [parse_date("2025-01-01"), end_date]

            else:
                date_range = None

        except (ValueError, TypeError):
            return Response(
                {
                    "message": "Invalid date format",
                    "error": "Invalid date format. Use YYYY-MM-DD.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if date_range:
            filters = {"agent_id": agent.id, "created_at__range": date_range}
        else:
            filters = {"agent_id": agent.id}

        transactions = Transaction.objects.filter(**filters).select_related(
            "agent_id", "customer_id"
        )
        metrics = transactions.aggregate(
            total_transactions=Count("id"),
            total_successful=Coalesce(
                Sum(
                    Case(
                        When(status="successful", then=1),
                        default=0,
                        output_field=IntegerField(),
                    )
                ),
                Value(0, output_field=IntegerField()),
            ),
            total_failed=Coalesce(
                Sum(
                    Case(
                        When(status="failed", then=1),
                        default=0,
                        output_field=IntegerField(),
                    )
                ),
                Value(0, output_field=IntegerField()),
            ),
            total_amount=Coalesce(
                Sum("amount", filter=Q(status="successful")),
                Value(0, output_field=DecimalField()),
            ),
            total_customers=Count("customer_id", distinct=True),
        )

        return Response(
            {"message": "Metrics retrieved successfully", "data": metrics},
            status=status.HTTP_200_OK,
        )
