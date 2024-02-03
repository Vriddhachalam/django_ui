# dbt/users/management/commands/login_user.py
from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate, login
from django.test.client import RequestFactory

class Command(BaseCommand):
    help = 'Log in a user using username and password'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='User username')
        parser.add_argument('password', type=str, help='User password')

    def handle(self, *args, **options):
        # Use RequestFactory to create a request object with session support
        request_factory = RequestFactory()
        request = request_factory.get('/favicon.ico', HTTP_COOKIE='')  # Include an empty HTTP_COOKIE to enable session support

        # Retrieve username and password from command line arguments
        username = options['username']
        password = options['password']
        print(f"Attempting to log in user with username '{username}' and password '{password}'")
        
        # Authenticate the user
        user = authenticate(request=request, username=username, password=password)
        print(f"User after authenticating is: '{user}'")
        if user is not None:
            # Log in the user
            login(request, user)
            self.stdout.write(self.style.SUCCESS(f"User '{username}' logged in successfully."))
        else:
            self.stdout.write(self.style.ERROR(f"Failed to log in user '{username}'."))
