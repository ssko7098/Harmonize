from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect
from django.http import HttpResponseRedirect

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Get the email from the social login data
        email = sociallogin.account.extra_data.get('email')

        if email:
            User = get_user_model()
            try:
                # Check if a user with this email already exists
                existing_user = User.objects.get(email=email)

                # If the social account is not already connected, link it to the existing user
                if not SocialAccount.objects.filter(user=existing_user, provider=sociallogin.account.provider).exists():
                    sociallogin.connect(request, existing_user)

                # Get the correct backend for the social account (Google in this case)
                backend = 'allauth.account.auth_backends.AuthenticationBackend'

                # Manually log in the user after the social account is connected, with the correct backend
                login(request, existing_user, backend=backend)

                # Redirect the user to the home page immediately after login
                return HttpResponseRedirect('/')  # <-- Force redirect here

            except User.DoesNotExist:
                # If the user does not exist, proceed as usual
                pass

    def get_login_redirect_url(self, request):
        # Redirect users to the home page after login
        return '/'
