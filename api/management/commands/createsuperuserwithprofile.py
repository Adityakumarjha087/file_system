from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser with a profile'

    def add_arguments(self, parser):
        parser.add_argument('--username', help='Username for the superuser')
        parser.add_argument('--email', help='Email for the superuser')
        parser.add_argument('--password', help='Password for the superuser')
        parser.add_argument('--noinput', '--no-input', action='store_false', dest='interactive',
                          help='Tells Django to NOT prompt the user for input of any kind.')

    def handle(self, *args, **options):
        username = options.get('username')
        email = options.get('email')
        password = options.get('password')
        interactive = options.get('interactive')

        if interactive:
            # Interactive mode - prompt for input
            username = input('Username: ')
            email = input('Email: ')
            password = input('Password: ')
            
            # Confirm password
            while True:
                password_confirm = input('Password (again): ')
                if password == password_confirm:
                    break
                self.stdout.write(self.style.ERROR("Error: Your passwords didn't match."))
                password = input('Password: ')
        
        # Validate required fields
        if not username or not email or not password:
            raise ValueError('Username, email, and password are required')
        
        # Create the superuser with the provided details
        with transaction.atomic():
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                self.stdout.write(self.style.WARNING(f'User {username} already exists. Updating to superuser status.'))
                user.is_staff = True
                user.is_superuser = True
                user.set_password(password)
                user.save()
            else:
                # Create new superuser
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(self.style.SUCCESS(f'Created superuser: {username}'))
            
            # Ensure the user has an ops role
            profile = user.profile
            if profile.role != 'ops':
                profile.role = 'ops'
                profile.save()
                self.stdout.write(self.style.SUCCESS(f'Updated {username} profile with ops role'))
            
            self.stdout.write(self.style.SUCCESS('Superuser created/updated successfully!'))
