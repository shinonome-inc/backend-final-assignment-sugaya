import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Tweet

User = get_user_model()


class TestHomeView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpassword")
        self.client.login(username="tester", password="testpassword")
        self.url = reverse(settings.HOME_URL)
        tweet_data = {
            "content": "test tweet",
        }
        response = self.client.post(reverse("tweets:create"), tweet_data)
        self.assertRedirects(
            response,
            reverse(settings.HOME_URL),
            status_code=302,
            target_status_code=200,
        )

    def test_success_get(self):
        response = self.client.get(reverse(settings.HOME_URL))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/home.html")
        # context内に含まれるTweetが、DBに登録されたTweetと同一か確認
        expected_tweet = Tweet.objects.all()
        actual_tweet = response.context["tweets"]
        self.assertQuerysetEqual(actual_tweet, expected_tweet)


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpassword")
        self.client.login(username="tester", password="testpassword")
        self.url = reverse(settings.TWEET_CREATE_URL)

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_success_post(self):
        content_data = "test tweet" + str(time.time())
        tweet_data = {
            "content": content_data,
        }
        response = self.client.post(self.url, tweet_data)
        self.assertRedirects(
            response,
            reverse(settings.HOME_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertEqual(Tweet.objects.filter(content=content_data).count(), 1)

    def test_failure_post_with_empty_content(self):
        content_data = ""
        tweet_data = {
            "content": content_data,
        }
        response = self.client.post(self.url, tweet_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(form.errors["content"], ["このフィールドは必須です。"])
        self.assertEqual(Tweet.objects.filter(content=content_data).count(), 0)

    def test_failure_post_with_too_long_content(self):
        content_data = "a" * 141
        tweet_data = {
            "content": content_data,
        }
        response = self.client.post(self.url, tweet_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(form.errors["content"], ["この値は 140 文字以下でなければなりません( 141 文字になっています)。"])
        self.assertEqual(Tweet.objects.filter(content=content_data).count(), 0)


class TestTweetDetailView(TestCase):
    def test_success_get(self):
        user = User.objects.create_user(username="tester", password="testpassword")
        self.client.login(username="tester", password="testpassword")
        content_data = "test tweet" + str(time.time())
        tweet = Tweet.objects.create(content=content_data, user=user)
        response = self.client.get(reverse("tweets:detail", kwargs={"pk": tweet.pk}))
        self.assertEqual(response.status_code, 200)
        actual_tweet = response.context["tweet"]
        self.assertEqual(tweet.pk, actual_tweet.pk)


class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpassword")
        self.client.login(username="tester", password="testpassword")
        content_data = "test tweet" + str(time.time())
        self.tweet = Tweet.objects.create(content=content_data, user=self.user)
        self.url = reverse("tweets:delete", kwargs={"pk": self.tweet.pk})

    def test_success_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(
            response,
            reverse(settings.HOME_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertEqual(Tweet.objects.filter(pk=self.tweet.pk).count(), 0)

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(reverse("tweets:delete", kwargs={"pk": 0}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Tweet.objects.filter(pk=0).count(), 0)

    def test_failure_post_with_incorrect_user(self):
        User.objects.create_user(username="tester2", password="testpassword")
        self.client.login(username="tester2", password="testpassword")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Tweet.objects.filter(pk=self.tweet.pk).count(), 1)


# class TestLikeView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_liked_tweet(self):


# class TestUnLikeView(TestCase):

#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_unliked_tweet(self):
