
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class User(AbstractUser):
    pass


class UserFollows(models.Model):
    # null = False -> can't be created without this field
    # CASCADE -> delete element if one of these users disappear
    # related_name for the inverse relation
    user = models.ForeignKey(to=User, null=False, on_delete=models.CASCADE,
                             related_name='following')
    followed_user = models.ForeignKey(to=User, null=False, on_delete=models.CASCADE,
                                      related_name='followed_by')

    class Meta:
        unique_together = ("user", "followed_user")


class Ticket(models.Model):
    user = models.ForeignKey(to=User, null=False, on_delete=models.CASCADE)
    title = models.fields.CharField(max_length=128)
    description = models.fields.CharField(max_length=2048, blank=True)
    time_created = models.DateTimeField(auto_now=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.title}'


class Review(models.Model):
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[
                                              MinValueValidator(0),
                                              MaxValueValidator(5)])
    user = models.ForeignKey(to=User, null=False, on_delete=models.CASCADE)
    headline = models.fields.CharField(max_length=128)
    body = models.fields.CharField(max_length=8192, blank=True)
    time_created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.headline}'
