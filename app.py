import os
from flask import Flask, url_for, render_template_string, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# ---------------- DATABASE ----------------
db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///local.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ---------------- MODELS ----------------
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    singles_played = db.Column(db.Integer, default=0)
    singles_won = db.Column(db.Integer, default=0)
    singles_lost = db.Column(db.Integer, default=0)

    doubles_played = db.Column(db.Integer, default=0)
    doubles_won = db.Column(db.Integer, default=0)
    doubles_lost = db.Column(db.Integer, default=0)


class MatchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    winner_names = db.Column(db.String(200))
    loser_names = db.Column(db.String(200))
    match_type = db.Column(db.String(10))
    score = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())


class LikeCounter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    media_url = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())


# ---------------- INIT ----------------
def init_db():
    with app.app_context():
        db.create_all()

        if not Player.query.first():
            for name in [
                "Manan", "Ourab", "Anuj", "Suhal", "Sujay", "Harshil",
                "Shreyas", "Ishita", "Idhant", "Chirag", "Nirlep", "Ameya"
            ]:
                db.session.add(Player(name=name))

        if not LikeCounter.query.first():
            db.session.add(LikeCounter(count=0))

        db.session.commit()

init_db()

# ---------------- HTML FRAGMENTS ----------------
def rankings_html():
    s = Player.query.order_by(Player.singles_won.desc(), Player.singles_played).all()
    d = Player.query.order_by(Player.doubles_won.desc(), Player.doubles_played).all()

    return render_template_string("""
    <div class="table-responsive">
    <table class="table table-dark table-striped table-sm">
        <thead>
            <tr><th>#</th><th>Name</th><th>P</th><th>W</th><th>L</th></tr>
        </thead>
        <tbody>
        {% for p in s %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ p.name }}</td>
                <td>{{ p.singles_played }}</td>
                <td class="text-warning">{{ p.singles_won }}</td>
                <td class="text-danger">{{ p.singles_lost }}</td>
            </tr>
        {% endfor %}
        </tbody>
    </table>
    </div>
    """, s=s, d=d)


def likes_html():
    l = LikeCounter.query.first()
    return render_template_string("""
    <button hx-post="/like" hx-swap="outerHTML"
        class="btn btn-outline-warning rounded-pill">
        ❤️ Like <span class="badge bg-warning text-dark">{{ l.count }}</span>
    </button>
    """, l=l)


def posts_html():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template_string("""
    <div id="posts-list" hx-get="/update-posts" hx-trigger="every 5s" hx-swap="outerHTML">
        {% for p in posts %}
        <div class="p-3 mb-3 bg-dark border-start border-warning border-4 rounded">
            <div class="text-warning fw-bold">{{ p.author }}</div>
            <div class="small mb-2">{{ p.text }}</div>

            {% if p.media_url %}
                {% if "youtube" in p.media_url or "youtu.be" in p.media_url %}
                    <div class="ratio ratio-16x9">
                        <iframe src="https://www.youtube.com/embed/{{ p.media_url.split('v=')[-1].split('/')[-1] }}"
                                allowfullscreen></iframe>
                    </div>
                {% elif p.media_url.endswith(('.jpg','.png','.jpeg','.gif','.webp')) %}
                    <img src="{{ p.media_url }}" class="img-fluid rounded">
                {% else %}
                    <video controls class="w-100 rounded">
                        <source src="{{ p.media_url }}">
                    </video>
                {% endif %}
            {% endif %}
        </div>
        {% else %}
        <p class="text-muted fst-italic">No posts yet.</p>
        {% endfor %}
    </div>
    """, posts=posts)

# ---------------- MAIN PAGE ----------------
@app.route("/")
def index():
    players = [p.name for p in Player.query.order_by(Player.name).all()]
    gif_url = "https://media.giphy.com/media/3o7TKSjRrfPHwSHaTu/giphy.gif"

    return render_template_string("""
<!doctype html>
<html lang="en" data-bs-theme="dark">
<head>
<meta charset="utf-8">
<title>Badminton Daddy</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://unpkg.com/htmx.org@1.9.6"></script>
</head>
<body class="bg-dark text-white">

<div class="container mt-4">
<h1 class="text-warning text-center">🏸 Badminton Daddy</h1>

<ul class="nav nav-tabs justify-content-center my-4">
  <li class="nav-item"><button class="nav-link active" data-bs-toggle="tab" data-bs-target="#standings">Standings</button></li>
  <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#posts">Posts</button></li>
</ul>

<div class="tab-content">

<div class="tab-pane fade show active" id="standings" hx-get="/update-rankings" hx-trigger="load, every 10s">
{{ rankings|safe }}
</div>

<div class="tab-pane fade" id="posts">
<div class="card bg-dark border-warning p-3 mb-3">

<h5>Create a Post</h5>
<form hx-post="/post" hx-target="#posts-list" hx-swap="outerHTML" class="row g-2 mb-3">
    <div class="col-4">
        <input name="author" class="form-control form-control-sm" placeholder="Name" required>
    </div>
    <div class="col-8">
        <input name="media_url" class="form-control form-control-sm"
               placeholder="Media link (GIF / Image / YouTube)">
    </div>
    <div class="col-10">
        <input name="text" class="form-control form-control-sm"
               placeholder="What's on your mind?" required>
    </div>
    <div class="col-2">
        <button class="btn btn-warning btn-sm w-100">Post</button>
    </div>
</form>

<div hx-get="/update-likes" hx-trigger="every 5s">
{{ likes|safe }}
</div>

<hr>
{{ posts|safe }}

</div>
</div>

</div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""",
        rankings=rankings_html(),
        likes=likes_html(),
        posts=posts_html()
    )

# ---------------- ROUTES ----------------
@app.route("/update-rankings")
def update_rankings():
    return rankings_html()

@app.route("/update-likes")
def update_likes():
    return likes_html()

@app.route("/update-posts")
def update_posts():
    return posts_html()

@app.route("/like", methods=["POST"])
def like():
    l = LikeCounter.query.first()
    l.count += 1
    db.session.commit()
    return likes_html()

@app.route("/post", methods=["POST"])
def post():
    author = request.form.get("author")
    text = request.form.get("text")
    media_url = request.form.get("media_url")

    if author and text:
        db.session.add(Post(author=author, text=text, media_url=media_url))
        db.session.commit()

    return posts_html()

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
