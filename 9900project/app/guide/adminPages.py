from . import guide
from flask import render_template, flash, redirect, url_for, request
from app import secure
from app import db as pydb
#from app.MongoFunction import get_list_of_complete_username
from app.models import User
from .forms import RegisterForm, LoginForm, PasswordResetForm, ResetPasswordForm, ProfileForm
from flask_login import login_required, login_user, current_user, logout_user
from .email import send_reset_password_mail
from werkzeug.utils import secure_filename
import os
import requests, re
from app.recommend_system import Recommendation_System
import pandas as pd

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@guide.route('/signup', methods=['GET', 'POST'])
def signup():
    global gender
    form = RegisterForm(request.form)
    if request.method == 'POST':
        image = request.files['file']
        if image.filename == '':
            flash('Please choose your avatar!', category='danger')
            return render_template('/guide/signup.html', form=form)
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join('app', 'static', 'filedata', filename))
            avatar = '/static/filedata/' + filename
        username = form.username.data
        user = pydb.users.find_one({'username': username})
        if user:
            flash('Username has been used, Please try again!', category='danger')
            return render_template('/guide/signup.html', form=form)
        email = form.email.data
        emailname = pydb.users.find_one({'email': email})
        if emailname:
            flash('Email has been used, Please try again!', category='danger')
            return render_template('/guide/signup.html', form=form)
        if request.form['submit'] == 'M':
            gender = "Male"
        elif request.form['submit'] == 'F':
            gender = "Female"
        password = form.password.data
        confirm_password = form.confirm.data
        if confirm_password != password:
            flash('The second confirmed password is inconsistent with the first!', category='danger')
            return render_template('/guide/signup.html', form=form)
        password = str(secure.generate_password_hash(password))
        pydb.users.insert({'avatar': avatar, 'username': username, 'password': password, 'email': email, 'gender': gender})
        flash('Well done! Sign up successfully!', category='success')
        return redirect(url_for('guide.login'))
    return render_template('/guide/signup.html', form=form)


"""
Page:        Login
Description: Login to access world map
API:         http://host/guide/login
methods:     GET AND POST
ref.data:    username, password ...
"""
@guide.route('/guide', methods=['GET', 'POST'])
def login():
    if not current_user.is_authenticated:
        form = LoginForm(request.form)
        if request.method == 'POST':
            username = form.username.data
            password = form.password.data
            rem = form.rem.data
            user = pydb.users.find_one({'username': username})
            if user and secure.check_password_hash(user['password'].replace("b'", "").replace("'", ""), password):
                user_obj = User(user['username'])
                login_user(user_obj, remember=rem)
                return redirect(url_for('search.film_search'))
            else:
                flash('User does not exist or password is incorrect', category='danger')
        return render_template('/guide/login.html', form=form)
    else:
        return redirect(url_for('search.film_search'))


"""
Page:        logout
Description: logout to homepage
API:         http://host/guide/logout
methods:     none
ref.data:    none
"""
@guide.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('search.film_search'))

"""
Page:        Send reset password email
Description: Type email address then we will send email to guide them to reset password page
API:         http://host/guide/password_reset
methods:     GET AND POST
ref.data:    username, email
"""
@guide.route('/password_reset', methods=['GET', 'POST'])
def password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('search.film_search'))
    form = PasswordResetForm(request.form)
    if request.method == 'POST':
        email = form.email.data
        user = pydb.users.find_one({'email': email})
        user_obj = User(user['username'])
        token = user_obj.generate_reset_password()
        print(token)
        send_reset_password_mail(user_obj, token)
        flash('Password reset mail has been sent, please check your email.', category='info')
    return render_template('/guide/password_reset.html', form=form)


"""
Page:        Reset password
Description: Help users to reset new password if they forget
API:         http://host/guide/reset_password/<token>
methods:     GET AND POST
ref.data:    username, password
"""
@guide.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('search.file_search'))
    form = ResetPasswordForm(request.form)
    if request.method == 'POST':
        user = User.check_reset_password(token)
        if user:
            pydb.users.update({'username': user['username']},
                              {'$set': {'password': str(secure.generate_password_hash(form.password.data))}})
            flash('Your password has been reset, you can login now.', category='info')
            return redirect(url_for('guide.login'))
        else:
            flash('The user does not exist', category='info')
            return redirect(url_for('guide.login'))
    return render_template('/guide/password_reset_commit.html', form=form)


'''@guide.route('/film_search', methods=['GET', 'POST'])
def film_search():
    cur_user = current_user.username
    re = pydb.users.find_one({'username': cur_user})
    username = re['username']
    gender = re['gender']
    avatar = re['avatar']
    email = re['email']
    try:
        description = re['personal_description']
        nickname = re['nickname']
        return render_template('/guide/film_search.html', avatar=avatar, username=username, gender=gender, description=description, email=email, nickname=nickname)
    except:
        return render_template('/guide/film_search.html', avatar=avatar, username=username, gender=gender,
                               description=None, email=email, nickname=None)'''

@guide.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    global gender
    form = ProfileForm(request.form)
    if request.method == 'POST':
        image = request.files['file']
        username = current_user.username
        nickname = form.nickname.data
        if nickname:
            pydb.users.update_one({'username': username}, {"$set": {'nickname': nickname}})
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join('app', 'static', 'filedata', filename))
            avatar = '/static/filedata/' + filename
            if avatar:
                pydb.users.update_one({'username': username}, {"$set": {'avatar': avatar}})
        email = form.email.data
        if email:
            pydb.users.update_one({'username': username}, {"$set": {'email': email}})
        description = form.description.data
        if description:
            pydb.users.update_one({'username': username}, {"$set": {'personal_description': description}})
        if request.form['submit'] == 'M':
            gender = "Male"
        elif request.form['submit'] == 'F':
            gender = "Female"
        if gender:
            pydb.users.update_one({'username': username}, {"$set": {'gender': gender}})
            flash('Your profile has been updated, please close this window now.', category='info')
    return render_template('/guide/edit_profile.html', form=form)

@guide.route('/recommend_movies', methods=['GET', 'POST'])
@login_required
def recommend_movies():
    cur_user = current_user.username
    re = pydb.users.find_one({'username': cur_user})
    username = re['username']
    gender = re['gender']
    avatar = re['avatar']
    email = re['email']
    wishlist_db = pydb.wishlists
    cur_wlist = wishlist_db.find_one({"username": cur_user})['wlist']
    movies_db = pydb.movies
    try:
        description = re['personal_description']
        nickname = re['nickname']
    except:
        description = None
        nickname = None
    comments = pydb.comments
    movies = pydb.movies
    ratings = pydb.ratings
    try:
        X, Y, data = Recommendation_System(comments).dbcomments2dataframe()
        W, user_item = Recommendation_System(comments).ItemSimilarity(X, Y)
        rank = Recommendation_System(comments).recommend(current_user.username, user_item, W, 25)
        movie_rank = Recommendation_System(comments).movie_rank(data, rank)
        trainSet, testSet = Recommendation_System(comments).get_dataset(data)
        movie_sim_matrix, movie_popular, movie_count = Recommendation_System(comments).calc_movie_sim(trainSet)
        res = Recommendation_System(comments).item_based_recommend(current_user.username, 40, 20, trainSet, movie_sim_matrix)
        movie_rank2 = Recommendation_System(comments).precommend(res, movies)
        movie_recommend = list(set(movie_rank + movie_rank2))
        recom_list = []
        for name in movie_recommend:
            res = movies.find_one({"movie_name": name})
            del res['_id']
            del res['description']
            recom_list.append(res)
        if len(recom_list) >= 28:
            recom_list = recom_list[:28]
        return render_template('/search/film_search_results.html', list=recom_list, avatar=avatar, username=username, gender=gender, description=description, email=email, nickname=nickname, cur_wlist=cur_wlist,movies_db=movies_db)
    except:
        df = pd.DataFrame(columns=['movie_id', 'ratings'])
        i = 0
        for x in ratings.find():
            df.loc[i, 'movie_id'] = x['movie_id']
            df.loc[i, 'ratings'] = x['ratings']
            i += 1
        df = df.sort_values(by='ratings', ascending=False)
        recom = df['movie_id'].head(28).values
        recom_list = []
        for name in recom:
            res = movies.find_one({"movie_id": name})
            del res['_id']
            del res['description']
            recom_list.append(res)
        return render_template('/search/film_search_results.html', list=recom_list, avatar=avatar, username=username, gender=gender, description=description, email=email, nickname=nickname, cur_wlist=cur_wlist, movies_db=movies_db)