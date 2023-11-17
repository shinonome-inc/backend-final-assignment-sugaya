from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint


class User(AbstractUser):
    email = models.EmailField()


class FriendShip(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="from_user")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="to_user")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # 重複してフォローできない
            UniqueConstraint(fields=["from_user", "to_user"], name="unique_friendship"),
            # 自分自身はフォローできない
            CheckConstraint(check=~Q(from_user=F("to_user")), name="not_follow_myself"),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.from_user} -> {self.to_user}"
