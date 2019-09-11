from django import forms

from .models import Rating, RatingCard

class RateForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']

class NewCardForm(forms.ModelForm):
    class Meta:
        model = RatingCard
        fields = ['title', 'url', 'text']
