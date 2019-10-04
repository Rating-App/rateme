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
            ut, s, vt = sparsesvd(csc_matrix(matrix), 100)

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

        observed_padded = observed_padded.toarray()
        
        # fix aspect ratio
        m = int(1.5*min(observed_padded.shape))
        x = min(observed_padded.shape[0], m)
        y = min(observed_padded.shape[1], m)

        plt.imshow(observed_padded[:x,:y], vmin=-2, vmax=2)
        plt.colorbar()
        plt.title("Ratings")
        plt.xlabel("cards")
        plt.ylabel("users")
        plt.savefig("rateme/static/observed")
        
        plt.close()
        
        plt.imshow(predicted[:x,:y], vmin=-2, vmax=2)
        plt.colorbar()
        plt.title("Predicted Ratings")
        plt.xlabel("cards")
        plt.ylabel("users")
        plt.savefig("rateme/static/predicted")

        plt.close()

        m = 10
        alpha = 0.4

        _, bins, _ = plt.hist(observed_padded[0,:][observed_padded[0,:] != 0][:], bins=100, alpha=alpha)
        for i in range(1, m):
            _ = plt.hist(observed_padded[i,:][observed_padded[i,:] != 0][:], bins=bins, alpha=alpha)
        plt.title("Observed User Distribution")
        plt.savefig("rateme/static/user_dist_o")

        plt.close()

        _, bins, _ = plt.hist(observed_padded[:,0][observed_padded[:,0] != 0][:], bins=100, alpha=alpha)
        for i in range(1, m):
            _ = plt.hist(observed_padded[:,i][observed_padded[:,i] != 0][:], bins=bins, alpha=alpha)
        plt.title("Observed Card Distribution")
        plt.savefig("rateme/static/card_dist_o")

        plt.close()

        _, bins, _ = plt.hist(predicted[0,:], bins=100, alpha=alpha)
        for i in range(1, m):
            _ = plt.hist(predicted[i,:], bins=bins, alpha=alpha)
        plt.title("Predicted User Distribution")
        plt.savefig("rateme/static/user_dist_p")

        plt.close()

        _, bins, _ = plt.hist(predicted[:,0], bins=100, alpha=alpha)
        for i in range(1, m):
            _ = plt.hist(predicted[:,i], bins=bins, alpha=alpha)
        plt.title("Predicted Card Distribution")
        plt.savefig("rateme/static/card_dist_p")

