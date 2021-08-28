from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=250)
    starting_bid = models.IntegerField(default = 0)
    current_price = models.IntegerField(default = 0)
    image_url = models.CharField(max_length=300)
    category = models.CharField(max_length=50)
    published_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True) 
    
    def __str__(self):
        return f"{self.title} by {self.published_by}"
    
    class Meta:
        ordering = ['created_at']


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user_bid = models.IntegerField()
    bidded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.bidder} bid {self.user_bid} on the {self.item} at {self.bidded_at}"
    
    class Meta:
        ordering = ['bidded_at']  

class Comment(models.Model):
    author = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    text = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment {self.text} by {self.author}"

    class Meta:
        ordering = ['created_on']

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Listing, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bookmarks of {self.user}: {self.items}"

    class Meta:
        ordering = ['added_on']
