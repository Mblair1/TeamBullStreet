import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, AddCommentForm
from flaskblog.models import User, Post, Comment
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import SocketIO

socketio = SocketIO(app)

@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user, likes=0, dislikes=0)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).all()
    commentCount = Comment.query.filter_by(post_id=post_id).count()
    return render_template('post.html', title=post.title, post=post, comments=comments, commentCount=commentCount)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    comments = Comment.query.filter_by(post_id=post_id).all()
    for comment in comments:
        db.session.delete(comment)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/calendar", methods=['GET'])
@login_required
def calendar():
    return render_template('index.html', title='Calendar')

@app.route("/metrics", methods=['GET'])
@login_required
def metrics():
    return render_template('chart.html', title='Company Metrics')

@app.route('/chat', methods=['GET', 'POST'])
def sessions():
    return render_template('messageIndex.html')

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

@app.route('/upvote/<int:post_id>/<int:user_id>')
@login_required
def upvote(post_id,user_id):
    post = Post.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/downvote/<int:post_id>/<int:user_id>')
@login_required
def downvote(post_id,user_id):
    post = Post.query.get_or_404(post_id)
    post.dislikes += 1
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/post/<int:post_id>/comment", methods=["GET", "POST"])
@login_required
def comment_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = AddCommentForm()
    if request.method == 'POST': # this only gets executed when the form is submitted and not when the page loads
        if form.validate_on_submit():
            comment = Comment(username=current_user.username, body=form.body.data, post_id=post.id)
            db.session.add(comment)
            db.session.commit()
            flash("Your comment has been added to the post", "success")
            return redirect(url_for("post", post_id=post.id))
    return render_template("comment_post.html", title="Comment Post", 
            form=form, post_id=post_id)

@app.route('/news', methods=['GET'])
@login_required
def newsletter():
    return render_template("newsletter.html", title="Company News")

@app.route('/form', methods=['GET'])
@login_required
def form():
    return render_template("form.html", title="Scheduler")

@app.route('/inclusion', methods=['GET'])
@login_required
def inclusion():
    return render_template("inclusion.html", title="Inclusion")

@app.route('/Anno', methods=['GET'])
@login_required
def anno():
    return render_template("Anno.html", title="Report")

@app.route('/workingwomen', methods=['GET'])
@login_required
def workingwomen():
    return render_template("workingwomen.html", title="Working Women")