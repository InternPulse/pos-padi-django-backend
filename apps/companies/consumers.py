import asyncio
import redis
from django.conf import settings
from asgiref.sync import sync_to_async
from urllib.parse import parse_qs
from django.utils.dateparse import parse_date
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.cache import cache
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from ..agents.models import Agent


class CompanyConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):

        if not self.scope["user"].is_authenticated:
            await self.close(code=4000, reason="Authentication required")
            return

        await self.accept()

        self.conn = self.scope["connection_id"]
        self.company = self.scope["company"]
        self.params = parse_qs(self.scope["query_string"].decode())

        try:
            self.filters = await self._validate_filters()
            
            try:
                await self.channel_layer.group_add(
                    f"metrics_{self.company.id}",
                    self.channel_name
                )
            except Exception as e:
                print(f"Group add failed: {e}")

        except (ValidationError, PermissionDenied) as e:
            await self.close(code=4001, reason=str(e))
        except Exception as e:
            import traceback
            print(f"Traceback:\n{traceback.format_exc()}")
            await self.close(code=4000, reason="Internal server error")

    async def _validate_filters(self):
        """Validate and convert all filters"""
        filters = {
            "agent_id": await self._validate_agent(),
            "date_range": await self._validate_dates(),
        }
        return filters

    @database_sync_to_async
    def _validate_dates(self):
        start_date = end_date = None
        if "start_date" in self.params:
            try:
                start_date = parse_date(self.params.get("start_date", None))
                if start_date is None:
                    raise ValidationError("Invalid start_date format (use YYYY-MM-DD)")
            except ValueError as e:
                raise ValidationError(f"Invalid start_date: {str(e)}")

        if "end_date" in self.params:
            try:
                end_date = parse_date(self.params.get("end_date", None))
                if end_date is None:
                    raise ValidationError("Invalid end_date format (use YYYY-MM-DD)")
            except ValueError as e:
                raise ValidationError(f"Invalid end_date: {str(e)}")

        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date must be before End date")

        return (start_date, end_date)

    @database_sync_to_async
    def _validate_agent(self):
        if not self.params.get("agent_id"):
            return None
        try:
            return Agent.objects.get(
                agent_id=self.params["agent_id"][0],
                company=self.company
            ).agent_id
        except Agent.DoesNotExist:
            raise ValidationError("Agent not found")

    async def send_metrics(self, event):
        """Send metrics to the WebSocket"""
        if event.get("connection_id") == self.conn:
            print(f"Sending to client: {event}")  # DEBUGGING LINE
            await self.send_json(
                {
                    "type": "periodic_update",
                    "data": event["data"],
                    "timestamp": event["timestamp"],
                }
            )

    async def disconnect(self, close_code):
        if hasattr(self, "conn") and hasattr(self, "company"):
            # Get the raw Redis client from Django's cache
            redis_client = cache.client.get_client()

            # Execute both operations in parallel
            await asyncio.gather(
                # Remove connection ID from company's list
                sync_to_async(redis_client.lrem)(
                    f"company:{self.company.id}:connections",
                    1,  # Remove first occurrence
                    self.conn
                ),
                # Delete connection-specific filters
                sync_to_async(redis_client.delete)(
                    f"connection_filters:{self.conn}"
                )
            )
        await super().disconnect(close_code)
