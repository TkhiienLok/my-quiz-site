import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string

from accounts.forms import SignUpForm, UserProfileForm
from accounts.models import UserProfile
from accounts.tokens import account_activation_token
from quiz.models import Score

# Get an instance of a logger
logger = logging.getLogger(__name__)


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                messages.error(request, """Your account is inactive.
                Please, activate it by following the link in the letter, we\'ve sent to your email address """, extra_tags='login')
                return HttpResponseRedirect('/accounts/login/')
        else:
            logger.info('Someone tried to login and failed.')
            logger.info('They used username: {} and password: {}'.format(username, password))
            messages.error(request, 'Username or password is not correct',  extra_tags='login')
            return HttpResponseRedirect('/accounts/login/')
    else:
        return render(request, 'accounts/login.html', {})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.refresh_from_db()  # load the profile instance created by the signal
            user.userprofile.birth_date = form.cleaned_data.get('birth_date')
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your Lok-Django-Blog Account'
            message = render_to_string('accounts/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return render(request, 'accounts/account_activation_sent.html')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def account_activation_sent(request):
    return render(request, 'accounts/account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.userprofile.email_confirmed = True
        user.save()
        login(request, user)
        return render(request, 'accounts/successful_signup.html')
    else:
        return render(request, 'accounts/account_activation_invalid.html')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context["user"] = self.request.user
        context["scores"] = Score.objects.filter(student=self.request.user).count()
        return context


class GuestProfileView(TemplateView):
    template_name = "accounts/guest_profile_view.html"

    def get_context_data(self, **kwargs):
        context = super(GuestProfileView, self).get_context_data(**kwargs)
        viewed_user = get_object_or_404(User, pk=kwargs.get('pk'))
        context['viewed_user'] = viewed_user
        context["scores"] = Score.objects.filter(student=self.request.user).count()
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    template_name = "accounts/edit_profile.html"
    form_class = UserProfileForm

    def get_object(self, *args, **kwargs):
        user = self.request.user
        try:
            return user.userprofile
        except UserProfile.DoesNotExist:
            return UserProfile.objects.create(user=user)

    def get_success_url(self, *args, **kwargs):
        return reverse("accounts:view-profile-url")


class ChangePasswordCompleteView(TemplateView):
    template_name = 'accounts/change_password_complete.html'
