#!/bin/bash

cd data
wget http://files.grouplens.org/datasets/movielens/ml-latest-small.zip
unzip ml-latest-small.zip
cd ..
python3 manage.py import_cards
python3 manage.py import_ratings

