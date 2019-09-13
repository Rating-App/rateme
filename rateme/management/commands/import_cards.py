from django.core.management.base import BaseCommand, CommandError
from rateme.models import RatingCard, Rating
from django.db import IntegrityError
import os
from django.contrib.auth.models import User
import csv

class Command(BaseCommand):
    help = 'Import rating card data'

    def handle(self, *args, **options):
        # TODO: refactor
        # - combine common parts of the functions
        # - first parse the string to parameters, then pass those around

        path = os.path.dirname(os.path.realpath(__file__))

        # Movies (move to helper)
        movies_path = path + "/../../../data/ml-latest-small/movies.csv"

        with open(movies_path, 'r') as movies_file:
            print("Importing movies...")
            parsed_file = csv.reader(movies_file, delimiter=',', quotechar='|')
            i = 0
            for movie in parsed_file:
                if i > 0:
                    ratingCard = RatingCard()
                    if len(movie) > 3:
                        movie = [movie[0], ",".join(movie[1:-1]), movie[-1]]
                    title = movie[1]
                    if title[0] == "\"":
                        title = title[1:]
                    ratingCard.title = title
                    ratingCard.card_id = movie[0]
                    try:
                        ratingCard.save()
                    except IntegrityError:
                        print("already exists")
                    print(str(i))
                i += 1
