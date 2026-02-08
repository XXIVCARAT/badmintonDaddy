import os
import json
import sqlite3
from flask import Flask, url_for, render_template_string, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
db_url = os.environ.get('DATABASE_URL')
# Handle Render/Heroku Postgres URL oddities if needed
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELS ---
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    # Singles Stats
    singles_played = db.Column(db.Integer, default=0)
    singles_won = db.Column(db.Integer, default=0)
    singles_lost = db.Column(db.Integer, default=0)
    
    # Doubles Stats
    doubles_played = db.Column(db.Integer, default=0)
    doubles_won = db.Column(db.Integer, default=0)
    doubles_lost = db.Column(db.Integer, default=0)

class MatchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    winner_names = db.Column(db.String(200))
    loser_names = db.Column(db.String(200))
    score = db.Column(db.String(20))
    match_type = db.Column(db.String(10)) 
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class LikeCounter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50), nullable=False)
    text = db.Column(db.String(500), nullable=False)

# --- MIGRATION & INIT ---
def run_migrations():
    """
    Checks if new columns exist; if not, adds them.
    This allows you to keep existing data while upgrading the code.
    """
    with app.app_context():
        inspector = db.inspect(db.engine)
        # Check if table exists first
        if not inspector.has_table('player'):
            return

        columns = [c['name'] for c in inspector.get_columns('player')]
        
        # List of new columns to check/add
        new_cols = [
            ('singles_played', 'INTEGER DEFAULT 0'),
            ('singles_lost', 'INTEGER DEFAULT 0'),
            ('doubles_played', 'INTEGER DEFAULT 0'),
            ('doubles_lost', 'INTEGER DEFAULT 0')
        ]
        
        with db.engine.connect() as conn:
            for col_name, col_type in new_cols:
                if col_name not in columns:
                    print(f"Migrating: Adding {col_name} to Player table...")
                    conn.execute(text(f'ALTER TABLE player ADD COLUMN {col_name} {col_type}'))
                    conn.commit()

def init_db():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Run migration to add columns to existing DB if needed
        run_migrations()

        # Seed Initial Players if empty
        if not Player.query.first():
            initial_players = [
                "Manan", "Ourab", "Anuj", "Suhal", "Sujay", "Harshil", 
                "Shreyas", "Ishita", "Idhant", "Chirag", "Nirlep", "Ameya"
            ]
            for name in initial_players:
                # Initialize explicitly with 0s to avoid NoneType errors
                db.session.add(Player(
                    name=name,
                    singles_played=0, singles_won=0, singles_lost=0,
                    doubles_played=0, doubles_won=0, doubles_lost=0
                ))
            
            # Init Likes
            if not LikeCounter.query.first():
                db.session.add(LikeCounter(count=0))
            
            db.session.commit()

init_db()

# --- HTMX FRAGMENTS ---

def get_rankings_html():
    singles_rank = Player.query.order_by(Player.singles_won.desc(), Player.singles_played.asc()).all()
    doubles_rank = Player.query.order_by(Player.doubles_won.desc(), Player.doubles_played.asc()).all()
    
    # Template for a single row to keep things DRY
    table_header = '''
    <thead>
        <tr class="border-warning">
            <th class="text-warning">#</th>
            <th>Name</th>
            <th class="text-center text-muted small">Played</th>
            <th class="text-center text-warning">Won</th>
            <th class="text-center text-danger">Lost</th>
        </tr>
    </thead>
    '''
    
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
            <table class="table table-dark table-striped align-middle table-sm">
                ''' + table_header + '''
                <tbody>
                    {% for p in s_ranks %}
                    <tr>
                        <td class="text-warning fw-bold">{{loop.index}}</td>
                        <td>{{p.name}}</td>
                        <td class="text-center text-muted">{{p.singles_played}}</td>
                        <td class="text-center text-warning fw-bold">{{p.singles_won}}</td>
                        <td class="text-center text-danger">{{p.singles_lost}}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div id="doubles-table" class="table-responsive mx-auto d-none" style="max-width: 600px;">
            <table class="table table-dark table-striped align-middle table-sm">
                ''' + table_header + '''
                <tbody>
                    {% for p in d_ranks %}
                    <tr>
                        <td class="text-warning fw-bold">{{loop.index}}</td>
                        <td>{{p.name}}</td>
                        <td class="text-center text-muted">{{p.doubles_played}}</td>
                        <td class="text-center text-warning fw-bold">{{p.doubles_won}}</td>
                        <td class="text-center text-danger">{{p.doubles_lost}}</td>
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
        <button id="like-btn" hx-post="/like" hx-swap="outerHTML" class="btn btn-outline-warning rounded-pill px-4 py-2 fw-bold">
            <i class="fa-solid fa-heart me-2"></i> Like <span class="badge bg-warning text-dark ms-2">{{ likes }}</span>
        </button>
    ''', likes=likes)

def get_comments_html():
    comments = Comment.query.order_by(Comment.id.desc()).all()
    return render_template_string('''
        <div id="comments-list" class="comments-list" style="max-height: 300px; overflow-y: auto;"
             hx-get="/update-comments" hx-trigger="every 5s" hx-swap="outerHTML">
            {% if comments|length == 0 %}
                <p class="text-muted small fst-italic">No wishes yet.</p>
            {% else %}
                {% for comment in comments %}
                <div class="comment-box mb-2 p-2 rounded border-start border-warning border-4 bg-dark">
                    <div class="text-warning fw-bold small">{{ comment.author }}</div>
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
    # NOTE: You need a gif in a static folder, or change this to an external URL
    gif_url = url_for('static', filename='my_cool_gif.gif') 
    
    # Fallback if static file not found, use a placeholder
    if not os.path.exists(os.path.join(app.root_path, 'static', 'my_cool_gif.gif')):
        gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcDdtY254YmF5eW52YmF5eW52YmF5eW52YmF5eW52YmF5eW52eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKSjRrfPHwSHaTu/giphy.gif"

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
            
            /* Court Visuals */
            .court-wrapper { perspective: 800px; margin: 20px auto; max-width: 400px; }
            .court { background-color: #2c9e4b; border: 4px solid white; height: 300px; position: relative; display: grid; grid-template-rows: 1fr 2px 1fr; }
            .net { background: rgba(255,255,255,0.8); height: 100%; width: 100%; border-top: 2px dashed #ddd; border-bottom: 2px dashed #ddd;}
            .court-half { display: grid; grid-template-columns: 1fr 1fr; position: relative; }
            .service-box { border: 1px solid rgba(255,255,255,0.3); display: flex; align-items: center; justify-content: center; font-size: 0.8em; font-weight: bold; text-shadow: 0 1px 2px black; transition: all 0.3s; padding: 2px;}
            .active-server { background-color: rgba(255, 204, 0, 0.4); border: 2px solid #ffcc00; }
            .active-receiver { background-color: rgba(255, 0, 0, 0.2); }
            
            /* Controls */
            .score-box { background: #333; border: 2px solid #555; border-radius: 10px; padding: 10px; text-align: center; cursor: pointer; }
            .score-box:active { background: #444; }
            .score-val { font-size: 3.5rem; font-weight: 800; line-height: 1; }
            .winner-glow { border-color: #00ff00 !important; box-shadow: 0 0 15px #00ff00; }
            
            /* Wish Card */
            .wish-card { border: 2px solid #ffcc00; background-color: #252525; border-radius: 15px; }
        </style>
      </head>
      <body>
        
        <div class="container mt-4 text-center mb-5">
            <h1 class="mb-3 custom-header">🏸 Badminton Daddy</h1>

            <ul class="nav nav-tabs justify-content-center mb-4" id="myTab" role="tablist">
                <li class="nav-item"><button class="nav-link active" data-bs-toggle="tab" data-bs-target="#standings">Standings</button></li>
                <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#announcements">Wishes</button></li>
                <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#scoreboard">Live Match</button></li>
                <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#manual">Manual Entry</button></li>
            </ul>

            <div class="tab-content">
                <div class="tab-pane fade show active" id="standings" hx-get="/update-rankings" hx-trigger="load, every 10s">
                    {{ rankings_html|safe }}
                </div>
                
                <div class="tab-pane fade" id="announcements">
                    <div class="container" style="max-width: 600px;">
                        <div class="card wish-card p-3 mb-4">
                            <h4 class="text-white mb-3">Best of Luck <span class="text-warning">Ourab!</span> 🎓</h4>
                            <div class="mb-3"><img src="{{ gif_url }}" class="img-fluid rounded" style="max-width: 100%; border: 1px solid white;"></div>
                            
                            <div class="d-inline-block mb-3" hx-get="/update-likes" hx-trigger="every 5s" hx-swap="innerHTML">
                                {{ like_html|safe }}
                            </div>

                            <div class="text-start mt-2">
                                <h6 class="text-secondary border-bottom pb-2 mb-2">Leave a Wish</h6>
                                <form hx-post="/comment" hx-target="#comments-list" hx-swap="outerHTML" class="row g-2 mb-3" onsubmit="setTimeout(()=>this.reset(), 100);">
                                    <div class="col-4"><input type="text" name="author" class="form-control form-control-sm bg-dark text-white border-secondary" placeholder="Name" required></div>
                                    <div class="col-6"><input type="text" name="comment_text" class="form-control form-control-sm bg-dark text-white border-secondary" placeholder="Message..." required></div>
                                    <div class="col-2"><button type="submit" class="btn btn-sm btn-warning w-100 fw-bold"><i class="fa-solid fa-paper-plane"></i></button></div>
                                </form>
                                {{ comments_html|safe }}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="tab-pane fade" id="scoreboard">
                    <div class="container" style="max-width: 600px;">
                        
                        <div class="row g-2 mb-3 align-items-center bg-dark p-2 rounded mx-1">
                            <div class="col-6">
                                <select id="match-point-select" class="form-select form-select-sm bg-secondary text-white border-0">
                                    <option value="21" selected>Target: 21</option>
                                    <option value="11">Target: 11</option>
                                    <option value="7">Target: 7</option>
                                </select>
                            </div>
                            <div class="col-6">
                                <select id="game-mode-select" class="form-select form-select-sm bg-secondary text-white border-0" onchange="resetGame()">
                                    <option value="singles">Singles</option>
                                    <option value="doubles" selected>Doubles</option>
                                </select>
                            </div>
                        </div>

                        <div id="player-setup" class="card p-3 mb-3 bg-dark border-secondary">
                            <h6 class="text-warning">New Match Setup</h6>
                            <div class="row g-1 mb-2">
                                <div class="col-6"><input type="text" id="pA1" class="form-control form-control-sm" placeholder="Team A (Server)" list="pList"></div>
                                <div class="col-6"><input type="text" id="pB1" class="form-control form-control-sm" placeholder="Team B (Receiver)" list="pList"></div>
                            </div>
                            <div class="row g-1 mb-2 doubles-only">
                                <div class="col-6"><input type="text" id="pA2" class="form-control form-control-sm" placeholder="Team A Partner" list="pList"></div>
                                <div class="col-6"><input type="text" id="pB2" class="form-control form-control-sm" placeholder="Team B Partner" list="pList"></div>
                            </div>
                            <button class="btn btn-warning btn-sm w-100 fw-bold" onclick="startGame()">Start Game</button>
                            <datalist id="pList">{% for name in player_names %}<option value="{{name}}">{% endfor %}</datalist>
                        </div>

                        <div id="active-game-area" class="d-none">
                            <div class="court-wrapper">
                                <div class="court">
                                    <div class="court-half">
                                        <div id="pos-A-L" class="service-box">A (L)</div>
                                        <div id="pos-A-R" class="service-box">A (R)</div>
                                    </div>
                                    <div class="net d-flex align-items-center justify-content-center text-dark fw-bold small">NET</div>
                                    <div class="court-half">
                                        <div id="pos-B-L" class="service-box">B (L)</div>
                                        <div id="pos-B-R" class="service-box">B (R)</div>
                                    </div>
                                </div>
                            </div>

                            <div class="row mb-3">
                                <div class="col-6">
                                    <div id="score-box-A" class="score-box" onclick="addPoint('A')">
                                        <div class="text-secondary small">TEAM A</div>
                                        <div id="scoreA" class="score-val text-white">0</div>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div id="score-box-B" class="score-box" onclick="addPoint('B')">
                                        <div class="text-secondary small">TEAM B</div>
                                        <div id="scoreB" class="score-val text-warning">0</div>
                                    </div>
                                </div>
                            </div>

                            <div class="d-flex justify-content-between">
                                <button class="btn btn-secondary btn-sm" onclick="undoPoint()"><i class="fa-solid fa-rotate-left"></i> Undo</button>
                                <button class="btn btn-outline-light btn-sm" onclick="forceSwapPositions()"><i class="fa-solid fa-arrows-rotate"></i> Man. Swap</button>
                                <button class="btn btn-danger btn-sm" onclick="resetGame()"><i class="fa-solid fa-xmark"></i> Quit</button>
                            </div>
                        </div>

                        <div id="save-btn-area" class="mt-3 d-none">
                            <button class="btn btn-success w-100 fw-bold py-3" onclick="saveLiveMatch()">
                                <i class="fa-solid fa-trophy"></i> GAME OVER - SAVE
                            </button>
                        </div>
                    </div>
                </div>

                <div class="tab-pane fade" id="manual">
                    <div class="container" style="max-width: 600px;">
                        <div class="card bg-dark border-warning p-3">
                            <h5 class="text-warning mb-3">Quick Result Entry</h5>
                            <label class="text-success fw-bold small">Winners</label>
                            <div class="row g-2 mb-3">
                                <div class="col-6"><input type="text" id="manual-w1" class="form-control form-control-sm" placeholder="Winner 1" list="pList"></div>
                                <div class="col-6"><input type="text" id="manual-w2" class="form-control form-control-sm" placeholder="Winner 2 (Opt)" list="pList"></div>
                            </div>
                            <label class="text-danger fw-bold small">Losers</label>
                            <div class="row g-2 mb-3">
                                <div class="col-6"><input type="text" id="manual-l1" class="form-control form-control-sm" placeholder="Loser 1" list="pList"></div>
                                <div class="col-6"><input type="text" id="manual-l2" class="form-control form-control-sm" placeholder="Loser 2 (Opt)" list="pList"></div>
                            </div>
                            <button class="btn btn-warning w-100 fw-bold" onclick="submitManualMatch()">Submit Result</button>
                        </div>
                    </div>
                </div>

            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // --- STATE & GAME LOGIC ---
            let state = {
                scoreA: 0, scoreB: 0,
                serverTeam: 'A',
                gamePoint: 21,
                mode: 'doubles',
                players: { A1:'', A2:'', B1:'', B2:'' },
                posA1: 1, posB1: 1, // 1=Right(Even), 0=Left(Odd)
                history: []
            };

            function startGame() {
                state.mode = document.getElementById('game-mode-select').value;
                state.gamePoint = parseInt(document.getElementById('match-point-select').value);
                state.players.A1 = document.getElementById('pA1').value || 'A1';
                state.players.B1 = document.getElementById('pB1').value || 'B1';
                if(state.mode === 'doubles') {
                    state.players.A2 = document.getElementById('pA2').value || 'A2';
                    state.players.B2 = document.getElementById('pB2').value || 'B2';
                } else { state.players.A2 = ''; state.players.B2 = ''; }
                
                // Reset positions for new game
                state.posA1 = 1; state.posB1 = 1;

                document.getElementById('player-setup').classList.add('d-none');
                document.getElementById('active-game-area').classList.remove('d-none');
                updateCourt();
            }

            function resetGame() {
                if(state.scoreA > 0 || state.scoreB > 0) { if(!confirm("Discard current game?")) return; }
                state.scoreA = 0; state.scoreB = 0; state.history = []; state.serverTeam = 'A';
                document.getElementById('player-setup').classList.remove('d-none');
                document.getElementById('active-game-area').classList.add('d-none');
                document.getElementById('save-btn-area').classList.add('d-none');
                document.getElementById('score-box-A').classList.remove('winner-glow');
                document.getElementById('score-box-B').classList.remove('winner-glow');
                const mode = document.getElementById('game-mode-select').value;
                document.querySelectorAll('.doubles-only').forEach(el => el.style.display = mode === 'doubles' ? 'flex' : 'none');
            }

            function addPoint(team) {
                if(checkWin()) return;
                state.history.push(JSON.parse(JSON.stringify(state)));
                
                const isServerWin = (team === state.serverTeam);
                if (team === 'A') state.scoreA++; else state.scoreB++;

                if (state.mode === 'doubles') {
                    if (isServerWin) {
                        // Same server continues, swaps sides
                        if (team === 'A') state.posA1 = 1 - state.posA1; else state.posB1 = 1 - state.posB1;
                    } else {
                        // Service over, no swap
                        state.serverTeam = team;
                    }
                } else {
                    state.serverTeam = team; 
                }
                
                if (navigator.vibrate) navigator.vibrate(50);
                updateCourt();
                checkWin();
            }

            function undoPoint() {
                if (state.history.length === 0) return;
                let last = state.history.pop();
                Object.assign(state, last);
                document.getElementById('save-btn-area').classList.add('d-none');
                document.getElementById('score-box-A').classList.remove('winner-glow');
                document.getElementById('score-box-B').classList.remove('winner-glow');
                updateCourt();
            }

            function forceSwapPositions() {
                if(state.serverTeam === 'A') state.posA1 = 1 - state.posA1; else state.posB1 = 1 - state.posB1;
                updateCourt();
            }

            function updateCourt() {
                document.getElementById('scoreA').innerText = state.scoreA;
                document.getElementById('scoreB').innerText = state.scoreB;
                const sA = state.scoreA; const sB = state.scoreB;
                const aBoxL = document.getElementById('pos-A-L'); const aBoxR = document.getElementById('pos-A-R');
                const bBoxL = document.getElementById('pos-B-L'); const bBoxR = document.getElementById('pos-B-R');
                [aBoxL, aBoxR, bBoxL, bBoxR].forEach(el => el.className = 'service-box');

                if (state.mode === 'singles') {
                    aBoxL.innerText = (sA%2!==0)?state.players.A1:''; aBoxR.innerText = (sA%2===0)?state.players.A1:'';
                    bBoxL.innerText = (sB%2!==0)?state.players.B1:''; bBoxR.innerText = (sB%2===0)?state.players.B1:'';
                    if(state.serverTeam === 'A') (sA%2===0)?aBoxR.classList.add('active-server'):aBoxL.classList.add('active-server');
                    else (sB%2===0)?bBoxR.classList.add('active-server'):bBoxL.classList.add('active-server');
                } else {
                    const pA1 = state.players.A1; const pA2 = state.players.A2;
                    const pB1 = state.players.B1; const pB2 = state.players.B2;
                    if(state.posA1===1){aBoxR.innerText=pA1;aBoxL.innerText=pA2;}else{aBoxL.innerText=pA1;aBoxR.innerText=pA2;}
                    if(state.posB1===1){bBoxR.innerText=pB1;bBoxL.innerText=pB2;}else{bBoxL.innerText=pB1;bBoxR.innerText=pB2;}
                    
                    const servingScore = (state.serverTeam === 'A') ? sA : sB;
                    if(state.serverTeam === 'A') (servingScore%2===0)?aBoxR.classList.add('active-server'):aBoxL.classList.add('active-server');
                    else (servingScore%2===0)?bBoxR.classList.add('active-server'):bBoxL.classList.add('active-server');
                }
            }

            function checkWin() {
                const sA = state.scoreA; const sB = state.scoreB; const limit = state.gamePoint;
                let winner = null;
                const hardCap = limit + 9;
                if ((sA >= limit && sA >= sB + 2) || sA === hardCap) winner = 'A';
                if ((sB >= limit && sB >= sA + 2) || sB === hardCap) winner = 'B';
                if (winner) {
                    document.getElementById('save-btn-area').classList.remove('d-none');
                    document.getElementById('score-box-'+winner).classList.add('winner-glow');
                    return true;
                }
                return false;
            }

            function saveLiveMatch() {
                const winners = (state.scoreA > state.scoreB) ? [state.players.A1, state.players.A2] : [state.players.B1, state.players.B2];
                const losers = (state.scoreA > state.scoreB) ? [state.players.B1, state.players.B2] : [state.players.A1, state.players.A2];
                sendMatchData(winners.filter(Boolean), losers.filter(Boolean), state.mode);
            }

            function submitManualMatch() {
                const w1 = document.getElementById('manual-w1').value; const w2 = document.getElementById('manual-w2').value;
                const l1 = document.getElementById('manual-l1').value; const l2 = document.getElementById('manual-l2').value;
                if(!w1 || !l1) return alert("Enter winner and loser");
                const winners = [w1, w2].filter(Boolean); const losers = [l1, l2].filter(Boolean);
                sendMatchData(winners, losers, (winners.length > 1) ? 'doubles' : 'singles');
            }

            function sendMatchData(winners, losers, type) {
                fetch('/save_match', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ winners, losers, type })
                })
                .then(response => {
                    if (!response.ok) { throw new Error("Network response was not ok"); }
                    return response.json();
                })
                .then(d => { 
                    alert("Match Saved!"); 
                    window.location.reload(); 
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert("Failed to save match. Check console.");
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

# --- ROUTES ---

@app.route('/update-rankings')
def r_rankings(): return get_rankings_html()

@app.route('/update-likes')
def r_likes(): return get_likes_html()

@app.route('/update-comments')
def r_comments(): return get_comments_html()

@app.route('/like', methods=['POST'])
def like():
    l = LikeCounter.query.first()
    if l:
        l.count += 1
        db.session.commit()
    return get_likes_html()

@app.route('/comment', methods=['POST'])
def comment():
    if request.form.get('author') and request.form.get('comment_text'):
        db.session.add(Comment(author=request.form['author'], text=request.form['comment_text']))
        db.session.commit()
    return get_comments_html()

# --- FIXED SAVE MATCH ROUTE ---
@app.route('/save_match', methods=['POST'])
def save_match():
    data = request.json
    winners = data.get('winners', [])
    losers = data.get('losers', [])
    match_type = data.get('type', 'singles')
    
    # Determine if double or singles from input or data length
    is_doubles = (match_type == 'doubles') or (len(winners) > 1) or (len(losers) > 1)

    # HELPER: Get player or create with explicit zeroed stats
    def get_or_create_player(name):
        p = Player.query.filter_by(name=name).first()
        if not p:
            p = Player(
                name=name,
                singles_played=0, singles_won=0, singles_lost=0,
                doubles_played=0, doubles_won=0, doubles_lost=0
            )
            db.session.add(p)
        return p

    # Update Winners
    for name in winners:
        p = get_or_create_player(name)
        if is_doubles:
            p.doubles_won += 1
            p.doubles_played += 1
        else:
            p.singles_won += 1
            p.singles_played += 1
            
    # Update Losers
    for name in losers:
        p = get_or_create_player(name)
        if is_doubles:
            p.doubles_lost += 1
            p.doubles_played += 1
        else:
            p.singles_lost += 1
            p.singles_played += 1
            
    # Record History
    w_str = ",".join(winners)
    l_str = ",".join(losers)
    
    # Add history entry
    hist = MatchHistory(
        winner_names=w_str, 
        loser_names=l_str, 
        match_type=match_type,
        score="Manual" # No score in manual entry, use placeholder
    )
    db.session.add(hist)
    
    try:
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)