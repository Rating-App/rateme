from django.core.management.base import BaseCommand, CommandError
from rateme.models import RatingCard
import os

class Command(BaseCommand):
    help = 'Import rating card data'

    def handle(self, *args, **options):
        movies_path = os.path.dirname(os.path.realpath(__file__)) + "/../../../data/ml-latest-small/movies.csv"

        movies_file = open(movies_path, 'r')
        print("Importing movies...")
        i = 0
        for movie in movies_file:
            if i > 0:
                movie_data = movie.split(",")
                ratingCard = RatingCard()
                ratingCard.title = movie_data[1]
                ratingCard.save()
                print(movie_data)
                print(str(i) + "/100")
                if i > 100: # temporary, would need to import all I guess
                    break
            i = i + 1

        movies_file.close()

        #print("Hello world")
        #for poll_id in options['poll_ids']:
        #    try:
        #        poll = Poll.objects.get(pk=poll_id)
        #    except Poll.DoesNotExist:
        #        raise CommandError('Poll "%s" does not exist' % poll_id)

        #    poll.opened = False
        #    poll.save()

        #    self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))
