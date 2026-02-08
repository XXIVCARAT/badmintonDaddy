"""
Database models for Badminton Daddy application.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


class Player(db.Model):
    """Player model with singles and doubles statistics."""
    
    __tablename__ = 'player'
    
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
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<Player {self.name}>'
    
    @property
    def total_matches(self) -> int:
        """Total matches played across all formats."""
        return self.singles_played + self.doubles_played
    
    @property
    def total_wins(self) -> int:
        """Total wins across all formats."""
        return self.singles_won + self.doubles_won
    
    @property
    def win_rate(self) -> float:
        """Win rate percentage."""
        if self.total_matches == 0:
            return 0.0
        return round((self.total_wins / self.total_matches) * 100, 2)


class MatchHistory(db.Model):
    """Match history record."""
    
    __tablename__ = 'match_history'
    
    id = db.Column(db.Integer, primary_key=True)
    winner_names = db.Column(db.String(200), nullable=False)
    loser_names = db.Column(db.String(200), nullable=False)
    score = db.Column(db.String(20))
    match_type = db.Column(db.String(10), nullable=False)  # 'Singles' or 'Doubles'
    timestamp = db.Column(db.DateTime, server_default=db.func.now(), default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<MatchHistory {self.match_type} - {self.timestamp}>'


class LikeCounter(db.Model):
    """Track likes for the wishes card."""
    
    __tablename__ = 'like_counter'
    
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<LikeCounter {self.count}>'


class Comment(db.Model):
    """Wishes/comments on the wishes card."""
    
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<Comment by {self.author}>'
