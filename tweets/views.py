from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from . import models


class HomeView(LoginRequiredMixin, ListView):
    model = models.Tweet
    template_name = "tweets/home.html"
    context_object_name = "tweet"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tweets"] = models.Tweet.objects.select_related("user").all().order_by("-created_at")
        return context


class TweetCreateView(LoginRequiredMixin, CreateView):
    model = models.Tweet
    fields = ("content",)
    template_name = "tweets/create.html"
    success_url = reverse_lazy(settings.HOME_URL)

    # ツイート主を設定
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TweetDetailView(DetailView):
    model = models.Tweet
    template_name = "tweets/detail.html"
    context_object_name = "tweet"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tweet"] = models.Tweet.objects.select_related("user").get(pk=self.kwargs["pk"])
        return context


class TweetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = models.Tweet
    template_name = "tweets/delete.html"
    success_url = reverse_lazy(settings.HOME_URL)
    context_object_name = "tweet"

    # userPassesTestMixinを使うと、test_funcを実装することで追加の条件を設定できる
    # 今回は、ツイート主のみ削除可能とする
    def test_func(self):
        try:
            self.tweet = models.Tweet.objects.select_related("user").get(pk=self.kwargs["pk"])
        except models.Tweet.DoesNotExist:
            return Http404
        return self.tweet.user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tweet"] = self.tweet
        return context
