import json
import uuid
from urllib.parse import parse_qs
from django.utils.dateparse import parse_date
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.cache import cache
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Company
from ..agents.models import Agent


class CompanyConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.conn = str(uuid.uuid4())
        # Parse query parameters
        self.params = parse_qs(self.scope["query_string"].decode())

        try:
            # Validate and store filters
            await self._authenticate()
            self.filters = await self._validate_filters()
            await self._store_connection_filters
            await self._join_group()
            await self.accept()
        except (ValidationError, PermissionDenied) as e:
            await self.close(code=4001, reason=str(e))
        except Exception as e:
            await self.close(code=4000, reason="Internal server error")
            # Log the exception here if needed

    async def _validate_filters(self):
        """Validate and convert all filters"""
        filters = {
            "company": await self.get_company(),
            "agent_id": await self._validate_agent(),
            "date_range": await self._validate_dates(),
        }
        if not filters["company"]:
            raise ValidationError("Company not found")
        return filters
    
    async def _store_connection_filters(self):
        """Store the connection filters in cache"""
        await cache.set_async(
            f"connection:{self.conn}:filters",
            {
                "agent_id": self.filters["agent_id"],
                "start_date": self.filters["date_range"][0].isoformat() if self.filters["date_range"] else None,
                "end_date": self.filters["date_range"][1].isoformat() if self.filters["date_range"] else None,
            },
            timeout = 3600
        )
        await cache.add_async(
            f"company:{self.company.id}:connections",
            self.conn,
        )

    async def _authenticate(self):
        """Authenticate the user and get the company"""
        if not self.scope["user"].is_authenticated:
            raise PermissionDenied("User not authenticated")
        
        self.get_company = await self.get_company()
        if not self.get_company:
            raise PermissionDenied("Company not found")
        

    @database_sync_to_async
    def _validate_dates(self):
        start_date = parse_date(self.params.get("start_date", [None])[0])
        end_date = parse_date(self.params.get("end_date", [None])[0])

        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date must be before End date")
        return start_date, end_date
    
    @database_sync_to_async
    def _validate_agent(self):
        if not self.params.get("agent_id"):
            return None
        try:
            return Agent.objects.get(
                agent_id=self.params["agent_id"][0],
                company=self.scope["user"].company
            ).agent_id
        except Agent.DoesNotExist:
            raise ValidationError("Agent not found")

    @database_sync_to_async
    def get_company(self):
        return Company.objects.filter(owner=self.scope["user"]).first()
    
    async def _join_group(self):
        """Join the group for the company"""
        company = self.filters["company"]
        await self.channel_layer.group_add(
            f"metrics_{company.id}",
            self.channel_name,
        )
    
    async def send_metrics(self, event):
        """Send metrics to the WebSocket"""
        if event.get("connection_id") == self.conn:
            await self.send_json(
                {
                    "type": "periodic_update",
                    "data": event["data"],
                    "timestamp": event["timestamp"],
                }
            )

    async def disconnect(self, close_code):
        if hasattr(self, "filters"):
            company = self.filters["company"]
            await self.channel_layer.group_discard(
                f"metrics_{company.id}",
                self.channel_name,
            )
        await cache.delete_async(f"connection:{self.conn}:filters")
        await cache.remove_from_list_async(f"company:{self.company.id}:connections", self.conn)
        await super().disconnect(close_code)
        
    
