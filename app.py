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

# --- HELPER FOR HTMX INTERACTIONS ---
def get_interaction_html():
    likes_obj = LikeCounter.query.first()
    likes = likes_obj.count if likes_obj else 0
    comments = Comment.query.order_by(Comment.id.desc()).all()
    
    return render_template_string('''
        <div class="d-inline-block mb-4">
            <button hx-post="/like" hx-swap="outerHTML" hx-target="#interaction-area" class="btn btn-like rounded-pill px-4 py-2 fw-bold">
                <i class="fa-solid fa-heart me-2"></i> Like 
                <span class="badge bg-warning text-dark ms-2">{{ likes }}</span>
            </button>
        </div>

        <div class="text-start">
            <h5 class="text-white border-bottom pb-2 mb-3">Leave a Wish</h5>
            <form hx-post="/comment" hx-target="#interaction-area" hx-swap="outerHTML" 
                  class="row g-2 mb-4" onsubmit="setTimeout(()=>this.reset(), 100);">
                <div class="col-4">
                    <input type="text" name="author" class="form-control bg-dark text-white border-secondary" placeholder="Name" required>
                </div>
                <div class="col-6">
                    <input type="text" name="comment_text" class="form-control bg-dark text-white border-secondary" placeholder="Message..." required>
                </div>
                <div class="col-2">
                    <button type="submit" class="btn btn-warning w-100 fw-bold">Post</button>
                </div>
            </form>

            <div class="comments-list" style="max-height: 400px; overflow-y: auto;">
                {% if comments|length == 0 %}
                    <p class="text-muted fst-italic">No comments yet.</p>
                {% else %}
                    {% for comment in comments %}
                    <div class="comment-box" style="background-color: #3b3b3b; border-radius: 10px; padding: 10px; margin-bottom: 10px; border-left: 4px solid #ffcc00;">
                        <div style="color: #ffcc00; font-weight: bold; font-size: 0.9em;">{{ comment.author }}</div>
                        <div class="text-light small">{{ comment.text }}</div>
                    </div>
                    {% endfor %}
                {% endif %}
            </div>
        </div>
    ''', likes=likes, comments=comments)

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

    # HTML TEMPLATE
    html_content = '''
    <!doctype html>
    <html lang="en" data-bs-theme="dark">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
        <title>Badminton Daddy</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <script src="https://unpkg.com/htmx.org@1.9.6"></script>
        
        <style>
            body { background-color: #1a1a1a; color: white; font-family: 'Segoe UI', sans-serif; touch-action: manipulation; }
            .custom-header { color: #ffcc00; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; }
            
            /* Tabs */
            .nav-tabs .nav-link.active { background-color: #ffcc00; color: black; border-color: #ffcc00; font-weight: bold; }
            .nav-tabs .nav-link { color: #ffcc00; margin-right: 5px; border: 1px solid #333; }
            .nav-tabs { border-bottom: 2px solid #ffcc00; }
            
            /* Card Styling */
            .wish-card { border: 4px solid #ffcc00; background-color: #2c2c2c; border-radius: 20px; }
            .btn-like { border: 2px solid #ffcc00; color: #ffcc00; background: transparent; }
            .btn-like:hover { background-color: #ffcc00; color: black; }

            /* --- SCOREBOARD STYLES --- */
            .score-container { display: flex; height: 50vh; width: 100%; border: 2px solid #444; border-radius: 15px; overflow: hidden; margin-top: 20px;}
            .team-area { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; cursor: pointer; transition: background 0.1s; position: relative; }
            .team-a-bg { background-color: #2c2c2c; border-right: 1px solid #555; }
            .team-b-bg { background-color: #252525; }
            .team-area:active { background-color: #444; } /* Tap feedback */

            .score-number { font-size: 6rem; font-weight: 800; line-height: 1; user-select: none; }
            .team-name-input { background: transparent; border: none; color: #aaa; text-align: center; font-size: 1.5rem; width: 80%; font-weight: bold; }
            .team-name-input:focus { outline: none; border-bottom: 2px solid #ffcc00; color: white; }
            
            .score-controls { display: flex; justify-content: center; gap: 10px; margin-top: 15px; }
            .winner-glow { box-shadow: inset 0 0 50px #00ff00 !important; border: 2px solid #00ff00 !important; }
        </style>
      </head>
      <body>
        
        <div class="container mt-4 text-center mb-5">
            <h1 class="mb-4 custom-header">🏸 Badminton Daddy 🏸</h1>

            <ul class="nav nav-tabs justify-content-center mb-4" id="myTab" role="tablist">
                <li class="nav-item"><button class="nav-link active" data-bs-toggle="tab" data-bs-target="#standings">Standings</button></li>
                <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#announcements">Announcements</button></li>
                <li class="nav-item"><button class="nav-link" id="score-tab-btn" data-bs-toggle="tab" data-bs-target="#scoreboard">Score Calculator</button></li>
            </ul>

            <div class="tab-content" id="myTabContent">

                <div class="tab-pane fade show active" id="standings">
                    <div class="table-responsive mx-auto" style="max-width: 600px;">
                        <table class="table table-dark table-striped table-hover align-middle">
                            <thead>
                                <tr style="border-bottom: 2px solid #ffcc00;">
                                    <th class="text-warning">Rank</th><th class="text-warning">Player</th><th class="text-warning">Elo</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for player in rankings %}
                                <tr>
                                    <th class="text-warning">#{{ player.rank }}</th><td>{{ player.name }}</td><td class="text-warning fw-bold">{{ player.elo }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="tab-pane fade" id="announcements">
                    <div class="container" style="max-width: 700px;">
                        
                        <div class="card wish-card p-4 mb-4">
                            <p class="fs-2 fw-bold text-white mb-4">Best of Luck <span class="text-warning">Ourab!</span> for his GATE Exam 🎓</p>
                            
                            <div class="mb-4">
                                <img src="{{ gif_url }}" class="img-fluid rounded" style="max-width: 100%; border: 2px solid white;">
                            </div>

                            <div id="interaction-area" hx-get="/updates" hx-trigger="every 2s" hx-swap="innerHTML">
                                 {{ interaction_html|safe }}
                            </div>
                        </div>

                        <div class="card wish-card p-4 mb-4 text-start">
                            <div class="d-flex align-items-center mb-3">
                                <i class="fa-solid fa-bullhorn text-warning fs-3 me-3"></i>
                                <h4 class="text-white m-0 fw-bold">Update: Score Calculator</h4>
                            </div>
                            <p class="text-light">
                                No more fighting over the score! We have added a <strong>Live Score Calculator</strong>. 
                                It works without internet and features big tap zones for referees.
                            </p>
                            <button onclick="document.getElementById('score-tab-btn').click()" class="btn btn-outline-warning w-100 fw-bold">
                                <i class="fa-solid fa-calculator me-2"></i> Try Scoreboard Now
                            </button>
                        </div>

                    </div>
                </div>

                <div class="tab-pane fade" id="scoreboard">
                    <div class="container" style="max-width: 800px;">
                        
                        <div class="alert alert-secondary p-2 mb-3 small">
                            <i class="fa-solid fa-circle-info"></i> Tap huge colored areas to add points. Refresh page to reset.
                        </div>

                        <div class="score-container">
                            <div id="areaA" class="team-area team-a-bg" onclick="addPoint('A')">
                                <input type="text" value="Team A" class="team-name-input" onclick="event.stopPropagation()">
                                <div id="scoreA" class="score-number text-white">0</div>
                            </div>
                            
                            <div id="areaB" class="team-area team-b-bg" onclick="addPoint('B')">
                                <input type="text" value="Team B" class="team-name-input" onclick="event.stopPropagation()">
                                <div id="scoreB" class="score-number text-warning">0</div>
                            </div>
                        </div>

                        <div class="score-controls">
                            <button class="btn btn-secondary" onclick="undoPoint()"><i class="fa-solid fa-rotate-left"></i> Undo</button>
                            <button class="btn btn-outline-warning" onclick="swapSides()"><i class="fa-solid fa-arrow-right-arrow-left"></i> Swap</button>
                            <button class="btn btn-danger" onclick="resetScore()"><i class="fa-solid fa-trash"></i> Reset</button>
                        </div>

                    </div>
                </div>

            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // --- BADMINTON SCOREBOARD LOGIC ---
            let scoreA = 0;
            let scoreB = 0;
            let historyStack = [];

            function updateDisplay() {
                const elA = document.getElementById('scoreA');
                const elB = document.getElementById('scoreB');
                const areaA = document.getElementById('areaA');
                const areaB = document.getElementById('areaB');

                elA.innerText = scoreA;
                elB.innerText = scoreB;

                areaA.classList.remove('winner-glow');
                areaB.classList.remove('winner-glow');

                let winner = null;
                if (scoreA >= 21 && scoreA >= scoreB + 2) winner = 'A';
                if (scoreB >= 21 && scoreB >= scoreA + 2) winner = 'B';
                if (scoreA === 30) winner = 'A';
                if (scoreB === 30) winner = 'B';

                if (winner === 'A') areaA.classList.add('winner-glow');
                if (winner === 'B') areaB.classList.add('winner-glow');
            }

            function addPoint(team) {
                historyStack.push({ A: scoreA, B: scoreB });
                if (team === 'A') scoreA++; else scoreB++;
                if (navigator.vibrate) navigator.vibrate(50); 
                updateDisplay();
            }

            function undoPoint() {
                if (historyStack.length > 0) {
                    const lastState = historyStack.pop();
                    scoreA = lastState.A;
                    scoreB = lastState.B;
                    updateDisplay();
                }
            }

            function resetScore() {
                if(confirm("Start a new game?")) {
                    scoreA = 0; scoreB = 0; historyStack = []; updateDisplay();
                }
            }

            function swapSides() {
                let tempScore = scoreA; scoreA = scoreB; scoreB = tempScore;
                const inputs = document.querySelectorAll('.team-name-input');
                let tempName = inputs[0].value; inputs[0].value = inputs[1].value; inputs[1].value = tempName;
                updateDisplay();
            }
        </script>
      </body>
    </html>
    '''
    
    return render_template_string(html_content, rankings=standings_data, gif_url=gif_url, interaction_html=get_interaction_html())

# --- ROUTES ---
@app.route('/updates')
def updates(): return get_interaction_html()

@app.route('/like', methods=['POST'])
def like():
    likes_obj = LikeCounter.query.first()
    if not likes_obj: likes_obj = LikeCounter(count=0); db.session.add(likes_obj)
    likes_obj.count += 1
    db.session.commit()
    return get_interaction_html()

@app.route('/comment', methods=['POST'])
def comment():
    if request.form.get('author') and request.form.get('comment_text'):
        db.session.add(Comment(author=request.form['author'], text=request.form['comment_text']))
        db.session.commit()
    return get_interaction_html()

if __name__ == '__main__':
    app.run(debug=True)