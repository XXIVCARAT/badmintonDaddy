from flask import Flask, url_for, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    # 1. HARDCODED RANKINGS DATA
    standings_data = [
        {"rank": 1, "name": "Suhal++ Chong Wei", "points": 1250, "win_rate": "92%"},
        {"rank": 2, "name": "Sujay Dan", "points": 1180, "win_rate": "88%"},
        {"rank": 3, "name": "Ourab Taufik", "points": 950, "win_rate": "75%"},
        {"rank": 4, "name": "Generic Player 1", "points": 800, "win_rate": "50%"},
    ]

    # Video file path
    video_url = url_for('static', filename='match_highlight.mp4')

    # CHANGED: Removed 'f' from here. Now it is just a normal string.
    # We use {{ video_url }} for Jinja to fill it in later.
    html_content = '''
    <!doctype html>
    <html lang="en" data-bs-theme="dark">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Badminton League</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #1a1a1a; color: white; font-family: sans-serif; }
            .custom-header { color: #ffcc00; text-shadow: 1px 1px 5px black; }
            .nav-tabs .nav-link.active { background-color: #ffcc00; color: black; border-color: #ffcc00; font-weight: bold; }
            .nav-tabs .nav-link { color: #ffcc00; }
            .highlight-card { border: 2px solid #ffcc00; background-color: #2c2c2c; }
        </style>
      </head>
      <body>
        
        <div class="container mt-5 text-center">
            <h1 class="mb-4 custom-header">🏸 The Badminton League 🏸</h1>

            <ul class="nav nav-tabs justify-content-center mb-4" id="myTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="announcements-tab" data-bs-toggle="tab" data-bs-target="#announcements" type="button" role="tab">Announcements</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="standings-tab" data-bs-toggle="tab" data-bs-target="#standings" type="button" role="tab">Standings</button>
                </li>
            </ul>

            <div class="tab-content" id="myTabContent">
                
                <div class="tab-pane fade show active" id="announcements" role="tabpanel">
                    <div class="alert alert-warning text-dark fw-bold fs-5" role="alert">
                        📢 Badminton Daddy wishes Ourab all the best for his GATE exam! 🎓
                    </div>

                    <div class="card highlight-card p-3 mx-auto" style="max-width: 700px;">
                        <h4 class="mb-3">🔥 Match of the Week 🔥</h4>
                        <div class="ratio ratio-16x9">
                            <video controls autoplay muted loop>
                                <source src="{{ video_url }}" type="video/mp4">
                                Your browser does not support the video tag.
                            </video>
                        </div>
                        <p class="mt-2 text-muted">Suhal++ vs Sujay Dan Highlights</p>
                    </div>
                </div>

                <div class="tab-pane fade" id="standings" role="tabpanel">
                    <div class="table-responsive mx-auto" style="max-width: 800px;">
                        <table class="table table-dark table-striped table-hover border-warning">
                            <thead>
                                <tr style="color: #ffcc00;">
                                    <th scope="col"># Rank</th>
                                    <th scope="col">Player Name</th>
                                    <th scope="col">Points</th>
                                    <th scope="col">Win Rate</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for player in rankings %}
                                <tr>
                                    <th scope="row">{{ player.rank }}</th>
                                    <td>{{ player.name }}</td>
                                    <td>{{ player.points }}</td>
                                    <td>{{ player.win_rate }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
      </body>
    </html>
    '''
    
    # CHANGED: We now pass video_url here
    return render_template_string(html_content, rankings=standings_data, video_url=video_url)

if __name__ == '__main__':
    app.run(debug=True)