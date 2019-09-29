from django.core.management.base import BaseCommand, CommandError
from rateme.models import RatingCard, Recommendation
from django.db import IntegrityError
from django.contrib.auth.models import User

import numpy as np
from scipy.sparse import csc_matrix
from sparsesvd import sparsesvd
import psycopg2
import time
import sys
import matplotlib.pyplot as plt


class Command(BaseCommand):
    help = 'Makes recommendations'

    def handle(self, *args, **options):
        conn = psycopg2.connect("dbname='rateme' user='rateme' host='localhost' password='1'")

        cur = conn.cursor()

        users = {}
        users_back = []
        cards = {}
        cards_back = []

        # matrix to store result in
        M = csc_matrix((1, 1)).toarray()

        cur.execute("""SELECT * from rateme_rating""")
        rows = cur.fetchall()

        for row in rows:
            # (66870, 432, 'neutral', 1545)
            rating_id, user_id, rating_val, card_id = row

            user_id = int(user_id)
            card_id = int(card_id)
            
            if user_id not in users:
                users[user_id] = len(users)
                users_back.append(user_id)
            
            if card_id not in cards:
                cards[card_id] = len(cards)
                cards_back.append(card_id)


        num_users = len(users)
        num_cards = len(cards)


        def todata(rating_val):
            if rating_val == "completely not interested":
                return -2
            elif rating_val == "not interested":
                return -1
            elif rating_val == "neutral":
                return 0
            elif rating_val == "interested":
                return 1
            elif rating_val == "very interested":
                return 2
            else:
                print("ERROR")
                return 0

        # Rows: users, Columns: cards
        # I.e. users x cards

        mrow = []
        mcol = []
        data = []

        for row in rows:
            # (66870, 432, 'neutral', 1545)
            rating_id, user_id, rating_val, card_id = row

            mrow.append(users[user_id])
            mcol.append(cards[card_id])
            data.append(todata(rating_val))

#            del rows # free some memory
        print("There are " + str(num_users) + " users, " +\
               str(num_cards) + " cards and " + str(len(data)) + " votes. Sparseness is " +\
               str(len(data)/(num_users*num_cards)*100) + "%")

        def get_sing_vals_rank(matrix):
            ut, s, vt = sparsesvd(csc_matrix(matrix), 100) # TODO: replace 500

            return s

        observed_padded = csc_matrix((data, (mrow, mcol)), shape=(num_users, num_cards))
        predicted = np.load('data/recommendations.npy')
        
        plt.plot(get_sing_vals_rank(observed_padded))
        plt.plot(get_sing_vals_rank(predicted))
        plt.title("Singular Values")
        plt.xlabel("singular values")
        plt.ylabel("importance")
        plt.legend(['padded','predicteed'])
        plt.savefig("rateme/static/predicted_observed_sv")

        plt.close()

        plt.imshow(observed_padded.toarray(), cmap='gist_rainbow')
        plt.title("Ratings")
        plt.xlabel("cards")
        plt.ylabel("users")
        plt.savefig("rateme/static/observed")
        
        plt.close()
        
        plt.imshow(predicted, cmap='gist_rainbow')
        plt.title("Predicted Ratings")
        plt.xlabel("cards")
        plt.ylabel("users")
        plt.savefig("rateme/static/predicted")
