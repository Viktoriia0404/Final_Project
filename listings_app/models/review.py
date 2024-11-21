from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from .listing import Listing


class Review(models.Model):
    listing = models.ForeignKey(Listing,
                                on_delete=models.DO_NOTHING, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='reviews')
    rating = models.IntegerField(choices=[
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.listing.title} ({self.rating})"
