from django.db import models

from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    friends = models.ManyToManyField(
        to='self',
        blank=True,
        related_name='friends'
    )
    def friends_amount(self):
        return self.friends.count()
    