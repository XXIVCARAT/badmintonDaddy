# Badminton Daddy 🏸

A modern Flask web application for tracking badminton matches, maintaining player rankings, and managing live scoreboard tracking for singles and doubles matches.

## Features

- **Live Scoreboard**: Track singles and doubles matches in real-time with court position visualization
- **Player Rankings**: View player statistics, win-loss records, and rankings for various match types
- **Match Recording**: Quick manual entry for match results or automatic tracking through the live scoreboard
- **Community Features**: Like counter and wish messages for special occasions
- **Responsive Design**: Dark-themed UI with Bootstrap 5, optimized for mobile devices
- **HTMX Integration**: Real-time UI updates without page reloads

## Project Structure

```
badmintonDaddy/
├── app.py                 # Application factory and entry point
├── config.py              # Configuration management
├── models.py              # SQLAlchemy database models
├── database.py            # Database initialization and migrations
├── routes.py              # Flask blueprints for all routes
├── requirements.txt       # Project dependencies
├── .env.example           # Environment variables template
│
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Base template with styling
│   ├── index.html         # Main page layout
│   └── fragments/         # HTMX template fragments
│       ├── rankings.html
│       ├── likes.html
│       ├── comments.html
│       ├── wishes.html
│       ├── scoreboard.html
│       └── manual_entry.html
│
└── static/                # Static assets
    ├── my_cool_gif.gif
    └── js/
        └── game.js        # Game logic and UI control
```

## Setup & Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, defaults to SQLite for development)

### Development Setup

1. **Clone and setup environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   python app.py
   ```

## Technology Stack

- **Backend**: Flask 2.3, SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Interactivity**: HTMX
- **Database**: PostgreSQL (production) / SQLite (development)

## Database Models

- **Player**: Individual player statistics (singles/doubles)
- **MatchHistory**: Match results and history
- **LikeCounter**: Likes on wish card
- **Comment**: User wishes and messages

## Deployment

### To Render.com

1. Push to GitHub
2. Connect on Render and set environment variables:
   - `DATABASE_URL=<postgresql-string>`
   - `FLASK_ENV=production`
   - `SECRET_KEY=<random-secret>`
3. Deploy!

Guide: https://render.com/docs/deploy-flask
