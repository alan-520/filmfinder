from . import wishlist

from flask import render_template, flash, redirect, url_for, request
from app import db
from flask_login import login_required, current_user
from collections import defaultdict

@wishlist.route('/wishlist/?<string:username>', methods=['GET', 'POST'])
@login_required
def wishlists(username):
    movieid_lists = db.wishlists.find_one({"username": username})['wlist']
    movie_db = db.movies

    movie_items = defaultdict(list)

    for i in movieid_lists:
        movie_info = movie_db.find_one({"movie_id": i})
        movie_names = movie_info["movie_name"]
        movie_types = movie_info["movie_type"]
        movie_directors = movie_info["director"]
        movie_ratings = db.ratings.find_one({"movie_id": i})["ratings"]
        movie_items[i].append(movie_names)
        movie_items[i].append(movie_types)
        movie_items[i].append(movie_directors)
        movie_items[i].append(movie_ratings)

    avatar = db.users.find_one({"username": username})['avatar']


    return render_template('/wishlist/wishlist.html', movie_items = movie_items,movieid_lists=movieid_lists, username=username, movie_db=movie_db, avatar=avatar)

@wishlist.route('/add/?<string:movie_id>')
def add(movie_id):
    r1 = db.wishlists.find_one({"username": current_user.username})["wlist"]
    movie_id = int(movie_id)
    if movie_id not in r1:
        r1.append(movie_id)
        db.wishlists.update_one({"username": current_user.username}, {"$set": {"wlist": r1}})
        flash("Successfully add to wish list!", category='info')
    else:
        pass
    return redirect(url_for('details.film_details', movie_id=movie_id))

@wishlist.route('/delete/?<string:movie_id>')
def delete(movie_id):
    r1 = db.wishlists.find_one({"username": current_user.username})["wlist"]
    movie_id = int(movie_id)
    if movie_id in r1:
        r1.remove(movie_id)
        db.wishlists.update_one({"username": current_user.username}, {"$set": {"wlist": r1}})
        flash("Successfully delete from wish list!", category='info')
    else:
        pass
    return redirect(url_for('wishlist.wishlists', username=current_user.username))

@wishlist.route('/wishlist_by_director/?<string:username>', methods=['GET', 'POST'])
@login_required
def wishlists_by_director(username):
    movieid_list = db.wishlists.find_one({"username": username})['wlist']
    movie_db = db.movies
    director_d = {}
    for i in movieid_list:
        directors = movie_db.find_one({'movie_id':i})["director"]
        director_d[i]= directors

    director_d2 = sorted(director_d.items(),key=lambda x:x[1])
    res=[i[0] for i in director_d2]

    movieid_lists =[]

    for x in res:
        r1=int(x)
        movieid_lists.append(r1)

    movie_items = defaultdict(list)

    for i in movieid_lists:
        movie_info = movie_db.find_one({"movie_id":i})
        movie_names= movie_info["movie_name"]
        movie_types = movie_info["movie_type"]
        movie_directors = movie_info["director"]
        movie_ratings = db.ratings.find_one({"movie_id": i})["ratings"]
        movie_items[i].append(movie_names)
        movie_items[i].append(movie_types)
        movie_items[i].append(movie_directors)
        movie_items[i].append(movie_ratings)

    avatar = db.users.find_one({"username": username})['avatar']
    return render_template('/wishlist/wishlist_by_director.html',movie_items = movie_items, movieid_lists=movieid_lists, username=username, movie_db=movie_db, avatar=avatar)

@wishlist.route('/wishlist_by_type/?<string:username>', methods=['GET', 'POST'])
@login_required
def wishlists_by_type(username):
    movieid_list = db.wishlists.find_one({"username": username})['wlist']
    movie_db = db.movies
    type_d = {}
    for i in movieid_list:
        types = movie_db.find_one({'movie_id': i})["movie_type"]
        type_d[i] = types.lower()

    type_d2 = sorted(type_d.items(), key=lambda x: x[1])
    res = [i[0] for i in type_d2]

    movieid_lists = []

    for y in res:
        r2 = int(y)
        movieid_lists.append(r2)

    movie_items = defaultdict(list)

    for i in movieid_lists:
        movie_info = movie_db.find_one({"movie_id": i})
        movie_names = movie_info["movie_name"]
        movie_types = movie_info["movie_type"]
        movie_directors = movie_info["director"]
        movie_ratings = db.ratings.find_one({"movie_id": i})["ratings"]
        movie_items[i].append(movie_names)
        movie_items[i].append(movie_types)
        movie_items[i].append(movie_directors)
        movie_items[i].append(movie_ratings)
    avatar = db.users.find_one({"username": username})['avatar']
    return render_template('/wishlist/wishlist_by_type.html', movie_items = movie_items,movieid_lists=movieid_lists, username=username, movie_db=movie_db, avatar=avatar)


@wishlist.route('/wishlist_by_ratings/?<string:username>', methods=['GET', 'POST'])
def wishlists_by_ratings(username):
    movieid_list = db.wishlists.find_one({"username": username})['wlist']
    movie_db=db.movies
    ratings_dict={}
    for z in movieid_list:
        ratings = db.ratings.find_one({"movie_id":z})['ratings']
        ratings_dict[z] = ratings


    ratings_d2 = sorted(ratings_dict.items(), key=lambda x: x[1], reverse=True)
    res = [a[0] for a in ratings_d2]

    movieid_lists = []

    for y in res:
        r2 = int(y)
        movieid_lists.append(r2)

    movie_items=defaultdict(list)

    for i in movieid_lists:
        movie_info = movie_db.find_one({"movie_id": i})
        movie_names= movie_info["movie_name"]
        movie_types = movie_info["movie_type"]
        movie_directors = movie_info["director"]
        movie_ratings = db.ratings.find_one({"movie_id": i})["ratings"]
        movie_items[i].append(movie_names)
        movie_items[i].append(movie_types)
        movie_items[i].append(movie_directors)
        movie_items[i].append(movie_ratings)
    avatar = db.users.find_one({"username": username})['avatar']
    return render_template('/wishlist/wishlist_by_ratings.html', movie_items = movie_items ,movieid_lists=movieid_lists, username=username, movie_db=movie_db, avatar=avatar)

