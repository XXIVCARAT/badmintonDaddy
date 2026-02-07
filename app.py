import os
from flask import Flask, url_for, render_template_string, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELS ---
class LikeCounter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50), nullable=False)
    text = db.Column(db.String(500), nullable=False)

# Init DB
with app.app_context():
    db.create_all()
    if not LikeCounter.query.first():
        db.session.add(LikeCounter(count=0))
        db.session.commit()

@app.route('/')
def index():
    # 1. HARDCODED RANKINGS
    standings_data = [
        {"rank": 1, "name": "Ourab", "elo": 1500},
        {"rank": 2, "name": "Anuj", "elo": 1480},
        {"rank": 3, "name": "Suhal", "elo": 1450},
        {"rank": 4, "name": "Sujay", "elo": 1425},
        {"rank": 5, "name": "Harshil", "elo": 1420},
        {"rank": 6, "name": "Shreyas", "elo": 1390},
        {"rank": 7, "name": "Ishita", "elo": 1390},
        {"rank": 8, "name": "Idhant", "elo": 1350},
        {"rank": 9, "name": "Chirag", "elo": 1350},
        {"rank": 10, "name": "Nirlep", "elo": 1300},
        {"rank": 11, "name": "Ameya", "elo": 1250},
    ]

    gif_url = url_for('static', filename='my_cool_gif.gif')

    # HTML TEMPLATE WITH JAVASCRIPT
    html_content = '''
    <!doctype html>
    <html lang="en" data-bs-theme="dark">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Badminton Daddy</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        
        <style>
            body { background-color: #1a1a1a; color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            .custom-header { color: #ffcc00; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; }
            .nav-tabs .nav-link.active { background-color: #ffcc00; color: black; border-color: #ffcc00; font-weight: bold; }
            .nav-tabs .nav-link { color: #ffcc00; margin-right: 5px; border: 1px solid #333; }
            .nav-tabs { border-bottom: 2px solid #ffcc00; }
            .wish-card { border: 4px solid #ffcc00; background-color: #2c2c2c; border-radius: 20px; box-shadow: 0 0 20px rgba(255, 204, 0, 0.3); }
            .wish-text { font-size: 2rem; color: #fff; font-weight: bold; line-height: 1.4; }
            .highlight-name { color: #ffcc00; text-decoration: underline; }
            
            .interaction-section { border-top: 1px solid #555; padding-top: 20px; margin-top: 20px; }
            .btn-like { border: 2px solid #ffcc00; color: #ffcc00; background: transparent; transition: 0.3s; }
            .btn-like:hover { background-color: #ffcc00; color: black; }
            .comment-box { background-color: #3b3b3b; border-radius: 10px; padding: 10px; margin-bottom: 10px; text-align: left; border-left: 4px solid #ffcc00; }
            .comment-author { color: #ffcc00; font-weight: bold; font-size: 0.9em; margin-bottom: 2px;}
        </style>
      </head>
      <body>
        
        <div class="container mt-5 text-center mb-5">
            <h1 class="mb-5 custom-header">🏸 Badminton Daddy 🏸</h1>

            <ul class="nav nav-tabs justify-content-center mb-4" id="myTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="standings-tab" data-bs-toggle="tab" data-bs-target="#standings" type="button" role="tab">Standings</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="announcements-tab" data-bs-toggle="tab" data-bs-target="#announcements" type="button" role="tab">Announcements</button>
                </li>
            </ul>

            <div class="tab-content" id="myTabContent">

                <div class="tab-pane fade show active" id="standings" role="tabpanel">
                    <div class="table-responsive mx-auto" style="max-width: 600px;">
                        <table class="table table-dark table-striped table-hover table-custom align-middle">
                            <thead>
                                <tr style="border-bottom: 2px solid #ffcc00;">
                                    <th scope="col" style="color: #ffcc00;">Rank</th>
                                    <th scope="col" style="color: #ffcc00;">Player Name</th>
                                    <th scope="col" style="color: #ffcc00;">Elo Rating</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for player in rankings %}
                                <tr>
                                    <th scope="row" class="rank-col">#{{ player.rank }}</th>
                                    <td class="fs-5">{{ player.name }}</td>
                                    <td class="text-warning fw-bold">{{ player.elo }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="tab-pane fade" id="announcements" role="tabpanel">
                    <div class="container" style="max-width: 700px;">
                        <div class="card wish-card p-4 mb-4">
                            <p class="wish-text">
                                Badminton Daddy wishes <br>
                                <span class="highlight-name">Ourab</span> <br>
                                All the Best for his <br>
                                <span style="color: #00d4ff;">GATE Exam!</span> 🎓
                            </p>
                            
                            <div class="mt-4">
                                <img src="{{ gif_url }}" alt="Good Luck GIF" class="img-fluid rounded" style="border: 2px solid white; max-width: 100%;">
                            </div>

                            <div class="interaction-section">
                                
                                <div class="d-inline-block mb-4">
                                    <button id="likeBtn" class="btn btn-like rounded-pill px-4 py-2 fw-bold" onclick="sendLike()">
                                        <i class="fa-solid fa-heart me-2"></i> Likes 
                                        <span id="likeCount" class="badge bg-warning text-dark ms-2">Loading...</span>
                                    </button>
                                </div>

                                <div class="text-start">
                                    <h5 class="text-white border-bottom pb-2 mb-3">Leave a Wish</h5>
                                    <form id="commentForm" onsubmit="sendComment(event)" class="row g-2 mb-4">
                                        <div class="col-4">
                                            <input type="text" id="author" class="form-control bg-dark text-white border-secondary" placeholder="Your Name" required>
                                        </div>
                                        <div class="col-6">
                                            <input type="text" id="commentText" class="form-control bg-dark text-white border-secondary" placeholder="Write something nice..." required>
                                        </div>
                                        <div class="col-2">
                                            <button type="submit" class="btn btn-warning w-100 fw-bold">Post</button>
                                        </div>
                                    </form>

                                    <div id="commentsList" class="comments-list" style="max-height: 400px; overflow-y: auto;">
                                        <p class="text-muted fst-italic">Loading comments...</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        
        <script>
            // --- 1. FUNCTION TO FETCH UPDATES (The Live Part) ---
            function fetchUpdates() {
                fetch('/api/updates')
                    .then(response => response.json())
                    .then(data => {
                        // Update Like Count
                        document.getElementById('likeCount').innerText = data.likes;
                        
                        // Update Comments List
                        const commentsList = document.getElementById('commentsList');
                        if (data.comments.length === 0) {
                            commentsList.innerHTML = '<p class="text-muted fst-italic">No comments yet. Be the first!</p>';
                        } else {
                            let html = '';
                            data.comments.forEach(comment => {
                                html += `
                                    <div class="comment-box">
                                        <div class="comment-author">${comment.author}</div>
                                        <div class="text-light small">${comment.text}</div>
                                    </div>
                                `;
                            });
                            commentsList.innerHTML = html;
                        }
                    });
            }

            // --- 2. FUNCTION TO SEND LIKE ---
            function sendLike() {
                fetch('/like', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    // Update the count immediately after clicking
                    document.getElementById('likeCount').innerText = data.count;
                });
            }

            // --- 3. FUNCTION TO SEND COMMENT ---
            function sendComment(event) {
                event.preventDefault(); // Stop page reload
                
                const author = document.getElementById('author').value;
                const text = document.getElementById('commentText').value;
                
                const formData = new FormData();
                formData.append('author', author);
                formData.append('comment_text', text);

                fetch('/comment', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    // Clear the input boxes
                    document.getElementById('author').value = '';
                    document.getElementById('commentText').value = '';
                    // Force an update immediately so user sees their comment
                    fetchUpdates();
                });
            }

            // --- 4. START THE LIVE UPDATES ---
            // Fetch immediately on load
            fetchUpdates();
            // Fetch every 2 seconds (2000 milliseconds)
            setInterval(fetchUpdates, 2000);
            
        </script>
      </body>
    </html>
    '''
    
    return render_template_string(html_content, rankings=standings_data, gif_url=gif_url)

# --- NEW API ROUTE FOR LIVE UPDATES ---
@app.route('/api/updates')
def get_updates():
    likes_obj = LikeCounter.query.first()
    likes = likes_obj.count if likes_obj else 0
    
    comments = Comment.query.order_by(Comment.id.desc()).all()
    comments_list = [{'author': c.author, 'text': c.text} for c in comments]
    
    return jsonify({'likes': likes, 'comments': comments_list})

# --- UPDATED LIKE ROUTE (Returns JSON now) ---
@app.route('/like', methods=['POST'])
def like_post():
    likes_obj = LikeCounter.query.first()
    if not likes_obj:
        likes_obj = LikeCounter(count=0)
        db.session.add(likes_obj)
    
    likes_obj.count += 1
    db.session.commit()
    return jsonify({'count': likes_obj.count})

# --- UPDATED COMMENT ROUTE (Returns JSON now) ---
@app.route('/comment', methods=['POST'])
def add_comment():
    author = request.form.get('author')
    text = request.form.get('comment_text')
    
    if author and text:
        new_comment = Comment(author=author, text=text)
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400

if __name__ == '__main__':
    app.run(debug=True)