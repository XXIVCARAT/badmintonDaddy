import os
import json
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
    doubles_won = db.Column(db.Integer, default=0)

class MatchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    winner_names = db.Column(db.String(200))
    loser_names = db.Column(db.String(200))
    score = db.Column(db.String(20))
    match_type = db.Column(db.String(10)) 

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
            db.session.commit()

init_db()

# --- HELPER FRAGMENTS ---
def get_rankings_html():
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
            <table class="table table-dark table-striped align-middle">
                <thead><tr class="border-warning"><th class="text-warning">#</th><th>Name</th><th class="text-warning text-end">Wins</th></tr></thead>
                <tbody>{% for p in s_ranks %}<tr><td class="text-warning">{{loop.index}}</td><td>{{p.name}}</td><td class="text-warning fw-bold text-end">{{p.singles_won}}</td></tr>{% endfor %}</tbody>
            </table>
        </div>
        <div id="doubles-table" class="table-responsive mx-auto d-none" style="max-width: 600px;">
            <table class="table table-dark table-striped align-middle">
                <thead><tr class="border-warning"><th class="text-warning">#</th><th>Name</th><th class="text-warning text-end">Wins</th></tr></thead>
                <tbody>{% for p in d_ranks %}<tr><td class="text-warning">{{loop.index}}</td><td>{{p.name}}</td><td class="text-warning fw-bold text-end">{{p.doubles_won}}</td></tr>{% endfor %}</tbody>
            </table>
        </div>
    ''', s_ranks=singles_rank, d_ranks=doubles_rank)

# --- MAIN ROUTE ---
@app.route('/')
def index():
    players = Player.query.order_by(Player.name).all()
    player_names = [p.name for p in players]

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
            
            /* COURT VISUALIZATION */
            .court-wrapper { perspective: 800px; margin: 20px auto; max-width: 400px; }
            .court { 
                background-color: #2c9e4b; 
                border: 4px solid white; 
                height: 300px; 
                position: relative; 
                display: grid; 
                grid-template-rows: 1fr 2px 1fr; /* Top, Net, Bottom */
            }
            .net { background: rgba(255,255,255,0.8); height: 100%; width: 100%; border-top: 2px dashed #ddd; border-bottom: 2px dashed #ddd;}
            .court-half { display: grid; grid-template-columns: 1fr 1fr; position: relative; }
            .service-box { border: 1px solid rgba(255,255,255,0.3); display: flex; align-items: center; justify-content: center; font-size: 0.8em; font-weight: bold; text-shadow: 0 1px 2px black; transition: all 0.3s; padding: 2px;}
            
            .active-server { background-color: rgba(255, 204, 0, 0.4); border: 2px solid #ffcc00; }
            .active-receiver { background-color: rgba(255, 0, 0, 0.2); }
            
            /* CONTROLS */
            .score-box { background: #333; border: 2px solid #555; border-radius: 10px; padding: 10px; text-align: center; cursor: pointer; }
            .score-box:active { background: #444; }
            .score-val { font-size: 3.5rem; font-weight: 800; line-height: 1; }
            .winner-glow { border-color: #00ff00 !important; box-shadow: 0 0 15px #00ff00; }
        </style>
      </head>
      <body>
        
        <div class="container mt-4 text-center mb-5">
            <h1 class="mb-3 custom-header">🏸 Badminton Daddy</h1>

            <ul class="nav nav-tabs justify-content-center mb-4" id="myTab" role="tablist">
                <li class="nav-item"><button class="nav-link active" data-bs-toggle="tab" data-bs-target="#standings">Standings</button></li>
                <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#scoreboard">Live Court</button></li>
                <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#manual">Direct Entry</button></li>
            </ul>

            <div class="tab-content">
                <div class="tab-pane fade show active" id="standings" hx-get="/update-rankings" hx-trigger="load, every 10s">
                    {{ rankings_html|safe }}
                </div>

                <div class="tab-pane fade" id="scoreboard">
                    <div class="container" style="max-width: 600px;">
                        
                        <div class="row g-2 mb-3 align-items-center bg-dark p-2 rounded">
                            <div class="col-6">
                                <select id="match-point-select" class="form-select form-select-sm bg-secondary text-white border-0">
                                    <option value="21" selected>Game to 21</option>
                                    <option value="11">Game to 11</option>
                                    <option value="7">Game to 7</option>
                                </select>
                            </div>
                            <div class="col-6">
                                <select id="game-mode-select" class="form-select form-select-sm bg-secondary text-white border-0" onchange="resetGame()">
                                    <option value="singles">Singles (1 vs 1)</option>
                                    <option value="doubles" selected>Doubles (2 vs 2)</option>
                                </select>
                            </div>
                        </div>

                        <div id="player-setup" class="card p-3 mb-3 bg-dark border-secondary">
                            <h6 class="text-warning">Who is playing?</h6>
                            <div class="row g-1 mb-2">
                                <div class="col-6"><input type="text" id="pA1" class="form-control form-control-sm" placeholder="Team A (Server)" list="pList"></div>
                                <div class="col-6"><input type="text" id="pB1" class="form-control form-control-sm" placeholder="Team B (Receiver)" list="pList"></div>
                            </div>
                            <div class="row g-1 mb-2 doubles-only">
                                <div class="col-6"><input type="text" id="pA2" class="form-control form-control-sm" placeholder="Team A Partner" list="pList"></div>
                                <div class="col-6"><input type="text" id="pB2" class="form-control form-control-sm" placeholder="Team B Partner" list="pList"></div>
                            </div>
                            <button class="btn btn-warning btn-sm w-100 fw-bold" onclick="startGame()">Start Match</button>
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
                            <h5 class="text-warning mb-3">Manual Match Entry</h5>
                            <p class="small text-muted">Use this to log matches played without the digital scoreboard.</p>
                            
                            <label class="text-success fw-bold">Winners</label>
                            <div class="row g-2 mb-3">
                                <div class="col-6"><input type="text" id="manual-w1" class="form-control" placeholder="Winner 1" list="pList"></div>
                                <div class="col-6"><input type="text" id="manual-w2" class="form-control" placeholder="Winner 2 (Opt)" list="pList"></div>
                            </div>

                            <label class="text-danger fw-bold">Losers</label>
                            <div class="row g-2 mb-3">
                                <div class="col-6"><input type="text" id="manual-l1" class="form-control" placeholder="Loser 1" list="pList"></div>
                                <div class="col-6"><input type="text" id="manual-l2" class="form-control" placeholder="Loser 2 (Opt)" list="pList"></div>
                            </div>

                            <button class="btn btn-warning w-100 fw-bold" onclick="submitManualMatch()">Submit Result</button>
                        </div>
                    </div>
                </div>

            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // --- STATE ---
            let state = {
                scoreA: 0, scoreB: 0,
                serverTeam: 'A', // 'A' or 'B'
                gamePoint: 21,
                mode: 'doubles', // 'singles' or 'doubles'
                players: { A1:'', A2:'', B1:'', B2:'' },
                // Positions: 0=Left, 1=Right. We track where Player 1 is.
                // In Badminton, players swap sides only when they win a point on THEIR serve.
                // We simplify: We just track "Right Service" vs "Left Service" based on score, 
                // and for Doubles we track the "Odd/Even Alignment".
                posA1: 1, // 1 = Right Box (Even), 0 = Left Box (Odd)
                posB1: 1,
                history: []
            };

            // --- CORE LOGIC ---
            function startGame() {
                state.mode = document.getElementById('game-mode-select').value;
                state.gamePoint = parseInt(document.getElementById('match-point-select').value);
                state.players.A1 = document.getElementById('pA1').value || 'A1';
                state.players.B1 = document.getElementById('pB1').value || 'B1';
                
                if(state.mode === 'doubles') {
                    state.players.A2 = document.getElementById('pA2').value || 'A2';
                    state.players.B2 = document.getElementById('pB2').value || 'B2';
                    document.getElementById('pos-A-L').innerText = state.players.A2; // Left
                    document.getElementById('pos-A-R').innerText = state.players.A1; // Right (Start Even)
                    document.getElementById('pos-B-L').innerText = state.players.B2; // Left (Inverted view)
                    document.getElementById('pos-B-R').innerText = state.players.B1; // Right
                } else {
                    state.players.A2 = ''; state.players.B2 = '';
                }

                document.getElementById('player-setup').classList.add('d-none');
                document.getElementById('active-game-area').classList.remove('d-none');
                updateCourt();
            }

            function resetGame() {
                if(state.scoreA > 0 || state.scoreB > 0) {
                    if(!confirm("Discard current game?")) return;
                }
                state.scoreA = 0; state.scoreB = 0; state.history = []; state.serverTeam = 'A';
                document.getElementById('player-setup').classList.remove('d-none');
                document.getElementById('active-game-area').classList.add('d-none');
                document.getElementById('save-btn-area').classList.add('d-none');
                document.getElementById('score-box-A').classList.remove('winner-glow');
                document.getElementById('score-box-B').classList.remove('winner-glow');
                
                // Toggle Inputs based on mode
                const mode = document.getElementById('game-mode-select').value;
                document.querySelectorAll('.doubles-only').forEach(el => el.style.display = mode === 'doubles' ? 'flex' : 'none');
            }

            function addPoint(team) {
                if(checkWin()) return;

                // 1. Record History
                state.history.push(JSON.parse(JSON.stringify(state))); // Deep copy

                // 2. Logic: If Server wins, they swap sides. If Receiver wins, they become server (no swap).
                const isServerWin = (team === state.serverTeam);

                if (team === 'A') state.scoreA++; else state.scoreB++;

                if (state.mode === 'doubles') {
                    if (isServerWin) {
                        // Serving team swaps sides
                        if (team === 'A') state.posA1 = 1 - state.posA1; // Toggle 0/1
                        else state.posB1 = 1 - state.posB1;
                    } else {
                        // Service Over. New server is the team that just won.
                        state.serverTeam = team;
                        // NO SWAP of positions.
                    }
                } else {
                    // Singles is simple: Server is always determined by score (Even=Right, Odd=Left)
                    state.serverTeam = team; 
                }

                if (navigator.vibrate) navigator.vibrate(50);
                updateCourt();
                checkWin();
            }

            function undoPoint() {
                if (state.history.length === 0) return;
                let last = state.history.pop();
                Object.assign(state, last); // Restore state
                document.getElementById('save-btn-area').classList.add('d-none');
                document.getElementById('score-box-A').classList.remove('winner-glow');
                document.getElementById('score-box-B').classList.remove('winner-glow');
                updateCourt();
            }

            function forceSwapPositions() {
                // Manual override if players get confused
                if(state.serverTeam === 'A') state.posA1 = 1 - state.posA1;
                else state.posB1 = 1 - state.posB1;
                updateCourt();
            }

            function updateCourt() {
                // update Scores
                document.getElementById('scoreA').innerText = state.scoreA;
                document.getElementById('scoreB').innerText = state.scoreB;

                const sA = state.scoreA;
                const sB = state.scoreB;

                // --- VISUAL POSITIONS ---
                const aBoxL = document.getElementById('pos-A-L');
                const aBoxR = document.getElementById('pos-A-R');
                const bBoxL = document.getElementById('pos-B-L');
                const bBoxR = document.getElementById('pos-B-R');
                
                // Clear Highlights
                [aBoxL, aBoxR, bBoxL, bBoxR].forEach(el => el.className = 'service-box');

                if (state.mode === 'singles') {
                    // Singles: Position is purely based on score
                    // Team A
                    aBoxL.innerText = (sA % 2 !== 0) ? state.players.A1 : '';
                    aBoxR.innerText = (sA % 2 === 0) ? state.players.A1 : '';
                    // Team B
                    bBoxL.innerText = (sB % 2 !== 0) ? state.players.B1 : '';
                    bBoxR.innerText = (sB % 2 === 0) ? state.players.B1 : '';

                    // Highlight Active Server
                    if(state.serverTeam === 'A') {
                        if(sA % 2 === 0) aBoxR.classList.add('active-server'); else aBoxL.classList.add('active-server');
                    } else {
                        if(sB % 2 === 0) bBoxR.classList.add('active-server'); else bBoxL.classList.add('active-server');
                    }

                } else {
                    // Doubles: Based on tracked position (posA1: 1=Right, 0=Left)
                    const pA1 = state.players.A1; const pA2 = state.players.A2;
                    const pB1 = state.players.B1; const pB2 = state.players.B2;

                    // Render Names based on current state alignment
                    if(state.posA1 === 1) { aBoxR.innerText = pA1; aBoxL.innerText = pA2; } 
                    else { aBoxL.innerText = pA1; aBoxR.innerText = pA2; }

                    if(state.posB1 === 1) { bBoxR.innerText = pB1; bBoxL.innerText = pB2; } 
                    else { bBoxL.innerText = pB1; bBoxR.innerText = pB2; }

                    // Highlight Server Box
                    const servingScore = (state.serverTeam === 'A') ? sA : sB;
                    const isEven = (servingScore % 2 === 0);
                    
                    // In badminton, Even score serves from Right box, Odd serves from Left box.
                    if(state.serverTeam === 'A') {
                        if(isEven) aBoxR.classList.add('active-server'); else aBoxL.classList.add('active-server');
                    } else {
                        if(isEven) bBoxR.classList.add('active-server'); else bBoxL.classList.add('active-server');
                    }
                }
            }

            function checkWin() {
                const sA = state.scoreA;
                const sB = state.scoreB;
                const limit = state.gamePoint;
                let winner = null;

                // Max point cap (usually 30 for 21 games, but let's say limit+9 for custom)
                const hardCap = limit + 9; 

                if ((sA >= limit && sA >= sB + 2) || sA === hardCap) winner = 'A';
                if ((sB >= limit && sB >= sA + 2) || sB === hardCap) winner = 'B';

                if (winner) {
                    document.getElementById('save-btn-area').classList.remove('d-none');
                    document.getElementById('score-box-' + winner).classList.add('winner-glow');
                    return true;
                }
                return false;
            }

            // --- SAVING ---
            function saveLiveMatch() {
                const winners = (state.scoreA > state.scoreB) 
                    ? [state.players.A1, state.players.A2].filter(Boolean)
                    : [state.players.B1, state.players.B2].filter(Boolean);
                
                const losers = (state.scoreA > state.scoreB)
                    ? [state.players.B1, state.players.B2].filter(Boolean)
                    : [state.players.A1, state.players.A2].filter(Boolean);

                sendMatchData(winners, losers, state.mode);
            }

            function submitManualMatch() {
                const w1 = document.getElementById('manual-w1').value;
                const w2 = document.getElementById('manual-w2').value;
                const l1 = document.getElementById('manual-l1').value;
                const l2 = document.getElementById('manual-l2').value;

                if(!w1 || !l1) return alert("Need at least 1 winner and 1 loser");

                const winners = [w1, w2].filter(Boolean);
                const losers = [l1, l2].filter(Boolean);
                const type = (winners.length > 1) ? 'doubles' : 'singles';

                sendMatchData(winners, losers, type);
            }

            function sendMatchData(winners, losers, type) {
                fetch('/save_match', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ winners, losers, type })
                }).then(r => r.json()).then(d => {
                    alert("Match Saved!");
                    window.location.reload();
                });
            }
        </script>
      </body>
    </html>
    '''
    return render_template_string(html_content, rankings_html=get_rankings_html(), player_names=player_names)

# --- SAVE ROUTE ---
@app.route('/save_match', methods=['POST'])
def save_match():
    data = request.json
    winners = data.get('winners', [])
    losers = data.get('losers', [])
    match_type = 'Singles' if len(winners) == 1 else 'Doubles'

    for name in winners:
        p = Player.query.filter_by(name=name).first()
        if p:
            if match_type == 'Singles': p.singles_won += 1
            else: p.doubles_won += 1
            
    db.session.add(MatchHistory(winner_names=",".join(winners), loser_names=",".join(losers), match_type=match_type))
    db.session.commit()
    return jsonify({'status': 'success'})

# --- OTHER ROUTES (Rankings, etc) ---
@app.route('/update-rankings')
def r_rankings(): return get_rankings_html()

if __name__ == '__main__':
    app.run(debug=True)