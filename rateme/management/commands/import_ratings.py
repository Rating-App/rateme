from django.core.management.base import BaseCommand, CommandError
from rateme.models import RatingCard, Rating
from django.db import IntegrityError
import os
from django.contrib.auth.models import User
import csv
from rateme.models import RATING_CHOICES

class Command(BaseCommand):
    help = 'Import rating card data'

    def handle(self, *args, **options):
        # TODO: refactor
        # - combine common parts of the functions
        # - first parse the string to parameters, then pass those around

        path = os.path.dirname(os.path.realpath(__file__))

        # Users and their ratings (move to helper)
        ratings_path = path + "/../../../data/ml-latest/ratings.csv"

        with open(ratings_path, 'r') as ratings_file:
            print("Importing ratings...")
            parsed_file = csv.reader(ratings_file, delimiter=',', quotechar='|')
            i = 0
            for rating_data in parsed_file:
                if i > 0:
                    print(rating_data)
                    # TODO: check if the user was already created
                    # use get_or_create ?
                    user, created = User.objects.get_or_create(username=rating_data[0])
                    if created:
                        user.set_password("1")
                        user.save()

                    rating = Rating()
                    rating.user = user
                    rating.rating = RATING_CHOICES[int(rating_data[2][:-2])-1][0]
                    try:
                        rating.rating_card = RatingCard.objects.get(card_id = rating_data[1])
                        try:
                            rating.save()
                        except IntegrityError:
                            print("already exists")
                    except RatingCard.DoesNotExist:
                        print("rating card does not exist")
                    print(str(i))
                i += 1
