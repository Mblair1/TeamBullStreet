from flask import Flask, render_template, url_for
app = Flask(__name__)

posts = [
    {
        'author': 'Matthew Blair',
        'title': 'Feed Post 1',
        'content': 'First post content',
        'date_posted': 'Auguest 11, 2021'
    },
    {
        'author': 'Kenndog',
        'title': 'Beethoven',
        'content': 'Homies with the guap',
        'date_posted': 'Auguest 11, 2021'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


if __name__ == '__main__':
    app.run(debug=True)
