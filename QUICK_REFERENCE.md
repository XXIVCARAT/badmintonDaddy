Quick Reference Card for Refactored Badminton Daddy Project
===============================================================

PROJECT STRUCTURE
─────────────────
badmintonDaddy/
├── app.py              → Application factory & entry point (45 lines)
├── config.py           → Configuration classes (35 lines)
├── models.py           → SQLAlchemy models (80 lines)
├── database.py         → DB init & migrations (60 lines)
├── routes.py           → Flask blueprints (150 lines)
├── wsgi.py             → Gunicorn entry point
├── verify_setup.py     → Verification script
├── requirements.txt    → Dependencies (with versions)
├── .env.example        → Environment template
├── README.md           → Project overview
├── DEVELOPMENT.md      → Developer guide
├── REFACTORING_SUMMARY.md → Changes documentation
│
├── templates/
│   ├── base.html       → Shared layout & styling
│   ├── index.html      → Main page
│   └── fragments/
│       ├── rankings.html    → Standings tables
│       ├── wishes.html      → Wish card
│       ├── likes.html       → Like button
│       ├── comments.html    → Comments list
│       ├── scoreboard.html  → Match tracking
│       └── manual_entry.html → Quick entry
│
└── static/
    ├── my_cool_gif.gif
    └── js/
        └── game.js     → Game logic (300 lines)


KEY FILES & RESPONSIBILITIES
─────────────────────────────

app.py (ENTRY POINT)
  • create_app() factory function
  • Blueprint registration
  • Database initialization
  • Run:  python app.py

config.py (CONFIGURATION)
  • Config, DevelopmentConfig, ProductionConfig
  • Environment variables
  • Database URI setup

models.py (DATABASE)
  • Player (with statistics properties)
  • MatchHistory (match records)
  • LikeCounter (wish card likes)
  • Comment (user wishes)

database.py (INITIALIZATION)
  • run_migrations() - Schema updates
  • init_db() - Create tables & seed data
  • reset_db() - Refresh database

routes.py (API)
  • main_bp blueprint (/, /comment, /like, /update-*)
  • api_bp blueprint (/api/save-match)
  • Template rendering helpers

templates/ (HTML)
  • base.html - Base template
  • index.html - Main layout
  • fragments/ - HTMX partial updates

static/js/game.js (FRONTEND LOGIC)
  • Game state management
  • Scoring rules
  • Court visualization
  • Match saving


COMMON COMMANDS
───────────────

# Install dependencies
pip install -r requirements.txt

# Verify setup
python verify_setup.py

# Start development server
python app.py

# Production with Gunicorn
gunicorn wsgi:app

# Reset database
python -c "from database import reset_db; from app import create_app; reset_db(create_app())"


BLUEPRINTS & ROUTES
────────────────────

main_bp (General Routes):
  GET  /                    → Main page
  GET  /update-rankings     → Rankings table (HTMX)
  GET  /update-likes        → Like button (HTMX)
  GET  /update-comments     → Comments list (HTMX)
  POST /like                → Increment likes
  POST /comment             → Add wish/comment

api_bp (API Routes):
  POST /api/save-match      → Save match result


DATABASE MODELS
────────────────

Player
  ├── id (primary key)
  ├── name (unique)
  ├── singles_played, singles_won, singles_lost
  ├── doubles_played, doubles_won, doubles_lost
  └── Properties: total_matches, total_wins, win_rate

MatchHistory
  ├── id
  ├── winner_names
  ├── loser_names
  ├── match_type ('Singles' or 'Doubles')
  └── timestamp

LikeCounter
  ├── id
  ├── count
  └── updated_at

Comment
  ├── id
  ├── author
  ├── text
  └── created_at


FEATURES BY TAB
────────────────

STANDINGS
├── Rankings tables (singles & doubles)
└── Click entries to toggle between formats

WISHES
├── Like counter (persists likes)
├── Leave a wish form
└── Comments list (polls every 5s)

LIVE MATCH
├── Match setup (player selection)
├── Court visualization
├── Score tracking (click to add points)
├── Undo button
├── Manual position swap
├── Save when game ends

MANUAL ENTRY
└── Quick result entry (winners/losers)


ENVIRONMENT VARIABLES
─────────────────────

DATABASE_URL       → PostgreSQL connection (optional)
FLASK_ENV          → 'development' or 'production'
SECRET_KEY         → Flask secret (required in production)


TEMPLATE VARIABLES
──────────────────

base.html context:
  • None (static template)

index.html context:
  • player_names: List of all players
  • gif_url: URL to celebration GIF
  • rankings_html: Pre-rendered rankings
  • like_html: Pre-rendered like button
  • comments_html: Pre-rendered comments list

fragments use local variables passed from routes


HTMX TRIGGERS
──────────────

#standings    → hx-get="/update-rankings" every 10s
#likes-btn    → hx-post="/like" on click
#comments     → hx-get="/update-comments" every 5s
.comment-form → hx-post="/comment" on submit


TECHNOLOGIES
──────────────

Backend:    Flask 2.3, SQLAlchemy 2.0
Frontend:   Bootstrap 5, HTMX, Vanilla JS
Database:   PostgreSQL (prod) / SQLite (dev)
Deployment: Gunicorn, Render


TIPS & TRICKS
──────────────

• Models are automatically created on first run
• Initial players seeded only when DB is empty
• Database migrations are automatic
• HTMX updates are real-time
• Game state is client-side for efficiency
• Court visualizes server/receiver positions
• Badminton rules enforced (21pt, 2pt lead, +9 cap)


NEXT IMPROVEMENTS
──────────────────

□ Add player profile pages
□ Match history filtering
□ Leaderboards
□ Tournament brackets
□ Mobile app/PWA
□ Analytics dashboard
□ Admin interface


DOCUMENTATION LINKS
─────────────────────

README.md            → Project overview & setup
DEVELOPMENT.md       → Developer guide & examples
REFACTORING_SUMMARY  → Full refactoring details
This file            → Quick reference


Need help? See DEVELOPMENT.md for detailed guides!
