from django.http import JsonResponse, HttpResponseRedirect
from django.conf import settings
from django.urls import reverse
import jwt
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()

class JWTAuthenticationMiddleware:
    """
    Middleware to authenticate users using JWT tokens from cookies or headers.
    This allows us to use JWT with Django's authentication system.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.public_paths = [
            '/',
            '/login/',
            '/signup/',
            '/api/token/',
            '/api/token/refresh/',
            '/api/token/verify/'
        ]
        self.jwt_authentication = JWTAuthentication()

    def __call__(self, request):
        # Skip middleware for public paths
        if any(request.path.startswith(path) for path in self.public_paths):
            return self.get_response(request)

        # Get the JWT token from the cookie or Authorization header
        token = request.COOKIES.get('access_token') or \
               request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return self.handle_missing_token(request)

        try:
            # Decode the JWT token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            # Get the user from the database
            user = User.objects.get(id=payload['user_id'])
            
            # Add the user to the request object
            request.user = user
            
            # Check admin access for admin paths
            if request.path.startswith('/admin/') and not (user.is_staff or user.is_superuser):
                return self.handle_unauthorized(request)
                
            # Check role-based access
            if request.path.startswith('/admin-dashboard/') and user.profile.role != 'ops':
                return self.handle_unauthorized(request)
            
            return self.get_response(request)
            
        except jwt.ExpiredSignatureError:
            return self.handle_expired_token(request)
        except (jwt.InvalidTokenError, jwt.DecodeError):
            return self.handle_invalid_token(request)
        except User.DoesNotExist:
            return self.handle_user_not_found(request)
    
    def handle_missing_token(self, request):
        if request.path.startswith('/api/'):
            return JsonResponse(
                {'error': 'Authentication required'}, 
                status=401
            )
        return HttpResponseRedirect(reverse('login') + f'?next={request.path}')
    
    def handle_unauthorized(self, request):
        if request.path.startswith('/api/'):
            return JsonResponse(
                {'error': 'You do not have permission to access this resource'}, 
                status=403
            )
        return HttpResponseRedirect(reverse('dashboard'))
    
    def handle_expired_token(self, request):
        if request.path.startswith('/api/'):
            return JsonResponse(
                {'error': 'Token has expired'}, 
                status=401
            )
        return HttpResponseRedirect(reverse('login') + '?expired=true')
    
    def handle_invalid_token(self, request):
        if request.path.startswith('/api/'):
            return JsonResponse(
                {'error': 'Invalid token'}, 
                status=401
            )
        return HttpResponseRedirect(reverse('login') + '?invalid=true')
    
    def handle_user_not_found(self, request):
        if request.path.startswith('/api/'):
            return JsonResponse(
                {'error': 'User not found'}, 
                status=404
            )
        return HttpResponseRedirect(reverse('login') + '?error=user_not_found')
