from flask import render_template, flash, redirect, url_for, request
from . import details
from .forms import RateForm, PostForm
from flask_login import current_user, login_required
from app import db
from numpy import mean
from random import sample

@details.route('/film_details/?<string:movie_id>', methods=['POST', 'GET'])
def film_details(movie_id):
    form = RateForm(request.form)
    postform = PostForm(request.form)
    id = int(movie_id)
    movies_db = db.movies
    cur_movie = movies_db.find_one({'movie_id': id})
    movie_name = cur_movie['movie_name']
    movie_type = cur_movie['movie_type']
    actor = cur_movie['actor']
    director = cur_movie['director']
    film_description = cur_movie['description']
    issue_date = cur_movie['issue_date']
    similar_movies = []
    for x in db.movies.find({'movie_type': movie_type}):
        similar_movies.append({'movie_name': x['movie_name'], 'movie_id': x['movie_id']})
    if len(similar_movies) > 3:
        similar_movies = sample(similar_movies, 3)
    comments = []
    rates = []
    for x in db.comments.find({'movie_id': id}):
        av = db.users.find_one({'username': x['username']})
        x['avatar'] = av['avatar']
        rates.append(x['ratings'])
        try:
            if x['username'] not in av['move_comment']:
                comments.append(x)
        except:
            comments.append(x)
    rates.append(db.ratings.find_one({'movie_id': id})['ratings'])
    try:
        rates.pop()
        new_rating = round(sum(rates)/len(rates), 1)
        db.ratings.update_one({'movie_id': id}, {"$set": {'ratings': new_rating}})
    except:
        pass
    rate = db.ratings.find_one({'movie_id': id})['ratings']
    if current_user.is_authenticated:
        cur_user = current_user.username
        re = db.users.find_one({'username': cur_user})
        username = re['username']
        gender = re['gender']
        avatar = re['avatar']
        email = re['email']
        wishlist_db = db.wishlists
        cur_wlist = wishlist_db.find_one({"username": cur_user})['wlist']
    else:
        username = ''
        gender = ''
        avatar = ''
        email = ''
        wishlist_db = None
        cur_wlist = []
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('guide.login'))
        else:
            ratings = form.rating.data
            text = postform.text.data
            if db.comments.find_one({'movie_id': id, 'username':username}) and text:
                db.comments.update_one({'movie_id': id, 'username':username}, {"$set": {'description': text}})
                flash("Comment Successfully")
            if db.comments.find_one({'movie_id': id, 'username':username}) and ratings != 'None':
                if ratings is not None:
                    ratings = float(ratings)
                    db.comments.update_one({'movie_id': id, 'username': username}, {"$set": {'ratings': ratings}})
            if not db.comments.find_one({'movie_id': id, 'username':username}) and text:
                db.comments.insert_one(
                    {'username': username, 'movie_name': movie_name, 'ratings': ratings, 'description': text, 'movie_id': id})
            if not db.comments.find_one({'movie_id': id, 'username': username}) and ratings != 'None':
                if ratings is not None:
                    ratings = float(ratings)
                    db.comments.insert_one({'username': username,'movie_name': movie_name, 'ratings': ratings, 'movie_id':id})
            try:
                description = re['personal_description']
                nickname = re['nickname']
                return render_template('/details/film_details.html', avatar=avatar, username=username, gender=gender,
                                       description=description, email=email, nickname=nickname, form=form, movie_name=movie_name, movie_type=movie_type, actor=actor,
                                       director = director, film_description=film_description, issue_date=issue_date,postform=postform, comments=comments, new_rating=rate, similar_movies=similar_movies, cur_wlist=cur_wlist, id=id, movies_db=movies_db)
            except:
                return render_template('/details/film_details.html', avatar=avatar, username=username, gender=gender,
                                       description=None, email=email, nickname=None, form=form, movie_name=movie_name, movie_type=movie_type, actor=actor,
                                       director = director, film_description=film_description, issue_date=issue_date,postform=postform, comments=comments, new_rating=rate, similar_movies=similar_movies, cur_wlist=cur_wlist, id=id, movies_db=movies_db)
    try:
        description = re['personal_description']
        nickname = re['nickname']
        return render_template('/details/film_details.html', avatar=avatar, username=username, gender=gender,
                                       description=description, email=email, nickname=nickname , form=form, current_user=current_user, movie_name=movie_name, movie_type=movie_type, actor=actor,
                                       director = director, film_description=film_description, issue_date=issue_date, comments=comments, postform=postform, new_rating=rate, similar_movies=similar_movies, cur_wlist=cur_wlist, id=id, movies_db=movies_db)
    except:
        return render_template('/details/film_details.html', avatar=avatar, username=username, gender=gender,
                               description=None, email=email, nickname=None, form=form,
                               current_user=current_user, movie_name=movie_name, movie_type=movie_type, actor=actor,
                               director=director, film_description=film_description, issue_date=issue_date,
                               comments=comments, postform=postform, new_rating=rate, similar_movies=similar_movies, cur_wlist=cur_wlist, id=id, movies_db=movies_db)

@details.route('/comment_delete/?<string:username>/?<string:movie_id>', methods=['POST', 'GET'])
def delete_comments(username, movie_id):
    try:
        move_comment = db.users.find_one({"username": username})['move_comment']
        move_comment.append(username)
        db.users.update_one({'username': username}, {"$set": {"move_comment": move_comment}})
    except:
        move_comment = [username]
        db.users.update_one({'username': username}, {"$set": {"move_comment": move_comment}})
    return redirect(url_for("details.film_details", movie_id=movie_id))