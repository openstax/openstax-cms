from django.contrib.auth.models import User
from rest_framework import viewsets

from .serializers import UserSerializer
 
class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    #model = User
    
    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(pk=user.pk)
