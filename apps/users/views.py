from rest_framework.viewsets import ModelViewSet
from .models import User
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny


class UserViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer

