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
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    singles_won = db.Column(db.Integer, default=0)
    doubles_won = db.Column(db.Integer, default=0) # Individual wins in doubles matches

class MatchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    winner_names = db.Column(db.String(200))
    loser_names = db.Column(db.String(200))
    score = db.Column(db.String(20))
    match_type = db.Column(db.String(10)) # 'Singles' or 'Doubles'

class LikeCounter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50), nullable=False)
    text = db.Column(db.String(500), nullable=False)

# --- INITIALIZATION ---
def init_db():
    with app.app_context():
        db.create_all()
        
        # Seed Initial Players if empty
        if not Player.query.first():
            initial_players = [
                "Manan", "Ourab", "Anuj", "Suhal", "Sujay", "Harshil", 
                "Shreyas", "Ishita", "Idhant", "Chirag", "Nirlep", "Ameya"
            ]
            for name in initial_players:
                db.session.add(Player(name=name))
            
            # Init Likes
            if not LikeCounter.query.first():
                db.session.add(LikeCounter(count=0))
            
            db.session.commit()
            print("Database initialized with players!")

init_db()

# --- HTMX FRAGMENTS ---

def get_rankings_html():
    # Fetch players sorted by wins
    singles_rank = Player.query.order_by(Player.singles_won.desc()).all()
    doubles_rank = Player.query.order_by(Player.doubles_won.desc()).all()
    
    return render_template_string('''
        <div class="d-flex justify-content-center mb-3">
            <div class="btn-group" role="group">
                <input type="radio" class="btn-check" name="ranktype" id="btnradio1" autocomplete="off" checked 
                       onclick="document.getElementById('singles-table').classList.remove('d-none'); document.getElementById('doubles-table').classList.add('d-none');">
                <label class="btn btn-outline-warning" for="btnradio1">Singles</label>

                <input type="radio" class="btn-check" name="ranktype" id="btnradio2" autocomplete="off"
                       onclick="document.getElementById('doubles-table').classList.remove('d-none'); document.getElementById('singles-table').classList.add('d-none');">
                <label class="btn btn-outline-warning" for="btnradio2">Doubles</label>
            </div>
        </div>

        <div id="singles-table" class="table-responsive mx-auto" style="max-width: 600px;">
            <h5 class="text-warning mb-2">🏆 Singles Leaderboard</h5>
            <table class="table table-dark table-striped table-hover align-middle">
                <thead><tr style="border-bottom: 2px solid #ffcc00;"><th class="text-warning">Rank</th><th>Player</th><th class="text-end text-warning">Wins</th></tr></thead>
                <tbody>
                    {% for p in s_ranks %}
                    <tr>
                        <th class="text-warning">#{{ loop.index }}</th>
                        <td>{{ p.name }}</td>
                        <td class="text-end fw-bold text-warning">{{ p.singles_won }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div id="doubles-table" class="table-responsive mx-auto d-none" style="max-width: 600px;">
            <h5 class="text-warning mb-2">👥 Doubles Leaderboard</h5>
            <table class="table table-dark table-striped table-hover align-middle">
                <thead><tr style="border-bottom: 2px solid #ffcc00;"><th class="text-warning">Rank</th><th>Player</th><th class="text-end text-warning">Wins</th></tr></thead>
                <tbody>
                    {% for p in d_ranks %}
                    <tr>
                        <th class="text-warning">#{{ loop.index }}</th>
                        <td>{{ p.name }}</td>
                        <td class="text-end fw-bold text-warning">{{ p.doubles_won }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    ''', s_ranks=singles_rank, d_ranks=doubles_rank)

def get_likes_html():
    likes_obj = LikeCounter.query.first()
    likes = likes_obj.count if likes_obj else 0
    return render_template_string('''
        <button id="like-btn" hx-post="/like" hx-swap="outerHTML" class="btn btn-like rounded-pill px-4 py-2 fw-bold">
            <i class="fa-solid fa-heart me-2"></i> Like 
            <span class="badge bg-warning text-dark ms-2">{{ likes }}</span>
        </button>
    ''', likes=likes)

def get_comments_html():
    comments = Comment.query.order_by(Comment.id.desc()).all()
    return render_template_string('''
        <div id="comments-list" class="comments-list" style="max-height: 400px; overflow-y: auto;"
             hx-get="/update-comments" hx-trigger="every 5s" hx-swap="outerHTML">
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
    ''', comments=comments)

# --- MAIN ROUTE ---
@app.route('/')
def index():
    players = Player.query.order_by(Player.name).all()
    player_names = [p.name for p in players]
    gif_url = url_for('static', filename='my_cool_gif.gif')

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
            .nav-tabs .nav-link.active { background-color: #ffcc00; color: black; border-color: #ffcc00; font-weight: bold; }
            .nav-tabs .nav-link { color: #ffcc00; margin-right: 5px; border: 1px solid #333; }
            .nav-tabs { border-bottom: 2px solid #ffcc00; }
            .wish-card { border: 4px solid #ffcc00; background-color: #2c2c2c; border-radius: 20px; }
            .btn-like { border: 2px solid #ffcc00; color: #ffcc00; background: transparent; }
            .btn-like:hover { background-color: #ffcc00; color: black; }
            
            /* Scoreboard */
            .score-container { display: flex; height: 50vh; width: 100%; border: 2px solid #444; border-radius: 15px; overflow: hidden; margin-top: 20px;}
            .team-area { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; cursor: pointer; transition: background 0.1s; position: relative; }
            .team-a-bg { background-color: #2c2c2c; border-right: 1px solid #555; }
            .team-b-bg { background-color: #252525; }
            .team-area:active { background-color: #444; } 
            .score-number { font-size: 6rem; font-weight: 800; line-height: 1; user-select: none; }
            .team-label { color: #aaa; font-size: 1.5rem; font-weight: bold; pointer-events: none; }
            .winner-glow { box-shadow: inset 0 0 50px #00ff00 !important; border: 2px solid #00ff00 !important; }
            
            /* Save Modal */
            .player-select { background: #333; color: white; border: 1px solid #555; margin-bottom: 10px; }
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

                <div class="tab-pane fade show active" id="standings" hx-get="/update-rankings" hx-trigger="load, every 10s">
                    {{ rankings_html|safe }}
                </div>
                
                <div class="tab-pane fade" id="announcements">
                    <div class="container" style="max-width: 700px;">
                        <div class="card wish-card p-4 mb-4">
                            <p class="fs-2 fw-bold text-white mb-4">Best of Luck <span class="text-warning">Ourab!</span> for his GATE Exam 🎓</p>
                            <div class="mb-4"><img src="{{ gif_url }}" class="img-fluid rounded" style="max-width: 100%; border: 2px solid white;"></div>
                            <div class="d-inline-block mb-4" hx-get="/update-likes" hx-trigger="every 5s" hx-swap="innerHTML">{{ like_html|safe }}</div>
                            <div class="text-start">
                                <h5 class="text-white border-bottom pb-2 mb-3">Leave a Wish</h5>
                                <form hx-post="/comment" hx-target="#comments-list" hx-swap="outerHTML" class="row g-2 mb-4" onsubmit="setTimeout(()=>this.reset(), 100);">
                                    <div class="col-4"><input type="text" name="author" class="form-control bg-dark text-white border-secondary" placeholder="Name" required></div>
                                    <div class="col-6"><input type="text" name="comment_text" class="form-control bg-dark text-white border-secondary" placeholder="Message..." required></div>
                                    <div class="col-2"><button type="submit" class="btn btn-warning w-100 fw-bold">Post</button></div>
                                </form>
                                {{ comments_html|safe }}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="tab-pane fade" id="scoreboard">
                    <div class="container" style="max-width: 800px;">
                        
                        <div id="save-area" class="d-none mb-3">
                            <button class="btn btn-success fw-bold w-100 py-3 fs-4 shadow" data-bs-toggle="modal" data-bs-target="#saveModal">
                                <i class="fa-solid fa-floppy-disk me-2"></i> GAME OVER - CLICK TO SAVE
                            </button>
                        </div>

                        <div class="score-container">
                            <div id="areaA" class="team-area team-a-bg" onclick="addPoint('A')">
                                <div class="team-label">TEAM A</div>
                                <div id="scoreA" class="score-number text-white">0</div>
                            </div>
                            <div id="areaB" class="team-area team-b-bg" onclick="addPoint('B')">
                                <div class="team-label">TEAM B</div>
                                <div id="scoreB" class="score-number text-warning">0</div>
                            </div>
                        </div>
                        <div class="score-controls mt-3">
                            <button class="btn btn-secondary" onclick="undoPoint()"><i class="fa-solid fa-rotate-left"></i> Undo</button>
                            <button class="btn btn-outline-warning" onclick="swapSides()"><i class="fa-solid fa-arrow-right-arrow-left"></i> Swap</button>
                            <button class="btn btn-danger" onclick="resetScore()"><i class="fa-solid fa-trash"></i> Reset</button>
                        </div>
                    </div>
                </div>

            </div>
        </div>

        <div class="modal fade" id="saveModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content bg-dark border-warning">
                    <div class="modal-header border-secondary">
                        <h5 class="modal-title text-warning fw-bold">Save Match Result</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-info py-2 small">Select players. If 1 player/side, it saves as Singles. If 2, Doubles.</div>
                        
                        <div class="mb-3 p-2 rounded" style="background: rgba(0,255,0,0.1); border: 1px solid green;">
                            <h6 class="text-success fw-bold mb-2">WINNERS (<span id="win-score-display"></span>)</h6>
                            <select class="form-select player-select" id="winner1">
                                <option value="">Select Winner 1</option>
                                {% for name in player_names %}<option value="{{name}}">{{name}}</option>{% endfor %}
                            </select>
                            <select class="form-select player-select" id="winner2">
                                <option value="">Select Winner 2 (Optional for Doubles)</option>
                                {% for name in player_names %}<option value="{{name}}">{{name}}</option>{% endfor %}
                            </select>
                        </div>

                        <div class="mb-3 p-2 rounded" style="background: rgba(255,0,0,0.1); border: 1px solid red;">
                            <h6 class="text-danger fw-bold mb-2">LOSERS (<span id="lose-score-display"></span>)</h6>
                            <select class="form-select player-select" id="loser1">
                                <option value="">Select Loser 1</option>
                                {% for name in player_names %}<option value="{{name}}">{{name}}</option>{% endfor %}
                            </select>
                            <select class="form-select player-select" id="loser2">
                                <option value="">Select Loser 2 (Optional for Doubles)</option>
                                {% for name in player_names %}<option value="{{name}}">{{name}}</option>{% endfor %}
                            </select>
                        </div>
                    </div>
                    <div class="modal-footer border-secondary">
                        <button type="button" class="btn btn-success w-100 fw-bold" onclick="submitMatch()">Confirm & Update Rankings</button>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // --- LOGIC ---
            let scoreA = 0; scoreB = 0; historyStack = [];
            let gameOver = false;

            function updateDisplay() {
                const elA = document.getElementById('scoreA');
                const elB = document.getElementById('scoreB');
                const areaA = document.getElementById('areaA');
                const areaB = document.getElementById('areaB');
                const saveArea = document.getElementById('save-area');

                elA.innerText = scoreA; elB.innerText = scoreB;
                areaA.classList.remove('winner-glow'); areaB.classList.remove('winner-glow');
                
                let winner = null;
                // Standard Badminton Rules
                if ((scoreA >= 21 && scoreA >= scoreB + 2) || scoreA === 30) winner = 'A';
                if ((scoreB >= 21 && scoreB >= scoreA + 2) || scoreB === 30) winner = 'B';

                if (winner) {
                    gameOver = true;
                    saveArea.classList.remove('d-none');
                    if (winner === 'A') areaA.classList.add('winner-glow');
                    else areaB.classList.add('winner-glow');
                    
                    // Prep Modal Text
                    document.getElementById('win-score-display').innerText = Math.max(scoreA, scoreB);
                    document.getElementById('lose-score-display').innerText = Math.min(scoreA, scoreB);
                } else {
                    gameOver = false;
                    saveArea.classList.add('d-none');
                }
            }

            function addPoint(team) {
                if(gameOver) return; // Stop scoring if game over
                historyStack.push({ A: scoreA, B: scoreB });
                if (team === 'A') scoreA++; else scoreB++;
                if (navigator.vibrate) navigator.vibrate(40); 
                updateDisplay();
            }

            function undoPoint() {
                if (historyStack.length > 0) {
                    const lastState = historyStack.pop();
                    scoreA = lastState.A; scoreB = lastState.B;
                    gameOver = false; // Allow play again
                    updateDisplay();
                }
            }

            function resetScore() {
                if(confirm("Reset scoreboard?")) { scoreA = 0; scoreB = 0; historyStack = []; gameOver = false; updateDisplay(); }
            }
            
            function swapSides() {
                let temp = scoreA; scoreA = scoreB; scoreB = temp;
                updateDisplay();
            }

            function submitMatch() {
                const w1 = document.getElementById('winner1').value;
                const w2 = document.getElementById('winner2').value;
                const l1 = document.getElementById('loser1').value;
                const l2 = document.getElementById('loser2').value;

                if (!w1 || !l1) { alert("Please select at least one winner and one loser."); return; }

                const winners = [w1]; if(w2) winners.push(w2);
                const losers = [l1]; if(l2) losers.push(l2);

                let type = 'Singles';
                if (winners.length === 2 && losers.length === 2) type = 'Doubles';
                
                fetch('/save_match', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ winners: winners, losers: losers, type: type })
                }).then(response => response.json()).then(data => {
                    if(data.status === 'success') {
                        // Close modal, reset score, reload to show new rankings
                        alert("Match Saved! Rankings Updated.");
                        window.location.reload(); 
                    }
                });
            }
        </script>
      </body>
    </html>
    '''
    return render_template_string(html_content, 
                                rankings_html=get_rankings_html(), 
                                like_html=get_likes_html(), 
                                comments_html=get_comments_html(),
                                gif_url=gif_url,
                                player_names=player_names)

# --- ROUTES FOR DATA ---

@app.route('/update-rankings')
def update_rankings_route(): return get_rankings_html()

@app.route('/update-likes')
def update_likes_route(): return get_likes_html()

@app.route('/update-comments')
def update_comments_route(): return get_comments_html()

@app.route('/like', methods=['POST'])
def like():
    l = LikeCounter.query.first()
    l.count += 1
    db.session.commit()
    return get_likes_html()

@app.route('/comment', methods=['POST'])
def comment():
    if request.form.get('author') and request.form.get('comment_text'):
        db.session.add(Comment(author=request.form['author'], text=request.form['comment_text']))
        db.session.commit()
    return get_comments_html()

@app.route('/save_match', methods=['POST'])
def save_match():
    data = request.json
    winners = data.get('winners', [])
    losers = data.get('losers', [])
    match_type = data.get('type') # 'Singles' or 'Doubles'

    # Update Winners
    for name in winners:
        p = Player.query.filter_by(name=name).first()
        if p:
            if match_type == 'Singles': p.singles_won += 1
            else: p.doubles_won += 1
    
    # Store match history (optional but good for debugging)
    score_str = f"Win" # Simplified for now
    db.session.add(MatchHistory(
        winner_names=",".join(winners), 
        loser_names=",".join(losers), 
        score=score_str, 
        match_type=match_type
    ))
    
    db.session.commit()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)