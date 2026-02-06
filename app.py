from flask import Flask, url_for

app = Flask(__name__)

@app.route('/')
def hello_world():
    video_url = url_for('static', filename='match_highlight.mp4')
    
    return f'''
    <html>
        <body style="text-align: center; background-color: #1a1a1a; color: white; font-family: sans-serif;">
            <h1>Suhal Chong Wei</h1>
            <h2 style="color: #ffcc00;">Vs</h2>
            <h1>Sujay Dan</h1>
            
            <div style="margin-top: 20px;">
                <video width="640" height="360" controls autoplay muted loop style="border: 5px solid #ffcc00; border-radius: 15px;">
                    <source src="{video_url}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            
            <p style="margin-top: 15px;">Match Highlights Loading...</p>
        </body>
    </html>
    '''