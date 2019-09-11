from django.contrib import admin

# Register your models here.
from .models import Rating, RatingCard

admin.site.register(Rating)
admin.site.register(RatingCard)
