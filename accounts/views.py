from django.conf import settings
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from tweets import models

from .forms import SignupForm


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class UserProfileView(ListView):
    model = models.Tweet
    template_name = "accounts/user_profile.html"
    context_object_name = "tweets"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ユーザー名と一致するユーザーのツイートのみを取得
        context["tweets"] = (
            models.Tweet.objects.select_related("user")
            .filter(user__username=self.kwargs["username"])
            .order_by("-created_at")
        )
        return context
