from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views

app_name = 'api'

urlpatterns = [
    # Authentication
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    
    # User operations
    path('user/', views.UserInfoView.as_view(), name='user-info'),
    
    # File operations
    path('upload/', views.FileUploadView.as_view(), name='file-upload'),
    path('files/', views.FileListView.as_view(), name='file-list'),
    path('download/<str:token>/', views.FileDownloadView.as_view(), name='file-download'),
]
