from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model
from allauth.account.utils import perform_login
from allauth.socialaccount.models import SocialAccount

class AutoActivateSocialAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return
            
        email = sociallogin.user.email
        if not email:
            return
            
        User = get_user_model()
        
        try:
            user = User.objects.get(email=email)
            
            if not user.is_active:
                user.is_active = True
                user.save()
                
            sociallogin.connect(request, user)
            
            perform_login(request, user, 'allauth.account.auth_backends.AuthenticationBackend')
            
        except User.DoesNotExist:
            sociallogin.user.is_active = True
            
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.is_active = True
        user.save()
        return user
    
    def delete_user(self, request, user):
        SocialAccount.objects.filter(user=user).delete()
        user.delete()
        
class CustomAccountAdapter(DefaultAccountAdapter):
    def delete_user(self, request, user):
        SocialAccount.objects.filter(user=user).delete()
        return super().delete_user(request, user)
    
    
    