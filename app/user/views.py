from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import UserSerializer, AuthTokenSerializer

# Remember : view = api view
#


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    # the serializer we defined in the serializers.py file
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

# ----------------------------------------------------------------------
# We define an API using a base class that can retrieve and update
# it implements the methods get, put, patch
# ----------------------------------------------------------------------


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated users"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authentication user"""
        return self.request.user
