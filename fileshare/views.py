import os
import jwt
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import UploadedFile
from api.serializers import FileUploadSerializer
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

def home(request):
    """Render the home page."""
    # If user is authenticated, redirect to appropriate dashboard
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile') and request.user.profile.role == 'ops':
            return redirect('admin_dashboard')
        return redirect('dashboard')
    
    # For unauthenticated users, show the home template
    return render(request, 'home.html', {
        'user': request.user if hasattr(request, 'user') else None
    })

def login_view(request):
    """Handle user login with role-based redirection and JWT tokens."""
    # If user is already logged in, redirect to appropriate dashboard
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile') and request.user.profile.role == 'ops':
            return redirect('admin_dashboard')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please provide both username and password')
            return render(request, 'login.html')
            
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Log the user in with Django session
            login(request, user)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Get the next URL or default dashboard
            next_url = request.GET.get('next')
            if not next_url:
                if hasattr(user, 'profile') and user.profile.role == 'ops':
                    next_url = reverse('admin_dashboard')
                else:
                    next_url = reverse('dashboard')
            
            # Create response with redirect
            response = redirect(next_url)
            
            # Set JWT tokens in cookies
            response.set_cookie(
                'access_token',
                str(refresh.access_token),
                httponly=True,
                samesite='Lax',
                secure=request.is_secure(),
                max_age=60 * 60 * 24 * 7  # 7 days
            )
            response.set_cookie(
                'refresh_token',
                str(refresh),
                httponly=True,
                samesite='Lax',
                secure=request.is_secure(),
                max_age=60 * 60 * 24 * 14  # 14 days
            )
            
            messages.success(request, 'Successfully logged in!')
            return response
        else:
            messages.error(request, 'Invalid username or password.')
    
    # For GET requests, show the login form
    return render(request, 'login.html', {
        'next': request.GET.get('next', '')
    })

def signup_view(request):
    """Handle user registration."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        is_admin = request.POST.get('is_admin') == 'on'
        admin_token = request.POST.get('admin_token')
        
        # Basic validation
        if password1 != password2:
            messages.error(request, "Passwords don't match.")
            return redirect('signup')
            
        # Check if username is taken
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return redirect('signup')
            
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            
            # Set role based on admin status
            if is_admin:
                # In a real app, verify the admin token here
                user.profile.role = 'ops'
            else:
                user.profile.role = 'client'
            user.profile.save()
            
            # Log the user in with Django session
            login(request, user)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Create response with redirect
            response = redirect('dashboard')
            
            # Set JWT tokens in cookies
            response.set_cookie(
                'access_token',
                str(refresh.access_token),
                httponly=True,
                samesite='Lax',
                secure=request.is_secure()
            )
            response.set_cookie(
                'refresh_token',
                str(refresh),
                httponly=True,
                samesite='Lax',
                secure=request.is_secure()
            )
            
            messages.success(request, 'Account created successfully!')
            return response
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    return render(request, 'signup.html')

def dashboard_view(request):
    """Render the regular user dashboard."""
    # First try session authentication
    if request.user.is_authenticated:
        # Check if user is an admin trying to access user dashboard
        if hasattr(request.user, 'profile') and request.user.profile.role == 'ops':
            return redirect('admin_dashboard')
        
        # Get all files from all users
        files = UploadedFile.objects.all()
        files_count = files.count()
        
        # Calculate total storage used (in MB)
        total_size = sum(file.file.size for file in files if file.file)
        storage_used = round(total_size / (1024 * 1024), 2)  # Convert to MB
        
        # If JWT token is missing, create one
        if not request.COOKIES.get('access_token'):
            refresh = RefreshToken.for_user(request.user)
            response = render(request, 'dashboard.html', {
                'user': request.user,
                'files': files,
                'files_count': files_count,
                'storage_used': storage_used,
                'is_admin': False,
            })
            response.set_cookie(
                'access_token',
                str(refresh.access_token),
                httponly=True,
                samesite='Lax',
                secure=request.is_secure()
            )
            response.set_cookie(
                'refresh_token',
                str(refresh),
                httponly=True,
                samesite='Lax',
                secure=request.is_secure()
            )
            return response
            
        return render(request, 'dashboard.html', {
            'user': request.user,
            'files': files,
            'files_count': files_count,
            'storage_used': storage_used,
            'is_admin': False,
        })
    
    # Then try JWT authentication
    token = request.COOKIES.get('access_token')
    if token:
        try:
            # Verify JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            
            # Check if user is an admin trying to access user dashboard
            if hasattr(user, 'profile') and user.profile.role == 'ops':
                return redirect('admin_dashboard')
            
            # Get all files from all users
            files = UploadedFile.objects.all()
            files_count = files.count()
            
            # Calculate total storage used (in MB)
            total_size = sum(file.file.size for file in files if file.file)
            storage_used = round(total_size / (1024 * 1024), 2)  # Convert to MB
            
            # Log the user in with session
            login(request, user)
            
            return render(request, 'dashboard.html', {
                'user': user,
                'files': files,
                'files_count': files_count,
                'storage_used': storage_used,
                'is_admin': False,
            })
            
        except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
            # If JWT is invalid, try to refresh token
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                try:
                    from rest_framework_simplejwt.tokens import RefreshToken
                    refresh = RefreshToken(refresh_token)
                    new_token = str(refresh.access_token)
                    
                    # Update the access token in cookies
                    response = redirect('dashboard')
                    response.set_cookie(
                        'access_token',
                        new_token,
                        httponly=True,
                        samesite='Lax',
                        secure=request.is_secure()
                    )
                    return response
                except Exception:
                    pass
    
    # If no valid authentication, redirect to login with next parameter
    return redirect(f'/login/?next={request.path}')

def admin_dashboard_view(request):
    """Render the admin dashboard with all files and upload functionality."""
    # First try JWT authentication
    token = request.COOKIES.get('access_token')
    if token:
        try:
            # Verify JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            
            # Check if user is an admin
            if not hasattr(user, 'profile') or user.profile.role != 'ops':
                return redirect('dashboard')
            
            # Get all files from all users
            files = UploadedFile.objects.all()
            files_count = files.count()
            users_count = User.objects.count()
            
            # Initialize the serializer for the upload form
            upload_form = FileUploadSerializer()
            
            context = {
                'user': user,
                'files': files,
                'files_count': files_count,
                'users_count': users_count,
                'is_admin': True,
                'upload_form': upload_form
            }
            return render(request, 'admin_dashboard.html', context)
            
        except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
            # If JWT is invalid, try to refresh token
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                try:
                    from rest_framework_simplejwt.tokens import RefreshToken
                    refresh = RefreshToken(refresh_token)
                    new_token = str(refresh.access_token)
                    
                    # Update the access token in cookies
                    response = redirect('admin_dashboard')
                    response.set_cookie(
                        'access_token',
                        new_token,
                        httponly=True,
                        samesite='Lax',
                        secure=request.is_secure()
                    )
                    return response
                except Exception:
                    pass
    
    # Fall back to session authentication
    if request.user.is_authenticated:
        # Check if user is an admin
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'ops':
            return redirect('dashboard')
        
        # Get all files and users count
        files = UploadedFile.objects.all()
        files_count = files.count()
        users_count = User.objects.count()
        
        context = {
            'user': request.user,
            'files': files,
            'files_count': files_count,
            'users_count': users_count,
            'is_admin': True,
            'upload_form': FileUploadForm()
        }
        return render(request, 'admin_dashboard.html', context)
    
    # If no valid authentication, redirect to login with next parameter
    return redirect(f'/login/?next={request.path}')

def upload_file_view(request):
    """Handle file uploads from the admin dashboard."""
    if request.method == 'POST' and request.user.is_authenticated and request.user.profile.role == 'ops':
        from api.models import UploadedFile
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        from django.conf import settings
        import os
        
        files = request.FILES.getlist('file')
        uploaded_files = []
        
        for file in files:
            try:
                # Save the file to the storage
                file_path = default_storage.save(
                    os.path.join('uploads', file.name),
                    ContentFile(file.read())
                )
                
                # Create the UploadedFile record
                uploaded_file = UploadedFile.objects.create(
                    file=file_path,
                    uploaded_by=request.user,
                    original_filename=file.name
                )
                uploaded_files.append(uploaded_file)
                
            except Exception as e:
                messages.error(request, f'Error uploading {file.name}: {str(e)}')
        
        if uploaded_files:
            messages.success(request, f'Successfully uploaded {len(uploaded_files)} file(s)')
        
        return redirect('admin_dashboard')
    
    return redirect('dashboard')

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@require_http_methods(["POST", "GET"])
@csrf_exempt
def logout_view(request):
    """Handle user logout.
    
    This view handles both session-based and JWT-based logout.
    For JWT, it clears the tokens from both client and server-side storage.
    """
    response = redirect('home')
    
    # Clear session data
    if hasattr(request, 'session'):
        request.session.flush()
    
    # Clear JWT tokens from cookies
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    
    # Log the user out using Django's auth system
    logout(request)
    
    # If it's an AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'redirect': '/'})
    
    return response

def profile_view(request):
    """Display and update user profile."""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        # Handle profile updates here if needed
        pass
    
    return render(request, 'profile.html', {
        'user': request.user,
    })

@login_required(login_url='/login/')
def download_file_view(request, file_id):
    """Redirect to the API download endpoint with a secure token."""
    from django.core.signing import TimestampSigner
    from django.shortcuts import redirect
    from django.utils.crypto import get_random_string
    from api.models import UploadedFile
    
    try:
        # Get the file
        file_obj = UploadedFile.objects.get(id=file_id)
        
        # All authenticated users can download any file
        # No additional permission check needed beyond authentication
        
        # Create a secure, time-limited download token
        signer = TimestampSigner()
        token = signer.sign(f"{file_obj.id}:{get_random_string(32)}")
        
        # Build the download URL without the trailing slash
        download_url = f'/api/download/{token}'
        return redirect(download_url)
        
    except UploadedFile.DoesNotExist:
        raise Http404("File not found")
    except Exception as e:
        # Log the error
        print(f"Download error: {str(e)}")
        raise Http404("Error processing download")
