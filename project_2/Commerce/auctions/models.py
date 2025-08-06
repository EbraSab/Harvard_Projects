from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):

    seller = models.ForeignKey(User, related_name="seller", on_delete=models.CASCADE)
    title = models.CharField(max_length=40)
    description = models.TextField()
    imgURL = models.URLField(default="https://www.svgrepo.com/show/340721/no-image.svg", blank=False)
    post_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    watchlist = models.ManyToManyField(User, related_name="watchlist", blank=True)

    starting_bid = models.ForeignKey('Bid', related_name="starting_bid", on_delete=models.CASCADE)

    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('fashion', 'Fashion'),
        ('home', 'Home & Garden'),
        ('toys', 'Toys'),
        ('books', 'Books'),
        ('other', 'Other')
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', blank=True)

    def __str__(self):
        return self.title


class Bid(models.Model):

    bid = models.FloatField(default=0)
    buyer = models.ForeignKey(User, related_name="buyer", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.bid} by {self.buyer}"


class Comment(models.Model):

    writer = models.ForeignKey(User, related_name="writer", on_delete=models.CASCADE)
    content = models.TextField()
    com_date = models.DateTimeField(auto_now_add=True)
    listing = models.ForeignKey(Listing, related_name="comment", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.content} | by {self.writer}"