from django.contrib.auth import authenticate, get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()  # ✅ এটাই সঠিক, direct import না


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email    = request.data.get('email')
    password = request.data.get('password')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    user = authenticate(request, email=email, password=password)
    if not user:
        return Response(
            {'success': False, 'message': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)
    return Response({
        'success': True,
        'data': {
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id':       user.id,
                'username': user.username,
                'email':    user.email,
            }
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    return Response({
        'success': True,
        'data': {
            'id':       user.id,
            'username': user.username,
            'email':    user.email,
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    from rest_framework_simplejwt.views import TokenRefreshView
    return TokenRefreshView.as_view()(request._request)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
        return Response({'success': True, 'message': 'Logged out'})
    except Exception:
        return Response({'success': False}, status=400)