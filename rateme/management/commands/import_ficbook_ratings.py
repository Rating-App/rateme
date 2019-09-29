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
        def collection2rating(name):
            if "рекомендую" in name.lower() or\
               "рекамендую" in name.lower() or\
               "мне интересно" in name.lower() or\
               "мне понрав" in name.lower() or\
               "мне нрав" in name.lower() or\
               "оху" in name.lower() or\
               "вдохновляют" in name.lower() or\
               "good stuff" in name.lower() or\
               "ахуе" in name.lower() or\
               "занят" in name.lower() or\
               "111" in name.lower() or\
               "!" in name.lower() or\
               "щедев" in name.lower() or\
               "любл" in name.lower() or\
               "любим" in name.lower() or\
               "само" in name.lower() or\
               "угар" in name.lower() or\
               "обязательно" in name.lower() or\
               "лучш" in name.lower():
                return "very interested"

            if "не интересно" in name.lower() or\
               "не понрав" in name.lower() or\
               "не нрав" in name.lower():
                return "not interested"

            if "интересно" in name.lower():
                return "very interested"

            if "фигня" in name.lower() or\
               "не пошло" in name.lower() or\
               "свалка" in name.lower() or\
               "лучше бы не" in name.lower():
                return "not interested"

            if "уныл" in name.lower() or\
               "полная хрень" in name.lower() or\
               "худш" in name.lower():
                return "completely not interested"

            if "бросил" in name.lower():
                return "neutral"

            return "interested"

        path = os.path.dirname(os.path.realpath(__file__))

        # Users and their ratings (move to helper)
        ratings_path = path + "/../../../../scrapy/ficbook/CollectionItem.csv"

        with open(ratings_path, 'r') as ratings_file:
            print("Importing ratings...")
            parsed_file = csv.reader(ratings_file, delimiter=',', quotechar='|')
            i = 0
            for rating_data in parsed_file:
                if i > 0:
                    print(rating_data)
                    # TODO: check if the user was already created
                    # use get_or_create ?
                    user, created = User.objects.get_or_create(username=rating_data[1])
                    if created:
                        user.set_password("1")
                        user.save()

                    rating = Rating()
                    rating.user = user
                    rating.rating = collection2rating(",".join(rating_data[2:-1]))
                    try:
                        rating.rating_card = RatingCard.objects.get(card_id = rating_data[0])
                        try:
                            rating.save()
                        except IntegrityError:
                            print("already exists")
                    except RatingCard.DoesNotExist:
                        print("rating card does not exist")
                    print(str(i))
                i += 1
