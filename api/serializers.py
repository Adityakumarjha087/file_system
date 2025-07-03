from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Profile, UploadedFile

class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role')
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        # Set role if provided, otherwise it will use the default from the signal
        if 'role' in profile_data:
            user.profile.role = profile_data['role']
            user.profile.save()
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.profile.role
        }
        return data

class UploadedFileSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UploadedFile
        fields = ('id', 'original_filename', 'uploaded_by', 'uploaded_at', 'download_url')
        read_only_fields = ('uploaded_by', 'uploaded_at', 'download_url')
    
    def get_download_url(self, obj):
        request = self.context.get('request')
        if request is not None:
            from django.urls import reverse
            from django.utils.encoding import force_str
            from django.utils.http import urlsafe_base64_encode
            from django.utils.crypto import get_random_string
            from django.core.signing import TimestampSigner
            
            # Create a secure, time-limited download token
            signer = TimestampSigner()
            token = signer.sign(f"{obj.id}:{get_random_string(32)}")
            
            # Build the full URL for the download endpoint
            return f"{request.scheme}://{request.get_host()}/api/files/download/{token}/"
        return None

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    
    def validate_file(self, value):
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in UploadedFile.ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f'File type not supported. Allowed types: {", ".join(UploadedFile.ALLOWED_EXTENSIONS)}'
            )
        return value
