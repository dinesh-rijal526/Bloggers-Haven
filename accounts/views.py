from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str  
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.db.models import Count, Q
from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from core.models import Article
from .forms import UserProfileForm
from .models import Profile

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Account not activated. Please check your email.")
        else:
            User = get_user_model()
            try:
                user = User.objects.get(username=username)
                if user.check_password(password) and not user.is_active:
                    messages.error(request, "Account not activated. Please check your email.")
                else:
                    messages.error(request, "Invalid username or password")
            except User.DoesNotExist:
                messages.error(request, "Invalid username or password")
        
        return render(request, 'auth/login.html')
    
    return render(request, 'auth/login.html')

def register_page(request):
    if request.method == 'POST':
        data = request.POST
        name = data.get('name')
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'auth/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return render(request, 'auth/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, 'auth/register.html')
        
        user = None  
        try:
            user = User.objects.create_user(
                first_name=name,
                username=username,
                email=email,
                password=password,
                is_active=False
            )
            
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_url = reverse('activate', kwargs={'uidb64': uid, 'token': token})
            full_activation_url = request.build_absolute_uri(activation_url)
            print("Generated activation URL:", full_activation_url)

            mail_subject = 'Activate your account'
            
            message = render_to_string('email/verification_email.html', {
                'user': user,
                'activation_url': full_activation_url  
            })
            
            send_mail(
                mail_subject,
                '',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
                html_message=message
            )
            
            return redirect('verification_sent')
                
        except Exception as e:
            if user is not None and hasattr(user, 'pk') and user.pk is not None:
                user.delete()
            messages.error(request, f"Registration failed: {str(e)}")
            return render(request, 'auth/register.html')
    
    return render(request, 'auth/register.html')

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        
        uid = int(uid)
        
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        print(f"Activation error: {str(e)}")
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated! You can now log in.')
        return redirect('login_page')
    else:
        messages.error(request, 'Activation link is invalid or has expired!')
        return redirect('register_page')

def verification_sent(request):
    return render(request, 'email/verification_sent.html')

def logout_page(request):
    logout(request)
    return redirect('login_page')



def reset_password_view(request):
    template_name = 'reset_password/password_reset.html'
    email_template_name = 'reset_password/password_reset_email.html'
    subject_template_name = 'reset_password/password_reset_subject.txt'
    html_email_template_name = 'reset_password/password_reset_email.html' 
    
    success_message = _(
        "We've emailed you instructions for setting your password, "
        "if an account exists with the email you entered. You should receive them shortly."
        " If you don't receive an email, "
        "please make sure you've entered the address you registered with, and check your spam folder."
    )
    
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            protocol = 'https' if request.is_secure() else 'http'
            domain = request.get_host()
            
            form.save(
                request=request,
                email_template_name=email_template_name,
                subject_template_name=subject_template_name,
                html_email_template_name=html_email_template_name,
                extra_email_context={
                    'protocol': protocol,
                    'domain': domain,
                }
            )
            messages.success(request, success_message)
            return redirect(reverse('home'))
    else:
        form = PasswordResetForm()
    
    context = {
        'form': form,
        'title': _("Password reset")
    }
    return render(request, template_name, context)

@login_required
def profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    
    user_articles = Article.objects.filter(author=request.user).order_by('-published_at')
    
    article_stats = user_articles.aggregate(
        total=Count('id'),
        published=Count('id', filter=Q(status='published')),
        draft=Count('id', filter=Q(status='draft'))
    )
    
    return render(request, 'auth/profile.html', {
        'profile': profile,
        'user_articles': user_articles,
        'article_stats': article_stats
    })



@login_required
def profile_update(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    
    if request.method == 'POST':
        form = UserProfileForm(
            request.POST, 
            request.FILES, 
            instance=profile,
            user_instance=user  
        )
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile, user_instance=user)
    
    return render(request, 'auth/profile_update.html', {
        'form': form,
        'profile': profile
    })

@login_required
def toggle_dark_mode(request):
    if request.method == 'POST':
        profile = request.user.profile
        profile.dark_mode = not profile.dark_mode
        profile.save()
        return JsonResponse({'dark_mode': profile.dark_mode})
    return JsonResponse({'error': 'Invalid request'}, status=400)