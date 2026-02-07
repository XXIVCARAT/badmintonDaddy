from flask import Flask, url_for, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    # 1. HARDCODED RANKINGS DATA
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

    # 2. LOAD STATIC FILES
    # Make sure 'my_cool_gif.gif' is inside the 'static' folder
    gif_url = url_for('static', filename='my_cool_gif.gif')

    # HTML TEMPLATE
    html_content = '''
    <!doctype html>
    <html lang="en" data-bs-theme="dark">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Badminton Daddy</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #1a1a1a; color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            .custom-header { color: #ffcc00; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; }
            
            /* Tab Styling */
            .nav-tabs .nav-link.active { background-color: #ffcc00; color: black; border-color: #ffcc00; font-weight: bold; }
            .nav-tabs .nav-link { color: #ffcc00; margin-right: 5px; border: 1px solid #333; }
            .nav-tabs { border-bottom: 2px solid #ffcc00; }
            
            /* Table Styling */
            .table-custom { border: 1px solid #444; }
            .rank-col { color: #ffcc00; font-weight: bold; font-size: 1.2em; }
            
            /* Announcement Styling */
            .wish-card { border: 4px solid #ffcc00; background-color: #2c2c2c; border-radius: 20px; box-shadow: 0 0 20px rgba(255, 204, 0, 0.3); }
            .wish-text { font-size: 2rem; color: #fff; font-weight: bold; line-height: 1.4; }
            .highlight-name { color: #ffcc00; text-decoration: underline; }
        </style>
      </head>
      <body>
        
        <div class="container mt-5 text-center">
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
                        
                        <div class="card wish-card p-5 mb-4">
                            <p class="wish-text">
                                Badminton Daddy wishes <br>
                                <span class="highlight-name">Ourab</span> <br>
                                All the Best for his <br>
                                <span style="color: #00d4ff;">GATE Exam!</span> 🎓
                            </p>
                            
                            <div class="mt-4">
                                <img src="{{ gif_url }}" alt="Good Luck GIF" class="img-fluid rounded" style="border: 2px solid white; max-width: 100%;">
                            </div>
                        </div>

                    </div>
                </div>

            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
      </body>
    </html>
    '''
    
    # PASS THE GIF URL HERE
    return render_template_string(html_content, rankings=standings_data, gif_url=gif_url)

if __name__ == '__main__':
    app.run(debug=True)