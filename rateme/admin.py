from django.contrib import admin

# Register your models here.
from .models import Rating, RatingCard, Tag

admin.site.register(Rating)
admin.site.register(RatingCard)
admin.site.register(Tag)
