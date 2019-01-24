
from users.serializers import CustomUserSerializer


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        # 'user': CustomUserSerializer(user, context={'request': request}).data
    }