from django.conf import settings

from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from redis_utils import delete_redis, get_redis

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request, *args, **kwargs):
        delete_redis(settings.PAYMENT_SESSION_KEY%(request.user.id))
        return Response({}, status=200)


