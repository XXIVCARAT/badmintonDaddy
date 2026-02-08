# Development Guide

## Project Architecture

This application follows the Flask application factory pattern and uses blueprints for modular route organization.

### Core Modules

- **app.py**: Application factory and initialization
- **config.py**: Configuration classes for different environments
- **models.py**: SQLAlchemy ORM models with properties and relationships
- **database.py**: Database utilities, migrations, and initialization
- **routes.py**: Blueprint definitions for all application routes

### Directory Organization

```
templates/
├── base.html              # Base template with shared layout & styling
├── index.html             # Main application with tab layout
└── fragments/             # HTMX template fragments for partial updates
    ├── rankings.html      # Rankings table (singles/doubles)
    ├── likes.html         # Like button component
    ├── comments.html      # Comments list
    ├── wishes.html        # Wish card container
    ├── scoreboard.html    # Live match scoreboard
    └── manual_entry.html  # Quick result entry form

static/
├── my_cool_gif.gif
└── js/
    └── game.js            # Game state management and UI control
```

## Adding Features

### 1. Add a Database Model

Edit `models.py`:

```python
class NewModel(db.Model):
    __tablename__ = 'new_model'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    
    def __repr__(self) -> str:
        return f'<NewModel {self.name}>'
```

### 2. Add a Route

Edit `routes.py` and add to appropriate blueprint:

```python
@main_bp.route('/new-endpoint')
def new_endpoint():
    """Endpoint description."""
    return render_template('template.html', data=data)
```

Or for API routes:

```python
@api_bp.route('/api/new-endpoint', methods=['POST'])
def api_new_endpoint():
    """API endpoint description."""
    data = request.json
    # Process data
    return jsonify({'status': 'success'})
```

### 3. Add a Template

Create in `templates/fragments/` for HTMX updates or `templates/` for full pages:

```html
<!-- templates/fragments/new_component.html -->
<div id="new-component">
    <!-- Content -->
</div>
```

### 4. Add JavaScript

Edit `static/js/game.js` for game-related logic or create new files as needed:

```javascript
function newFunction() {
    // Implementation
}
```

## Testing

### Manual Testing

1. Start the development server: `python app.py`
2. Navigate to `http://localhost:5000`
3. Test features through the web interface

### Database Testing

```python
from models import db, Player
from app import create_app

app = create_app()
with app.app_context():
    player = Player.query.first()
    print(player)
```

## Common Tasks

### Reset Database

```python
from database import reset_db
from app import create_app

app = create_app()
reset_db(app)  # Drops all tables and reinitializes
```

### Add Initial Data

Edit `database.py` `INITIAL_PLAYERS` list and re-run `init_db()`.

### Configure Settings

1. Edit `config.py` for application settings
2. Use environment variables for secrets: `os.environ.get('VAR_NAME', 'default')`

## Code Style

- Use type hints for function parameters and returns
- Add docstrings to functions and classes
- Follow PEP 8 guidelines
- Use meaningful variable names

## Debugging

### Enable Debug Mode

```python
app = create_app('development')  # Sets DEBUG=True
```

### Database Queries

```python
from sqlalchemy import event

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    print(statement)
```

### Flask Debug Toolbar

Add to `requirements-dev.txt`:
```
flask-debugtoolbar
```

## Performance Notes

- Queries are optimized with `order_by()` for ranking calculations
- HTMX updates are partial page renders to reduce bandwidth
- Database indexes should be added for frequently queried fields

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup instructions.
