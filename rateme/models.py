from django.db import models
from django.contrib.auth.models import User


class RatingCard(models.Model):
    title = models.CharField(max_length=200, unique=True)
    url = models.CharField(max_length=2047, null=True, blank=True, unique=True) # needs to be validated
    text = models.CharField(max_length=1000, null=True, blank=True, unique=True)
    # todo: add picture field, add many-to-many relationship for tags.
    def __str__(self):
        return self.title

RATING_CHOICES= [
    ('completely not interested', 'Completely Not Interested'),
    ('not interested', 'Not Interested'),
    ('neutral', 'Neutral'),
    ('interested', 'Interested'),
    ('very interested', 'Very Interested'),
    ]

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.CharField(max_length=120, choices=RATING_CHOICES)
    rating_card = models.ForeignKey(RatingCard, on_delete=models.CASCADE)
    def __str__(self):
        return self.user.get_username() + " is " + self.rating + " in " + self.rating_card.title

    class Meta:
        unique_together = ["user", "rating_card"]

class Tags(models.Model):
    rating_card = models.ForeignKey(RatingCard, on_delete=models.CASCADE)
