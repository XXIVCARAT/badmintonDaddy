"""
Routes and views for Badminton Daddy application.
"""
from flask import Blueprint, render_template, request, jsonify, url_for
from models import db, Player, MatchHistory, LikeCounter, Comment
from errors import success_response, error_response, ValidationError, NotFoundError, DatabaseError
from validators import Validator, MatchValidator
import logging


logger = logging.getLogger(__name__)


# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')


# ============ HELPER FUNCTIONS ============

def get_rankings_html():
    """Generate rankings tables for singles and doubles."""
    singles_rank = Player.query.order_by(
        Player.singles_won.desc(), 
        Player.singles_played.asc()
    ).all()
    doubles_rank = Player.query.order_by(
        Player.doubles_won.desc(), 
        Player.doubles_played.asc()
    ).all()
    
    return render_template('fragments/rankings.html',
                          singles_ranks=singles_rank,
                          doubles_ranks=doubles_rank)


def get_likes_html():
    """Generate likes button."""
    likes_obj = LikeCounter.query.first()
    likes = likes_obj.count if likes_obj else 0
    return render_template('fragments/likes.html', likes=likes)


def get_comments_html():
    """Generate comments list."""
    comments = Comment.query.order_by(Comment.id.desc()).all()
    return render_template('fragments/comments.html', comments=comments)


# ============ MAIN ROUTES ============

@main_bp.route('/')
def index():
    """Main page with all tabs."""
    players = Player.query.order_by(Player.name).all()
    player_names = [p.name for p in players]
    gif_url = url_for('static', filename='my_cool_gif.gif')
    
    return render_template('index.html',
                          player_names=player_names,
                          gif_url=gif_url,
                          rankings_html=get_rankings_html(),
                          like_html=get_likes_html(),
                          comments_html=get_comments_html())


# ============ HTMX UPDATE ROUTES ============

@main_bp.route('/update-rankings')
def update_rankings():
    """Update rankings table via HTMX."""
    return get_rankings_html()


@main_bp.route('/update-likes')
def update_likes():
    """Update likes count via HTMX."""
    return get_likes_html()


@main_bp.route('/update-comments')
def update_comments():
    """Update comments list via HTMX."""
    return get_comments_html()


# ============ INTERACTIVE ROUTES ============

@main_bp.route('/like', methods=['POST'])
def like():
    """Increment likes counter."""
    likes_obj = LikeCounter.query.first()
    if likes_obj:
        likes_obj.count += 1
        db.session.commit()
    return get_likes_html()


@main_bp.route('/comment', methods=['POST'])
def add_comment():
    """Add a new comment/wish."""
    author = request.form.get('author', '').strip()
    text = request.form.get('comment_text', '').strip()
    
    if author and text:
        comment = Comment(author=author, text=text)
        db.session.add(comment)
        db.session.commit()
    
    return get_comments_html()


# ============ API ROUTES ============

@api_bp.route('/save-match', methods=['POST'])
def save_match():
    """
    Save match result and update player statistics.
    
    Expected JSON:
    {
        "winners": ["name1", "name2"],
        "losers": ["name1", "name2"],
        "type": "singles" or "doubles"
    }
    """
    try:
        data = request.json
        if not data:
            return error_response("Request body must be JSON", 400)
        
        winners = data.get('winners', [])
        losers = data.get('losers', [])
        match_type = data.get('type', 'singles')
        
        # Validate match data
        winners, losers, match_type = MatchValidator.validate_match_data(
            winners, losers, match_type
        )
        
        is_doubles = match_type == 'doubles'
        
        # Update winners
        for name in winners:
            player = Player.query.filter_by(name=name).first()
            if not player:
                player = Player(name=name)
                db.session.add(player)
            
            if is_doubles:
                player.doubles_won += 1
                player.doubles_played += 1
            else:
                player.singles_won += 1
                player.singles_played += 1
        
        # Update losers
        for name in losers:
            player = Player.query.filter_by(name=name).first()
            if not player:
                player = Player(name=name)
                db.session.add(player)
            
            if is_doubles:
                player.doubles_lost += 1
                player.doubles_played += 1
            else:
                player.singles_lost += 1
                player.singles_played += 1
        
        # Record match history
        match_record = MatchHistory(
            winner_names=",".join(winners),
            loser_names=",".join(losers),
            match_type='Doubles' if is_doubles else 'Singles'
        )
        db.session.add(match_record)
        db.session.commit()
        
        logger.info(f"Match saved: {match_type.upper()} - Winners: {winners}, Losers: {losers}")
        
        return success_response(
            {
                'match_id': match_record.id,
                'winners': winners,
                'losers': losers,
                'type': match_type
            },
            message="Match saved successfully",
            code=201
        )
    
    except ValidationError as e:
        logger.warning(f"Validation error: {e.message}")
        return error_response(e.message, e.status_code, e.data)
    
    except Exception as e:
        logger.error(f"Error saving match: {str(e)}")
        return error_response("Failed to save match", 500)
