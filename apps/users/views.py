from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .models import User
from .serializers import UserSerializer, TransactionSerializer
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import openpyxl
from io import BytesIO
import requests
from rest_framework.decorators import action


# Node.js endpoint configuration
NODEJS_API_URL = "http://localhost:3000/api/transactions"  # Replace with actual Node.js API URL
NODEJS_LOG_URL = f"{NODEJS_API_URL}/logs"  # Assuming a logs endpoint

class UserViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # def get_permissions(self):
    #     if self.action in ['create']:
    #         return [AllowAny()]
    #     return [IsAuthenticated()]

    def _fetch_transactions(self, params):
        """Helper method to fetch transactions from Node.js API"""
        try:
            response = requests.get(NODEJS_API_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Failed to fetch transactions: {str(e)}"}

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profit_loss_report(self, request):
        user = request.user
        if user.role != 'owner':
            return Response({"error": "Only owners can view profit/loss reports"}, status=status.HTTP_403_FORBIDDEN)

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        terminal = request.query_params.get('terminal')
        agent_id = request.query_params.get('agent')

        params = {
            'start_date': start_date,
            'end_date': end_date,
            'terminal': terminal,
            'agent_id': agent_id
        }

        transactions = self._fetch_transactions(params)
        if "error" in transactions:
            return Response(transactions, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        income = sum(float(t['amount']) for t in transactions if t['transaction_type'] == 'income')
        expenses = sum(float(t['amount']) for t in transactions if t['transaction_type'] == 'expense')
        net_profit = income - expenses

        data = {
            'total_income': income,
            'total_expenses': expenses,
            'net_profit': net_profit,
            'period': f"{start_date} to {end_date}"
        }

        export_format = request.query_params.get('export')
        if export_format:
            if export_format.lower() == 'pdf':
                return self.export_to_pdf(data, 'Profit and Loss Report')
            elif export_format.lower() == 'excel':
                return self.export_to_excel(data, 'Profit and Loss Report')
        
        return Response(data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def daily_report(self, request):
        date = request.query_params.get('date', str(timezone.now().date()))
        agent_id = request.query_params.get('agent')
        terminal = request.query_params.get('terminal')

        params = {
            'date': date,
            'agent_id': agent_id,
            'terminal': terminal
        }

        transactions = self._fetch_transactions(params)
        if "error" in transactions:
            return Response(transactions, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        income = sum(float(t['amount']) for t in transactions if t['transaction_type'] == 'income')
        expenses = sum(float(t['amount']) for t in transactions if t['transaction_type'] == 'expense')
        net_profit = income - expenses

        data = {
            'date': date,
            'total_income': income,
            'total_expenses': expenses,
            'net_profit': net_profit
        }
        return Response(data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def net_profit(self, request):
        start_date = request.query_params.get('start_date', str(timezone.now().date() - timedelta(days=30)))
        end_date = request.query_params.get('end_date', str(timezone.now().date()))
        user_id = request.user.id

        params = {
            'start_date': start_date,
            'end_date': end_date,
            'user_id': user_id
        }

        transactions = self._fetch_transactions(params)
        if "error" in transactions:
            return Response(transactions, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        income = sum(float(t['amount']) for t in transactions if t['transaction_type'] == 'income')
        expenses = sum(float(t['amount']) for t in transactions if t['transaction_type'] == 'expense')
        net_profit = income - expenses

        return Response({
            'net_profit': net_profit,
            'period': f"{start_date} to {end_date}"
        })

    def export_to_pdf(self, data, title):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        
        elements = []
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Paragraph(f"Period: {data['period']}", styles['Normal']))
        
        table_data = [
            ['Metric', 'Amount'],
            ['Total Income', f"${data['total_income']:.2f}"],
            ['Total Expenses', f"${data['total_expenses']:.2f}"],
            ['Net Profit', f"${data['net_profit']:.2f}"]
        ]
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        
        doc.build(elements)
        buffer.seek(0)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{title}.pdf"'
        response.write(buffer.getvalue())
        buffer.close()
        return response

    def export_to_excel(self, data, title):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Report"
        
        ws.append([title])
        ws.append([f"Period: {data['period']}"])
        ws.append([])
        ws.append(['Metric', 'Amount'])
        ws.append(['Total Income', data['total_income']])
        ws.append(['Total Expenses', data['total_expenses']])
        ws.append(['Net Profit', data['net_profit']])
        
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{title}.xlsx"'
        response.write(buffer.getvalue())
        buffer.close()
        return response


class TransactionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return []  # Not using Django ORM since transactions are from Node.js

    def list(self, request):
        params = request.query_params
        transactions = self._fetch_transactions(params)
        if "error" in transactions:
            return Response(transactions, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data['user_id'] = request.user.id
        
        try:
            response = requests.post(NODEJS_API_URL, json=validated_data, timeout=10)
            response.raise_for_status()
            return Response(response.json(), status=status.HTTP_201_CREATED)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        transaction_id = kwargs.get('pk')
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        try:
            response = requests.put(f"{NODEJS_API_URL}/{transaction_id}", json=serializer.validated_data, timeout=10)
            response.raise_for_status()
            
            # Log edit
            requests.post(
                NODEJS_LOG_URL,
                json={
                    'transaction_id': transaction_id,
                    'action': 'edit',
                    'user': request.user.email,
                    'timestamp': str(timezone.now())
                },
                timeout=10
            )
            return Response(response.json())
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        transaction_id = kwargs.get('pk')
        try:
            response = requests.delete(f"{NODEJS_API_URL}/{transaction_id}", timeout=10)
            response.raise_for_status()
            
            # Log deletion
            requests.post(
                NODEJS_LOG_URL,
                json={
                    'transaction_id': transaction_id,
                    'action': 'delete',
                    'user': request.user.email,
                    'timestamp': str(timezone.now())
                },
                timeout=10
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)