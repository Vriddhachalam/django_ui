from django.contrib import auth
from django.contrib.auth.middleware import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


class AutomaticUserLoginMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not AutomaticUserLoginMiddleware._is_user_authenticated(request):
            request.META['REMOTE_USER'] = 'admin'
            user = auth.authenticate(request)
            if user is None:
                return HttpResponseForbidden()

            request.user = user
            auth.login(request, user)

    @staticmethod
    def _is_user_authenticated(request):
        user = request.user
        return user and user.is_authenticated


class AuthenticationBackend(ModelBackend):

    def authenticate(self, request, p_username=None, password=None, **kwargs):

        # Get credentials from the query strings
        username = request.META.get('REMOTE_USER')
        # password = request.GET.get('password')
        print(f"-----------------------------------------------------------")
        print(f"username: {username}")
        # Check that the user can authenticate in the LDAP using its username and password
        if username is None:
            return None
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username)
            user.is_staff = True
            user.save()
        return user

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None