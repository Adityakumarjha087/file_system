from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model, authenticate, login as auth_login
from django.core.exceptions import ValidationError
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.http import FileResponse, Http404, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.urls import reverse
import json

from .models import UploadedFile, Profile
from .serializers import (
    UserSerializer, 
    CustomTokenObtainPairSerializer,
    UploadedFileSerializer,
    FileUploadSerializer
)
from .permissions import IsOpsUser, IsClientUser

User = get_user_model()

class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get the role from request data or use 'client' as default
        role = request.data.get('role', 'client')
        if role not in dict(Profile.ROLE_CHOICES).keys():
            return Response(
                {'error': 'Invalid role. Must be either "ops" or "client"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user with profile
        user = serializer.save()
        user.profile.role = role
        user.profile.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'message': 'User created successfully',
                'user': UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = (permissions.AllowAny,)

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.profile.role == 'ops':
                return redirect('admin_dashboard')
            return redirect('client_dashboard')
        return render(request, 'login.html')

    def post(self, request):
        # Handle both form data and JSON
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                username = data.get('username')
                password = data.get('password')
            except json.JSONDecodeError:
                return JsonResponse(
                    {'error': 'Invalid JSON'}, 
                    status=400
                )
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
        
        if not username or not password:
            if request.content_type == 'application/json':
                return JsonResponse(
                    {'error': 'Username and password are required'}, 
                    status=400
                )
            else:
                return render(request, 'login.html', {
                    'error': 'Username and password are required'
                })
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            refresh = RefreshToken.for_user(user)
            
            # Prepare response data
            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'role': user.profile.role,
                'redirect_url': reverse('admin_dashboard' if user.profile.role == 'ops' else 'dashboard')
            }
            
            # For API requests, return JSON
            if request.content_type == 'application/json':
                response = JsonResponse(response_data, status=200)
            else:
                # For form submissions, redirect
                response = redirect(response_data['redirect_url'])
            
            # Set cookies
            response.set_cookie(
                key='access_token',
                value=str(refresh.access_token),
                httponly=True,
                samesite='Lax',
                secure=request.is_secure(),
                max_age=60 * 60 * 24 * 7  # 7 days
            )
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                samesite='Lax',
                secure=request.is_secure(),
                max_age=60 * 60 * 24 * 30  # 30 days
            )
            
            # Set success message for form submission
            if request.content_type != 'application/json':
                messages.success(request, 'Successfully logged in!')
            
            return response
        
        # Handle failed authentication
        if request.content_type == 'application/json':
            return JsonResponse(
                {'error': 'Invalid username or password'}, 
                status=400
            )
        else:
            return render(request, 'login.html', {
                'error': 'Invalid username or password',
                'username': username
            })

class FileUploadView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated, IsOpsUser]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            uploaded_file = UploadedFile.objects.create(
                file=serializer.validated_data['file'],
                uploaded_by=request.user,
                original_filename=serializer.validated_data['file'].name
            )
            
            return Response(
                {
                    'message': 'File uploaded successfully',
                    'file': UploadedFileSerializer(uploaded_file, context={'request': request}).data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class FileListView(generics.ListAPIView):
    serializer_class = UploadedFileSerializer
    permission_classes = [permissions.IsAuthenticated, IsClientUser]
    
    def get_queryset(self):
        return UploadedFile.objects.all().order_by('-uploaded_at')
    
    def get_serializer_context(self):
        return {'request': self.request}

class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.profile.role if hasattr(user, 'profile') else 'client',
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser
        })


class FileDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Allow all authenticated users
    
    def get(self, request, token, *args, **kwargs):
        signer = TimestampSigner()
        try:
            # Verify the token and get the file ID
            unsigned_value = signer.unsign(token, max_age=3600)  # Token valid for 1 hour
            file_id = int(unsigned_value.split(':')[0])
            
            # Get the file
            uploaded_file = get_object_or_404(UploadedFile, id=file_id)
            
            # Return the file as a download response
            response = FileResponse(uploaded_file.file)
            response['Content-Disposition'] = f'attachment; filename="{uploaded_file.original_filename}"'
            return response
            
        except (BadSignature, SignatureExpired, ValueError, IndexError):
            raise Http404("Invalid or expired download link")
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
