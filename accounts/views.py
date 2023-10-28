from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView

from tweets import models as tweet_models

from . import models
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
    model = tweet_models.Tweet
    template_name = "accounts/user_profile.html"
    context_object_name = "tweets"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ユーザー名と一致するユーザーのツイートのみを取得
        context["tweets"] = (
            tweet_models.Tweet.objects.select_related("user")
            .filter(user__username=self.kwargs["username"])
            .order_by("-created_at")
        )
        context["username"] = self.kwargs["username"]
        context["following"] = models.FriendShip.objects.filter(from_user__username=self.kwargs["username"]).count()
        context["follower"] = models.FriendShip.objects.filter(to_user__username=self.kwargs["username"]).count()
        context["already_following"] = (
            models.FriendShip.objects.filter(
                from_user=self.request.user, to_user__username=self.kwargs["username"]
            ).count()
            > 0
        )
        return context


class FollowView(LoginRequiredMixin, CreateView):
    model = models.FriendShip
    fields = []
    success_url = reverse_lazy(settings.HOME_URL)

    def form_valid(self, form):
        form.instance.from_user = self.request.user
        form.instance.to_user = get_object_or_404(models.User, username=self.kwargs["username"])
        if form.instance.from_user == form.instance.to_user:
            return HttpResponseBadRequest("自分自身はフォローできません。")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(settings.HOME_URL)


class UnFollowView(LoginRequiredMixin, DeleteView):
    model = models.FriendShip
    success_url = reverse_lazy(settings.HOME_URL)

    def get_object(self, queryset=None):
        return get_object_or_404(
            models.FriendShip, from_user=self.request.user, to_user__username=self.kwargs["username"]
        )

    def get_success_url(self):
        return reverse_lazy(settings.HOME_URL)


class FollowingListView(ListView):
    model = models.FriendShip
    template_name = "accounts/following_list.html"
    context_object_name = "followings"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["username"] = self.kwargs["username"]
        return context

    def get_queryset(self):
        return models.User.objects.filter(
            id__in=(
                models.FriendShip.objects.values_list("to_user").filter(from_user__username=self.kwargs["username"])
            )
        )


class FollowerListView(ListView):
    model = models.FriendShip
    template_name = "accounts/follower_list.html"
    context_object_name = "followers"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["username"] = self.kwargs["username"]
        return context

    def get_queryset(self):
        return models.User.objects.filter(
            id__in=(
                models.FriendShip.objects.values_list("from_user").filter(to_user__username=self.kwargs["username"])
            )
        )
