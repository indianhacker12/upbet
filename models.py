from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    pass_hash = db.Column(db.String(200), nullable=False)
    wallet_balance = db.Column(db.Float, nullable=False, default=0.0)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime, nullable=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    referral_bonus = db.Column(db.Float, nullable=False, default=0.0)
    has_recharged = db.Column(db.Boolean, nullable=False, default=False)
    
    # Relationships
    referred_users = db.relationship('User', backref=db.backref('referrer', remote_side=[id]))
    game_results = db.relationship('GameResult', backref='user')
    odd_even_results = db.relationship('OddEvenGameResult', backref='user')
    color_game_results = db.relationship('ColorGameResult', backref='user')
    game_histories = db.relationship('GameHistory', backref='user')
    mine_betting_history = db.relationship('MineBettingHistory', backref='user')
    aviator_history = db.relationship('AviatorHistory', backref='user')
    aviter_history = db.relationship('AviterHistory', backref='user')
    plinko_history = db.relationship('PlinkoHistory', backref='user')
    plinko_games = db.relationship('PlinkoGame', backref='user')
    mines_games = db.relationship('MinesGame', backref='user')
    slot_games = db.relationship('SlotGame', backref='user')

class GameResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_name = db.Column(db.String(100), default='Dice Roll')
    result = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class OddEvenGameResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    user_choice = db.Column(db.String(10), nullable=False)
    result = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class ColorGameResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    user_choice = db.Column(db.String(10), nullable=False)
    winning_color = db.Column(db.String(10), nullable=False)
    result = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class GameHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_type = db.Column(db.String(50), nullable=False)
    result = db.Column(db.String(50), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    winnings = db.Column(db.Float, nullable=False)
    date_played = db.Column(db.DateTime, nullable=False)

class MineBettingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    grid_size = db.Column(db.Integer, nullable=False)
    mines_count = db.Column(db.Integer, nullable=False)
    cells_revealed = db.Column(db.Integer, nullable=False)
    mine_positions = db.Column(db.JSON, nullable=False)
    revealed_positions = db.Column(db.JSON, nullable=False)
    multiplier_achieved = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(10), nullable=False)
    winnings = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AviatorHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    multiplier = db.Column(db.Float, nullable=True)
    auto_cashout = db.Column(db.Float, nullable=True)
    winnings = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AviterHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    multiplier = db.Column(db.Float, nullable=True)
    auto_cashout = db.Column(db.Float, nullable=True)
    winnings = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class PlinkoHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(10), nullable=False)
    rows = db.Column(db.Integer, nullable=False)
    path = db.Column(db.String(100), nullable=False)
    multiplier = db.Column(db.Float, nullable=False)
    winnings = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class PlinkoGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(10), nullable=False)
    rows = db.Column(db.Integer, nullable=False)
    path = db.Column(db.String(100), nullable=False)
    landing_position = db.Column(db.Integer, nullable=False)
    multiplier = db.Column(db.Float, nullable=False)
    winnings = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class MinesGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    grid_size = db.Column(db.Integer, nullable=False)
    mines_count = db.Column(db.Integer, nullable=False)
    mine_positions = db.Column(db.JSON, nullable=False)
    revealed_positions = db.Column(db.JSON, nullable=False)
    multiplier = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(20), nullable=True)
    winnings = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class SlotGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    symbols = db.Column(db.String(50), nullable=False)
    multiplier = db.Column(db.Float, nullable=False)
    winnings = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AdvancedColorPredictionGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_type = db.Column(db.String(20))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    result = db.Column(db.String(20))
    status = db.Column(db.String(20), default='waiting')

class AdvancedColorPredictionBet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('advanced_color_prediction_game.id'))
    bet_type = db.Column(db.String(20))
    bet_value = db.Column(db.String(20))
    bet_amount = db.Column(db.Float)
    multiplier = db.Column(db.Float)
    result = db.Column(db.String(20))
    winnings = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Cricket models
class CricketMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.String(50), unique=True, nullable=False)
    team1 = db.Column(db.String(100), nullable=False)
    team2 = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    format = db.Column(db.String(50))  # T20, ODI, Test, etc.
    status = db.Column(db.String(50), default='upcoming')  # upcoming, live, completed
    winner = db.Column(db.String(100), nullable=True)
    team1_odds = db.Column(db.Float, default=2.0)
    team2_odds = db.Column(db.Float, default=2.0)
    draw_odds = db.Column(db.Float, default=3.0)
    venue = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bets = db.relationship('CricketMatchBet', backref='match', lazy=True)
    events = db.relationship('CricketEvent', backref='match', lazy=True)

class CricketMatchBet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('cricket_match.id'), nullable=False)
    bet_type = db.Column(db.String(50))  # team1, team2, draw
    bet_amount = db.Column(db.Float, nullable=False)
    odds = db.Column(db.Float, nullable=False)
    potential_winnings = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(20), default='pending')  # pending, won, lost
    settlement_amount = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='cricket_match_bets')

class CricketEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('cricket_match.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)  # e.g., "Most Sixes", "Top Batsman"
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='open')  # open, closed, settled
    result = db.Column(db.String(100), nullable=True)  # The winning option
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    options = db.relationship('CricketEventOption', backref='event', lazy=True)
    bets = db.relationship('CricketEventBet', backref='event', lazy=True)

class CricketEventOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('cricket_event.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Team1", "Player1"
    odds = db.Column(db.Float, nullable=False)
    is_winner = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bets = db.relationship('CricketEventBet', backref='option', lazy=True)

class CricketEventBet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('cricket_event.id'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('cricket_event_option.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    odds = db.Column(db.Float, nullable=False)
    potential_winnings = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(20), default='pending')  # pending, won, lost
    settlement_amount = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='cricket_event_bets') 