from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import razorpay
from datetime import datetime, timedelta
import random
from razorpay_config import RAZORPAY_API_KEY, RAZORPAY_API_SECRET
import time
import math
from random import choice, shuffle
import itertools
import uuid
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from sqlalchemy import func
import requests
import json
import random
import string
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, flash
import bcrypt
import sqlite3

# Secret key
razorpay_client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET))
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://u483781610_yaswantpandey:Somilpandey123%23@srv1495.hstgr.io/u483781610_upbet'
  # MySQL database connection
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Custom filters for templates
@app.template_filter('format_number')
def format_number(value):
    """Format a number with commas as thousand separators"""
    return "{:,.2f}".format(float(value)) if value is not None else "0.00"

# Helper function to generate game ID


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    pass_hash = db.Column(db.String(200), nullable=False)  # Store hashed password
    wallet_balance = db.Column(db.Float, nullable=False, default=0.0)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime, nullable=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    referral_bonus = db.Column(db.Float, nullable=False, default=0.0)
    has_recharged = db.Column(db.Boolean, nullable=False, default=False)
    
    # Relationship for referrals
    referred_users = db.relationship('User', backref=db.backref('referrer', remote_side=[id]))
    
    def get_id(self):
        return str(self.id)
    
    def set_password(self, password):
        self.pass_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        return check_password_hash(self.pass_hash, password)
    
    @property
    def wallet(self):
        return self.wallet_balance
    
    @wallet.setter
    def wallet(self, value):
        self.wallet_balance = value

# GameResult model for generic game results
class GameResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_name = db.Column(db.String(100), default='Dice Roll')
    result = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref='game_results')

class OddEvenGameResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    user_choice = db.Column(db.String(10), nullable=False)
    result = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref='odd_even_results')

class ColorGameResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    user_choice = db.Column(db.String(10), nullable=False)
    winning_color = db.Column(db.String(10), nullable=False)
    result = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref='color_game_results')

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

class GameHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_type = db.Column(db.String(50), nullable=False)
    result = db.Column(db.String(50), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    winnings = db.Column(db.Float, nullable=False)
    date_played = db.Column(db.DateTime, nullable=False)
    user = db.relationship('User', backref=db.backref('game_histories', lazy=True))

class RockPaperScissorsHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Integer, nullable=False)
    user_choice = db.Column(db.String(10), nullable=False)
    computer_choice = db.Column(db.String(10), nullable=False)
    result = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class OddEvenHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Integer, nullable=False)
    user_choice = db.Column(db.String(10), nullable=False)
    generated_number = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ColorPredictionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    user_choice = db.Column(db.String(10), nullable=False)
    winning_color = db.Column(db.String(10), nullable=False)
    result = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class KenoHistory(db.Model):
    __tablename__ = 'keno_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    bet_amount = db.Column(db.Numeric(10, 2), nullable=False)  # Add this line
    user_numbers = db.Column(db.JSON, nullable=False)
    generated_numbers = db.Column(db.JSON, nullable=False)
    matches = db.Column(db.Integer, nullable=False)
    winnings = db.Column(db.Numeric(10, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Add any other necessary fields


class PokerHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Integer, nullable=False)
    user_hand = db.Column(db.String(50), nullable=False)
    dealer_hand = db.Column(db.String(50), nullable=False)
    winner = db.Column(db.String(50), nullable=False)
    winnings = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class BetHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_type = db.Column(db.String(50), nullable=False)
    bet_value = db.Column(db.String(50), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    multiplier = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(20), nullable=True) 

class MineBettingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    grid_size = db.Column(db.Integer, nullable=False)  # e.g., 5x5
    mines_count = db.Column(db.Integer, nullable=False)  # Number of mines placed
    cells_revealed = db.Column(db.Integer, nullable=False)  # Number of cells revealed
    mine_positions = db.Column(db.JSON, nullable=False)  # Positions of mines
    revealed_positions = db.Column(db.JSON, nullable=False)  # Positions revealed by player
    multiplier_achieved = db.Column(db.Float, nullable=False)  # Final multiplier achieved
    result = db.Column(db.String(10), nullable=False)  # 'win' or 'lose'
    winnings = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='mine_betting_history')

class AviatorHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    multiplier = db.Column(db.Float, nullable=True)
    auto_cashout = db.Column(db.Float, nullable=True)
    winnings = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(10), nullable=False)  # 'win' or 'loss'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='aviator_history')

class DiceBettingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Integer, nullable=False)
    user_choice = db.Column(db.Integer, nullable=False)
    dice_roll = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class PlinkoHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(10), nullable=False)  # 'low', 'medium', 'high'
    rows = db.Column(db.Integer, nullable=False)
    path = db.Column(db.String(100), nullable=False)  # Store the path as a string of L/R directions
    multiplier = db.Column(db.Float, nullable=False)
    winnings = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='plinko_history')

class MinesGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    grid_size = db.Column(db.Integer, nullable=False)
    mines_count = db.Column(db.Integer, nullable=False)
    mine_positions = db.Column(db.JSON, nullable=False)
    revealed_positions = db.Column(db.JSON, nullable=False)
    multiplier = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(20), nullable=True)  # Changed from 10 to 20 to accommodate 'in_progress'
    winnings = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='mines_games')

# Plinko Model
class PlinkoGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(10), nullable=False)  # 'low', 'medium', 'high'
    rows = db.Column(db.Integer, nullable=False)
    path = db.Column(db.String(100), nullable=False)  # Store the path as a string of L/R directions
    landing_position = db.Column(db.Integer, nullable=False)
    multiplier = db.Column(db.Float, nullable=False)
    winnings = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='plinko_games')

# MegaSlot Game Model
class MegaSlotGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    symbols = db.Column(db.String(100), nullable=False)  # Store symbols as a string, more space for 5 reels
    multiplier = db.Column(db.Float, nullable=False)
    winnings = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='mega_slot_games')

# Lucky Wheel Slot Game Model
class LuckyWheelSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    wheel_position = db.Column(db.Integer, nullable=False)  # Position where wheel landed (0-11)
    symbol = db.Column(db.String(20), nullable=False)  # Symbol at that position
    multiplier = db.Column(db.Float, nullable=False)
    winnings = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='lucky_wheel_games')

# Enhanced Dice Betting Game Model
class EnhancedDiceGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    bet_type = db.Column(db.String(20), nullable=False)  # 'exact', 'range', 'odd_even', 'high_low'
    bet_value = db.Column(db.String(20), nullable=False)  # The actual bet value (number, range, etc.)
    dice_result = db.Column(db.Integer, nullable=False)
    multiplier = db.Column(db.Float, nullable=False)
    winnings = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(10), nullable=False)  # 'win' or 'lose'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='enhanced_dice_games')

# Coin Flip Betting Game Model
class CoinFlipGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    user_choice = db.Column(db.String(10), nullable=False)  # 'heads' or 'tails'
    result = db.Column(db.String(10), nullable=False)  # 'heads' or 'tails'
    outcome = db.Column(db.String(10), nullable=False)  # 'win' or 'lose'
    multiplier = db.Column(db.Float, nullable=False, default=1.9)  # Default payout multiplier
    winnings = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='coin_flip_games')

# Odd Even Betting Game Model
class OddEvenBettingGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    user_choice = db.Column(db.String(10), nullable=False)  # 'odd' or 'even'
    number = db.Column(db.Integer, nullable=False)  # Generated number
    result = db.Column(db.String(10), nullable=False)  # 'win' or 'lose'
    multiplier = db.Column(db.Float, nullable=False, default=1.9)
    winnings = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='odd_even_betting_games')

# SuperSlot Game Model
class SuperSlotGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    symbols = db.Column(db.String(150), nullable=False)  # Store symbols as a string
    rows = db.Column(db.Integer, nullable=False, default=3)  # Number of rows
    multiplier = db.Column(db.Float, nullable=False)
    special_feature = db.Column(db.String(30), nullable=True)  # Free spins, bonus round, etc.
    winnings = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='super_slot_games')
    bet_level = db.Column(db.Integer, nullable=False, default=1)
    free_spins_used = db.Column(db.Integer, nullable=True)
    progressive_multiplier = db.Column(db.Float, nullable=True)  # New field for tracking progressive multiplier

class SuperSlotAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_type = db.Column(db.String(50), nullable=False)  # 'big_win', 'jackpot', 'free_spins_complete', etc.
    achievement_value = db.Column(db.Float, nullable=False)  # Amount won, multiplier achieved, etc.
    game_id = db.Column(db.Integer, db.ForeignKey('super_slot_game.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_claimed = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref='super_slot_achievements')
    game = db.relationship('SuperSlotGame', backref='achievements')

class SuperSlotJackpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_amount = db.Column(db.Float, nullable=False, default=20000.0)
    last_winner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    last_win_amount = db.Column(db.Float, nullable=True)
    last_win_date = db.Column(db.DateTime, nullable=True)
    total_contributions = db.Column(db.Float, nullable=False, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    last_winner = db.relationship('User', backref='jackpot_wins')

class TreasureHuntGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    grid_size = db.Column(db.Integer, nullable=False, default=5)  # 5x5 grid by default
    treasure_positions = db.Column(db.JSON, nullable=False)  # Positions of treasures
    trap_positions = db.Column(db.JSON, nullable=False)  # Positions of traps
    revealed_positions = db.Column(db.JSON, nullable=False)  # Positions revealed by player
    multiplier = db.Column(db.Float, nullable=False, default=1.0)
    result = db.Column(db.String(20), nullable=False, default='progress')  # 'win', 'lose', or 'progress'
    winnings = db.Column(db.Float, nullable=True)
    game_state = db.Column(db.String(20), nullable=False, default='active')  # 'active', 'completed', 'terminated'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='treasure_hunt_games')

class TreasureHuntAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_type = db.Column(db.String(50), nullable=False)  # 'treasure_master', 'trap_evader', 'big_win', etc.
    achievement_value = db.Column(db.Float, nullable=False)  # Number of treasures found, multiplier achieved, etc.
    game_id = db.Column(db.Integer, db.ForeignKey('treasure_hunt_game.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_claimed = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref='treasure_hunt_achievements')
    game = db.relationship('TreasureHuntGame', backref='achievements')

class AndarBaharGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    bet_side = db.Column(db.String(10), nullable=False)  # 'andar' or 'bahar'
    joker_card = db.Column(db.String(10), nullable=False)  # The middle card (e.g., 'KH' = King of Hearts)
    winning_card = db.Column(db.String(10), nullable=False)  # The matching card that came up
    winning_side = db.Column(db.String(10), nullable=False)  # 'andar' or 'bahar'
    cards_drawn = db.Column(db.Integer, nullable=False)  # Number of cards drawn before match found
    result = db.Column(db.String(10), nullable=False)  # 'win' or 'lose'
    multiplier = db.Column(db.Float, nullable=False)
    winnings = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='andar_bahar_games')
    
class AndarBaharAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_type = db.Column(db.String(50), nullable=False)  # 'win_streak', 'big_win', 'consistent_player', etc.
    achievement_value = db.Column(db.Integer, nullable=False)  # Count or value of achievement
    is_claimed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='andar_bahar_achievements')
    
    @staticmethod
    def check_and_create_achievements(user_id, game):
        """
        Checks if the user has earned any achievements and creates them
        """
        # Check for big win achievement (win more than 5x bet)
        if game.result == 'win' and game.winnings >= (game.bet_amount * 5):
            # Calculate how many times the bet amount was won
            win_multiple = int(game.winnings / game.bet_amount)
            
            achievement = AndarBaharAchievement(
                user_id=user_id,
                achievement_type='big_win',
                achievement_value=win_multiple
            )
            db.session.add(achievement)
        
        # Check for streak achievement
        recent_games = AndarBaharGame.query.filter_by(
            user_id=user_id
        ).order_by(AndarBaharGame.timestamp.desc()).limit(5).all()
        
        if len(recent_games) >= 3:
            # Check for 3+ consecutive wins
            if all(g.result == 'win' for g in recent_games[:3]):
                # Count streak length
                streak = 0
                for g in recent_games:
                    if g.result == 'win':
                        streak += 1
                    else:
                        break
                
                # Create achievement
                achievement = AndarBaharAchievement(
                    user_id=user_id,
                    achievement_type='win_streak',
                    achievement_value=streak
                )
                db.session.add(achievement)
        
        # Check for card drawn achievement (winning with 15+ cards drawn)
        if game.result == 'win' and game.cards_drawn >= 15:
            achievement = AndarBaharAchievement(
                user_id=user_id,
                achievement_type='long_game_win',
                achievement_value=game.cards_drawn
            )
            db.session.add(achievement)
        
        # Check for consistent player (played 10+ games)
        games_count = AndarBaharGame.query.filter_by(user_id=user_id).count()
        if games_count in [10, 25, 50, 100, 500, 1000]:
            achievement = AndarBaharAchievement(
                user_id=user_id,
                achievement_type='consistent_player',
                achievement_value=games_count
            )
            db.session.add(achievement)

# TeenPatti Game Model
class TeenPattiGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    game_type = db.Column(db.String(20), nullable=False)  # 'classic', 'AK47', 'muflis'
    player_cards = db.Column(db.String(100), nullable=False)  # Store cards as JSON string
    dealer_cards = db.Column(db.String(100), nullable=False)  # Store cards as JSON string
    player_rank = db.Column(db.String(20), nullable=False)  # 'high_card', 'pair', 'flush', 'straight', etc.
    dealer_rank = db.Column(db.String(20), nullable=False)
    result = db.Column(db.String(10), nullable=False)  # 'win', 'lose', 'tie'
    multiplier = db.Column(db.Float, nullable=False, default=2.0)
    winnings = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='teenpatti_games')

class ColorPredictionGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    selected_color = db.Column(db.String(20), nullable=False)
    result_color = db.Column(db.String(20), nullable=False)
    multiplier = db.Column(db.Float, default=2.0)
    winnings = db.Column(db.Float, default=0)
    result = db.Column(db.String(10), nullable=False)  # 'win' or 'loss'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class CricketT20Bet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    match_name = db.Column(db.String(100), nullable=False)
    team_a = db.Column(db.String(50), nullable=False)
    team_b = db.Column(db.String(50), nullable=False)
    selected_team = db.Column(db.String(50), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    odds = db.Column(db.Float, nullable=False, default=1.8)
    result = db.Column(db.String(20), nullable=True)  # 'win', 'lose', 'pending'
    winnings = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='cricket_t20_bets')

class RouletteGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    bet_type = db.Column(db.String(20), nullable=False)  # 'number', 'color', 'even_odd', 'dozen', 'column', etc.
    bet_value = db.Column(db.String(20), nullable=False)  # The actual bet value (number, color, etc.)
    result_number = db.Column(db.Integer, nullable=False)  # The winning number
    result_color = db.Column(db.String(10), nullable=False)  # 'red', 'black', or 'green' for 0
    is_win = db.Column(db.Boolean, nullable=False)
    multiplier = db.Column(db.Float, nullable=False)
    winnings = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='roulette_games')

class SuperSlotMultiplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    current_multiplier = db.Column(db.Float, nullable=False, default=1.0)
    consecutive_losses = db.Column(db.Integer, nullable=False, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='super_slot_multiplier')

with app.app_context():
    db.create_all()


def roll_dice():
    return random.randint(1, 6)

@app.route('/dice', methods=['GET', 'POST'])
def dice_game():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        bet_amount = int(request.form['bet_amount'])
        user_choice = int(request.form['user_choice'])

        if bet_amount > user.wallet:
            return "Insufficient Balance!"

        dice_roll = roll_dice()
        result = 'win' if user_choice == dice_roll else 'lose'

        # Update wallet balance
        if result == 'win':
            user.wallet += bet_amount * 5  # Winning payout is 5x the bet
        else:
            user.wallet -= bet_amount

        # Save game history
        game = DiceBettingHistory(
            user_id=user.id,
            bet_amount=bet_amount,
            user_choice=user_choice,
            dice_roll=dice_roll,
            result=result
        )
        db.session.add(game)
        db.session.commit()

        return render_template('dice_result.html', user_choice=user_choice, dice_roll=dice_roll, result=result, balance=user.wallet)

    return render_template('dice_play.html', balance=user.wallet)



@app.route('/dice/history')
def dice_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    games = DiceBettingHistory.query.filter_by(user_id=session['user_id']).all()
    return render_template('dice_history.html', games=games)



@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Validate the input
    if not name or not email or not message:
        return "All fields are required!", 400

    # Save to the database
    try:
        new_message = ContactMessage(name=name, email=email, message=message)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('contact_success'))
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/contact_success')
def contact_success():
    return "Your message has been sent successfully!"

@app.route('/messages')
def view_messages():
    messages = ContactMessage.query.all()
    return {
        "messages": [
            {
                "name": msg.name,
                "email": msg.email,
                "message": msg.message,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            } for msg in messages
        ]
    }

# Wallet route
@app.route('/wallet', methods=['GET', 'POST'])
@login_required
def wallet():
    if request.method == 'POST':
        action = request.form.get('action')
        amount = float(request.form.get('amount', 0))
        
        if action == 'deposit':
            return redirect(url_for('create_order', amount=amount))
            
        elif action == 'withdraw':
            # Validate withdrawal amount
            if amount <= 0:
                flash('Please enter a valid amount!', 'danger')
                return render_template('wallet.html', user=current_user)
                
            if amount > current_user.wallet_balance:
                flash('Insufficient balance for this withdrawal!', 'danger')
                return render_template('wallet.html', user=current_user)
            
            # Get payment method and account details
            payment_method = request.form.get('payment_method', 'bank_transfer')
            account_details = request.form.get('account_details', '')
            
            # Deduct from user balance
            current_user.wallet_balance -= amount
            db.session.commit()
            
            # Save withdrawal request in transactions table
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Store transaction details as JSON
                transaction_details = json.dumps({
                    'account_details': account_details,
                    'user_note': request.form.get('note', '')
                })
                
                # Insert transaction record
                cursor.execute("""
                    INSERT INTO transactions 
                    (user_id, amount, type, status, payment_method, transaction_details) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (current_user.id, amount, 'withdrawal', 'pending', payment_method, transaction_details))
                
                conn.commit()
                conn.close()
                
                flash('Withdrawal request submitted successfully! It will be processed within 24 hours.', 'success')
            except Exception as e:
                # If transactions table doesn't exist, just show basic success
                flash('Withdrawal successful!', 'success')
                print(f"Error recording transaction: {str(e)}")
        else:
            flash('Invalid action!', 'danger')
            
    return render_template('wallet.html', user=current_user)

# Create order for Razorpay payment
@app.route('/create_order/<float:amount>', methods=['GET'])
@login_required
def create_order(amount):
    amount_in_paise = int(amount * 100)  # Convert amount to paise
    order_data = {
        'amount': amount_in_paise,
        'currency': 'INR',
        'payment_capture': '1'
    }
    order = razorpay_client.order.create(data=order_data)
    return render_template('pay.html', order_id=order['id'], amount=amount)

# Payment success route
@app.route('/payment_success', methods=['POST'])
@login_required
def payment_success():
    payment_id = request.form.get('razorpay_payment_id')
    order_id = request.form.get('razorpay_order_id')
    
    if not payment_id:
        flash("Payment ID not found!", 'danger')
        return redirect(url_for('wallet'))
    
    amount = float(request.form.get('amount', 0))
    
    # If this is first recharge, unlock referral bonus
    if not current_user.has_recharged and current_user.referral_bonus > 0:
        current_user.wallet_balance += current_user.referral_bonus
        current_user.has_recharged = True
        flash(f'Congratulations! Your referral bonus of ₹{current_user.referral_bonus} has been unlocked!', 'success')
    
    # Add amount to user balance
    current_user.wallet_balance += amount
    db.session.commit()
    
    # Record deposit transaction
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Store transaction details
        transaction_details = json.dumps({
            'payment_id': payment_id,
            'order_id': order_id,
            'payment_method': 'razorpay'
        })
        
        # Insert transaction record
        cursor.execute("""
            INSERT INTO transactions 
            (user_id, amount, type, status, payment_method, transaction_details) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (current_user.id, amount, 'deposit', 'completed', 'razorpay', transaction_details))
        
        conn.commit()
        conn.close()
    except Exception as e:
        # If transactions table doesn't exist, just log the error
        print(f"Error recording deposit transaction: {str(e)}")
    
    flash("Payment Successful!", 'success')
    return redirect(url_for('wallet'))

# Payment failure route
@app.route('/payment_failed', methods=['POST'])
def payment_failed():
    flash("Payment Failed! Please try again.", 'danger')
    return redirect(url_for('wallet'))

# Account route
@app.route('/account')
@login_required
def account():
    # Get user's recent activities
    recent_activities = GameHistory.query.filter_by(user_id=current_user.id)\
        .order_by(GameHistory.date_played.desc())\
        .limit(5)\
        .all()
    
    # Get total games played
    total_games = GameHistory.query.filter_by(user_id=current_user.id).count()
    
    # Get total winnings
    total_winnings = db.session.query(func.sum(GameHistory.winnings))\
        .filter(GameHistory.user_id == current_user.id)\
        .scalar() or 0
    
    # Get Aviator game history
    aviator_history = AviatorHistory.query.filter_by(user_id=current_user.id)\
        .order_by(AviatorHistory.timestamp.desc())\
        .limit(20)\
        .all()
    
    # Get Mines game history
    mines_history = MineBettingHistory.query.filter_by(user_id=current_user.id)\
        .order_by(MineBettingHistory.timestamp.desc())\
        .limit(20)\
        .all()
    
    # Get Slots game history
    try:
        slots_history = SlotGame.query.filter_by(user_id=current_user.id)\
            .order_by(SlotGame.timestamp.desc())\
            .limit(20)\
            .all()
    except Exception as e:
        # Handle error when slot_game table doesn't exist
        print(f"Error loading slot history: {str(e)}")
        slots_history = []
    
    # Get Dice game history
    dice_history = DiceBettingHistory.query.filter_by(user_id=current_user.id)\
        .order_by(DiceBettingHistory.timestamp.desc())\
        .limit(20)\
        .all()
    
    # Get Plinko game history
    plinko_history = PlinkoHistory.query.filter_by(user_id=current_user.id)\
        .order_by(PlinkoHistory.timestamp.desc())\
        .limit(20)\
        .all()
    
    # Other games history (combine any other game types)
    other_history = []
    
    # Add Lucky Wheel history if available
    try:
        lucky_wheel_history = LuckyWheelSlot.query.filter_by(user_id=current_user.id)\
            .order_by(LuckyWheelSlot.timestamp.desc())\
            .limit(10)\
            .all()
        
        for game in lucky_wheel_history:
            result = 'win' if game.winnings > 0 else 'loss'
            other_history.append({
                'game_type': 'Lucky Wheel',
                'bet_amount': game.bet_amount,
                'result': result,
                'winnings': game.winnings,
                'timestamp': game.timestamp
            })
    except Exception as e:
        print(f"Error loading lucky wheel history: {str(e)}")
    
    # Add Mega Slot history if available
    try:
        mega_slot_history = MegaSlotGame.query.filter_by(user_id=current_user.id)\
            .order_by(MegaSlotGame.timestamp.desc())\
            .limit(10)\
            .all()
        
        for game in mega_slot_history:
            result = 'win' if game.winnings > 0 else 'loss'
            other_history.append({
                'game_type': 'Mega Slot',
                'bet_amount': game.bet_amount,
                'result': result,
                'winnings': game.winnings,
                'timestamp': game.timestamp
            })
    except Exception as e:
        print(f"Error loading mega slot history: {str(e)}")
    
    # Sort combined other_history by timestamp
    if other_history:
        other_history.sort(key=lambda x: x['timestamp'], reverse=True)
        other_history = other_history[:20]  # Limit to 20 most recent
    
    return render_template('account.html',
                         current_user=current_user,
                         total_games=total_games,
                         total_winnings=total_winnings,
                         recent_activities=recent_activities,
                         account_created=current_user.date_created.strftime('%d %b %Y'),
                         last_login=current_user.last_login.strftime('%d %b %Y %H:%M') if current_user.last_login else 'Never',
                         aviator_history=aviator_history,
                         mines_history=mines_history,
                         slots_history=slots_history,
                         dice_history=dice_history,
                         plinko_history=plinko_history,
                         other_history=other_history)

# Promotion route


# Route for displaying game history
@app.route('/game-history')
def game_history():
    # Check if the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Fetch each game type's history from the database
    # color_game_history = ColorGameResult.query.filter_by(user_id=user_id).order_by(ColorGameResult.timestamp.desc()).all()
    odd_even_game_history = OddEvenGameResult.query.filter_by(user_id=user_id).order_by(OddEvenGameResult.timestamp.desc()).all()
    generic_game_history = GameResult.query.filter_by(user_id=user_id).order_by(GameResult.timestamp.desc()).all()

    # Structure data to pass to the template
    all_games_history = {
        # 'color_game': color_game_history,
        'odd_even_game': odd_even_game_history,
        'generic_game': generic_game_history
    }

    # Render the game history template
    return render_template('game_history.html', all_games_history=all_games_history)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
        
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        captcha = request.form.get('captcha')
        
        # Verify CAPTCHA first
        if not verify_captcha(captcha):
            flash('Invalid CAPTCHA. Please try again.', 'danger')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(phone=phone).first()
        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user)
            session['user_id'] = user.id  # Also set in session for backward compatibility
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main'))
        else:
            flash('Invalid phone number or password.', 'danger')
    
    # Generate new CAPTCHA for GET request
    captcha = generate_captcha()
    return render_template('login.html', captcha=captcha)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        captcha = request.form.get('captcha')
        referral_code = request.form.get('referral_code')
        
        # Verify CAPTCHA first
        if not verify_captcha(captcha):
            flash('Invalid CAPTCHA. Please try again.', 'danger')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(phone=phone).first():
            flash('Phone number already registered.', 'danger')
            return redirect(url_for('signup'))
        
        # Create new user
        user = User(name=name, phone=phone)
        user.set_password(password)
        
        # Process referral if provided
        if referral_code:
            referrer = User.query.filter_by(id=referral_code).first()
            if referrer:
                user.referrer_id = referrer.id
                # Add referral bonus (₹50) to be unlocked after first recharge
                user.referral_bonus = 50.0
                # Also add bonus to referrer
                referrer.referral_bonus += 50.0
                flash(f'Referral bonus will be unlocked after your first recharge!', 'success')
        
        db.session.add(user)
        db.session.commit()
        
        # Log in the user immediately
        login_user(user)
        session['user_id'] = user.id  # For backward compatibility
        
        flash('Account created successfully! Welcome to Xbetin.', 'success')
        return redirect(url_for('main'))
    
    # Generate new CAPTCHA for GET request
    captcha = generate_captcha()
    return render_template('signup.html', captcha=captcha)



import mysql.connector
# from flask import Flask, render_template, request, redirect, url_for, session, flash
import bcrypt
import sqlite3

  # Change this

# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='myadmin'
    )

# Admin Login Route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
        admin = cursor.fetchone()
        conn.close()

        if admin and bcrypt.checkpw(password.encode('utf-8'), admin['password'].encode('utf-8')):
            session['admin_logged_in'] = True
            session['admin_username'] = admin['username']
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid credentials", "danger")

    return render_template('admin_login.html')

# Admin Dashboard Route
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_users FROM user")
    total_users = cursor.fetchone()['total_users']

    cursor.execute("SELECT COUNT(*) AS total_bets FROM bet_history")
    total_bets = cursor.fetchone()['total_bets']

    # Check if transactions table exists
    try:
        cursor.execute("SELECT COUNT(*) AS pending_withdrawals FROM transactions WHERE type='withdrawal' AND status='pending'")
        pending_withdrawals = cursor.fetchone()['pending_withdrawals']
    except mysql.connector.errors.ProgrammingError as e:
        # Table doesn't exist
        if e.errno == 1146:  # "Table doesn't exist" error code
            pending_withdrawals = 0
            flash("Transactions table not found. Please run the database migration script.", "danger")
        else:
            # Re-raise if it's a different error
            raise
    
    # Get game activity statistics for admin dashboard
    game_stats = {}
    try:
        # Get total games played today
        cursor.execute("""
            SELECT COUNT(*) as today_games 
            FROM (
                SELECT id FROM mines_game WHERE DATE(timestamp) = CURDATE() UNION ALL
                SELECT id FROM plinko_game WHERE DATE(timestamp) = CURDATE() UNION ALL
                SELECT id FROM slot_game WHERE DATE(timestamp) = CURDATE() UNION ALL
                SELECT id FROM mega_slot_game WHERE DATE(timestamp) = CURDATE() UNION ALL
                SELECT id FROM lucky_wheel_slot WHERE DATE(timestamp) = CURDATE() UNION ALL
                SELECT id FROM aviator_history WHERE DATE(timestamp) = CURDATE() UNION ALL
                SELECT id FROM coin_flip_game WHERE DATE(timestamp) = CURDATE() UNION ALL
                SELECT id FROM odd_even_betting_game WHERE DATE(timestamp) = CURDATE()
            ) AS all_games
        """)
        game_stats['today_games'] = cursor.fetchone()['today_games'] or 0
        
        # Get most played game
        cursor.execute("""
            SELECT game_name, game_count FROM (
                SELECT 'Mines' as game_name, COUNT(*) as game_count FROM mines_game UNION ALL
                SELECT 'Plinko' as game_name, COUNT(*) as game_count FROM plinko_game UNION ALL
                SELECT 'Slots' as game_name, COUNT(*) as game_count FROM slot_game UNION ALL
                SELECT 'MegaSlots' as game_name, COUNT(*) as game_count FROM mega_slot_game UNION ALL
                SELECT 'LuckyWheel' as game_name, COUNT(*) as game_count FROM lucky_wheel_slot UNION ALL
                SELECT 'Aviator' as game_name, COUNT(*) as game_count FROM aviator_history UNION ALL
                SELECT 'CoinFlip' as game_name, COUNT(*) as game_count FROM coin_flip_game UNION ALL
                SELECT 'OddEven' as game_name, COUNT(*) as game_count FROM odd_even_betting_game
            ) as game_counts
            ORDER BY game_count DESC
            LIMIT 1
        """)
        most_played = cursor.fetchone()
        game_stats['most_played'] = most_played['game_name'] if most_played else 'N/A'
        game_stats['most_played_count'] = most_played['game_count'] if most_played else 0
    except Exception as e:
        print(f"Error getting game stats: {str(e)}")
        game_stats = {'today_games': 0, 'most_played': 'N/A', 'most_played_count': 0}

    conn.close()

    return render_template('admin_dashboard.html', 
                          total_users=total_users, 
                          total_bets=total_bets, 
                          pending_withdrawals=pending_withdrawals,
                          game_stats=game_stats)

# Manage Users
@app.route('/manage_users')
def manage_user():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    
    # Process the users to add status field for template
    for user in users:
        # Add status field (in the real app, this would come from the database)
        user['status'] = "Active"
        # Format wallet balance as currency
        if 'wallet_balance' in user:
            user['wallet_balance'] = "{:.2f}".format(user['wallet_balance'])
        # Add email field if it doesn't exist (template expects it)
        if 'email' not in user and 'phone' in user:
            user['email'] = user['phone']  # Use phone as email for display
    
    conn.close()

    # Make sure we're using the correct template name with proper extension
    return render_template('manage_users.html', users=users)

# Block User
@app.route('/block_user/<int:user_id>')
def block_user(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_blocked = TRUE WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('manage_users'))

# Approve Withdrawal
@app.route('/approve_withdrawal/<int:transaction_id>')
def approve_withdrawal(transaction_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE transactions SET status = 'approved' WHERE id = %s", (transaction_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))

# Logout
@app.route('/admin_logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))







@app.route('/')
def main():
    return render_template('home.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/privacy')
def privacy_policy():
    return render_template('privacy.html')

@app.route('/security')
def security():
    return render_template('security.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route("/manage-users")
def manage_users():
    return render_template("manage_users.html")

@app.route('/color')
def color():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('color.html', User=session)

@app.route('/contact')
def contact_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('contact.html')
    


@app.route('/dice')
def dice():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dice_play.html', User=session)

@app.route('/keno')
@login_required
def keno():
    return render_template('keno_play.html', balance=current_user.wallet_balance)

# Helper function to render keno results
def render_keno_result(user_numbers, drawn_numbers, matches, bet_amount, winnings):
    return render_template(
        'keno_result.html',
        user_numbers=user_numbers,
        generated_numbers=drawn_numbers,
        matches=matches,
        bet_amount=bet_amount,
        winnings=winnings,
        balance=current_user.wallet_balance
    )

@app.route('/keno/play', methods=['POST'])
@login_required
def keno_play():
    try:
        # Handle both JSON and form submissions for flexibility
        if request.is_json:
            data = request.get_json()
            bet_amount = float(data.get('bet_amount', 0))
            selected_numbers = data.get('selected_numbers', [])
        else:
            bet_amount = float(request.form.get('bet_amount', 0))
            selected_numbers = request.form.getlist('user_numbers')
        
        # Validate inputs with specific error messages
        if bet_amount <= 0:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Please enter a valid bet amount greater than 0'})
            flash('Please enter a valid bet amount greater than 0', 'error')
            return redirect(url_for('keno'))
        
        if current_user.wallet_balance < bet_amount:
            error_msg = f'Insufficient balance. You have ₹{current_user.wallet_balance} available.'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg})
            flash(error_msg, 'error')
            return redirect(url_for('keno'))
        
        # Validate selected numbers
        if not selected_numbers:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Please select at least one number to play'})
            flash('Please select at least one number to play', 'error')
            return redirect(url_for('keno'))
            
        if len(selected_numbers) > 10:
            if request.is_json:
                return jsonify({'success': False, 'error': 'You can select maximum 10 numbers'})
            flash('You can select maximum 10 numbers', 'error')
            return redirect(url_for('keno'))
        
        # Convert string numbers to integers if needed
        try:
            selected_numbers = [int(num) for num in selected_numbers]
        except (ValueError, TypeError):
            error_msg = 'Invalid number selection format'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg})
            flash(error_msg, 'error')
            return redirect(url_for('keno'))
        
        # Check if all selected numbers are within range 1-80
        invalid_nums = [num for num in selected_numbers if num < 1 or num > 80]
        if invalid_nums:
            error_msg = f'Invalid number(s): {", ".join(map(str, invalid_nums))}. Numbers must be between 1 and 80.'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg})
            flash(error_msg, 'error')
            return redirect(url_for('keno'))
        
        # Check for duplicate numbers
        if len(selected_numbers) != len(set(selected_numbers)):
            error_msg = 'Please avoid selecting duplicate numbers'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg})
            flash(error_msg, 'error')
            return redirect(url_for('keno'))
        
        # Generate 20 random numbers for the draw
        drawn_numbers = random.sample(range(1, 81), 20)
        
        # Count matches
        matches = len(set(selected_numbers) & set(drawn_numbers))
        
        # Calculate multiplier based on number of matches and selections
        try:
            multiplier = get_keno_multiplier(len(selected_numbers), matches)
        except KeyError:
            error_msg = 'Error calculating multiplier. Please try again.'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg})
            flash(error_msg, 'error')
            return redirect(url_for('keno'))
        
        # Calculate winnings
        winnings = bet_amount * multiplier
        
        # Update user balance
        current_user.wallet_balance -= bet_amount
        if winnings > 0:
            current_user.wallet_balance += winnings
        
        # Save game to history
        try:
            history = KenoHistory(
                user_id=current_user.id,
                bet_amount=bet_amount,
                user_numbers=selected_numbers,
                generated_numbers=drawn_numbers,
                matches=matches,
                winnings=winnings
            )
            
            db.session.add(history)
            db.session.commit()

            if request.is_json:
                return jsonify({
                    'success': True,
                    'drawn_numbers': drawn_numbers,
                    'matches': matches,
                    'multiplier': multiplier,
                    'winnings': winnings,
                    'new_balance': current_user.wallet_balance
                })
            else:
                # For form submission, render the result page
                return render_keno_result(selected_numbers, drawn_numbers, matches, bet_amount, winnings)
                
        except Exception as db_error:
            db.session.rollback()
            print(f"Database error in keno_play: {str(db_error)}")
            
            # Still give the user their result but note the history error
            if request.is_json:
                return jsonify({
                    'success': True,
                    'drawn_numbers': drawn_numbers,
                    'matches': matches,
                    'multiplier': multiplier,
                    'winnings': winnings,
                    'new_balance': current_user.wallet_balance,
                    'history_saved': False,
                    'note': 'Game played successfully but there was an error saving to history'
                })
            else:
                flash('Game played successfully but there was an error saving to history', 'warning')
                return render_keno_result(selected_numbers, drawn_numbers, matches, bet_amount, winnings)
            
    except ValueError as ve:
        db.session.rollback()
        print(f"Value error in keno_play: {str(ve)}")
        error_msg = 'Please enter valid number values'
        if request.is_json:
            return jsonify({'success': False, 'error': error_msg})
        flash(error_msg, 'error')
        return redirect(url_for('keno'))
        
    except Exception as e:
        db.session.rollback()
        error_message = str(e)
        print(f"Error in keno_play: {error_message}")
        
        # Provide more helpful error messages based on exception type
        if "JSON" in error_message:
            error_msg = 'Invalid request format'
        elif "NoneType" in error_message:
            error_msg = 'Missing required information'
        else:
            error_msg = 'An error occurred. Please try again.'
            
        if request.is_json:
            return jsonify({'success': False, 'error': error_msg})
        flash(error_msg, 'error')
        return redirect(url_for('keno'))

@app.route('/keno/history')
@login_required
def keno_history():
    try:
        # Check if the request wants JSON response
        if request.headers.get('Content-Type') == 'application/json' or request.args.get('format') == 'json':
            # Get user's recent games
            games = KenoHistory.query.filter_by(
                user_id=current_user.id
            ).order_by(KenoHistory.timestamp.desc()).limit(20).all()
            
            if not games:
                return jsonify({
                    'success': True,
                    'history': [],
                    'message': 'No game history found'
                })
                
            history = []
            for game in games:
                history.append({
                    'bet_amount': float(game.bet_amount),
                    'user_numbers': game.user_numbers,
                    'drawn_numbers': game.generated_numbers,
                    'matches': game.matches,
                    'winnings': float(game.winnings),
                    'timestamp': game.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                })

            return jsonify({
                'success': True,
                'history': history
            })
        else:
            # Render HTML template for browser view
            games = KenoHistory.query.filter_by(
                user_id=current_user.id
            ).order_by(KenoHistory.timestamp.desc()).all()
            
            return render_template('keno_history.html', games=games)
    except Exception as e:
        print(f"Error in keno_history: {str(e)}")
        if request.headers.get('Content-Type') == 'application/json' or request.args.get('format') == 'json':
            return jsonify({'success': False, 'error': 'Error loading game history. Please try again later.'})
        else:
            flash('Error loading game history. Please try again later.', 'error')
            return redirect(url_for('keno'))

@app.route('/keno/recent')
@login_required
def keno_recent():
    try:
        # Get user's recent games - limit to 5 for the sidebar widget
        games = KenoHistory.query.filter_by(
            user_id=current_user.id
        ).order_by(KenoHistory.timestamp.desc()).limit(5).all()
        
        game_list = []
        for game in games:
            game_list.append({
                'bet_amount': float(game.bet_amount),
                'user_numbers': game.user_numbers,
                'drawn_numbers': game.generated_numbers,
                'matches': game.matches,
                'multiplier': float(game.winnings) / float(game.bet_amount) if float(game.bet_amount) > 0 else 0,
                'winnings': float(game.winnings),
                'timestamp': game.timestamp.strftime('%H:%M:%S')
            })
            
        return jsonify({
            'success': True,
            'games': game_list
        })
    except Exception as e:
        print(f"Error in keno_recent: {str(e)}")
        return jsonify({'success': False, 'error': 'Error loading recent games'})

# Helper function for Keno
def get_keno_multiplier(picks, matches):
    """
    Returns the multiplier for Keno based on number of picks and matches
    """
    # Multiplier table based on number of picks and matches
    multiplier_table = {
        1: {0: 0, 1: 3.8},
        2: {0: 0, 1: 1, 2: 9},
        3: {0: 0, 1: 0, 2: 2.7, 3: 32},
        4: {0: 0, 1: 0, 2: 1, 3: 5, 4: 120},
        5: {0: 0, 1: 0, 2: 0.5, 3: 3, 4: 15, 5: 300},
        6: {0: 0, 1: 0, 2: 0.5, 3: 2, 4: 7, 5: 30, 6: 600},
        7: {0: 0, 1: 0, 2: 0.5, 3: 1, 4: 4, 5: 15, 6: 100, 7: 1200},
        8: {0: 0, 1: 0, 2: 0.5, 3: 1, 4: 3, 5: 10, 6: 50, 7: 300, 8: 3000},
        9: {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 5, 6: 15, 7: 100, 8: 500, 9: 4000},
        10: {0: 0, 1: 0, 2: 0, 3: 0.5, 4: 1, 5: 3, 6: 10, 7: 50, 8: 200, 9: 1000, 10: 10000}
    }
    
    # Return multiplier if valid, otherwise 0
    try:
        return multiplier_table.get(picks, {}).get(matches, 0)
    except:
        print(f"Error getting multiplier for picks={picks}, matches={matches}")
        return 0

@app.route('/get_balance', methods=['GET'])
def get_balance():
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    if user:
        return jsonify({"balance": user.wallet})
    return jsonify({"error": "User not found"}), 404

@app.route('/update_balance', methods=['POST'])
def update_balance():
    data = request.json
    user_id = data.get("user_id")
    new_balance = data.get("new_balance")

    user = User.query.get(user_id)
    if user:
        user.wallet = new_balance
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "User not found"}), 404


# ///////////////////////////////////////////////////

@app.route('/get_wallet_balance', methods=['GET'])
def get_wallet_balance():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404

    print("Returning Wallet Balance:", user.wallet)  # Debugging
    return jsonify({"wallet_balance": user.wallet})



@app.route('/place_bet', methods=['POST'])
def place_bet():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    data = request.json
    bet_amount = float(data['betAmount'])
    bet_type = data['type']
    bet_value = data['value']
    multiplier = float(data['multiplier'])

    if bet_amount > user.wallet:
        return jsonify({"success": False, "error": "Insufficient balance"})

    # Deduct balance
    user.wallet -= bet_amount
    
    # Determine result (random for now, can be replaced with actual game logic)
    result = "win" if random.random() < 0.5 else "lose"
    
    # Update balance if win
    if result == "win":
        winnings = bet_amount * multiplier
        user.wallet += winnings
    
    # Save bet history with result
    bet = BetHistory(
        user_id=user.id, 
        bet_type=bet_type, 
        bet_value=bet_value, 
        bet_amount=bet_amount, 
        multiplier=multiplier,
        result=result
    )
    db.session.add(bet)
    db.session.commit()

    return jsonify({
        "success": True,
        "new_balance": user.wallet,
        "bet_history": {"type": bet_type, "value": bet_value, "amount": bet_amount},
        "result": result
    })



@app.route('/get_bet_history', methods=['GET'])
def get_bet_history():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404

    bet_history = BetHistory.query.filter_by(user_id=user.id).order_by(BetHistory.id.desc()).limit(10).all()

    bet_data = [
        {
            "type": bet.bet_type,
            "value": bet.bet_value,
            "amount": bet.bet_amount,
            "multiplier": bet.multiplier,
            "result": bet.result or "pending"
        }
        for bet in bet_history
    ]

    return jsonify({"bet_history": bet_data})

@app.route('/mine-betting', methods=['GET'])
def mine_betting_game():
    """Render the mine betting game page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('mine_betting.html', balance=user.wallet)

@app.route('/mine-betting/start', methods=['POST'])
def mine_betting_start():
    """Start a new mine betting game"""
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401
    
    try:
        data = request.get_json()
        bet_amount = float(data.get('bet_amount', 0))
        grid_size = int(data.get('grid_size', 5))  # Default 5x5 grid
        mines_count = int(data.get('mines_count', 3))  # Default 3 mines
        
        # Validate inputs
        if not bet_amount or bet_amount <= 0:
            return jsonify({"success": False, "error": "Invalid bet amount"}), 400
        
        if grid_size < 3 or grid_size > 8:
            return jsonify({"success": False, "error": "Grid size must be between 3x3 and 8x8"}), 400
        
        if mines_count < 1 or mines_count >= (grid_size * grid_size) / 2:
            return jsonify({"success": False, "error": f"Mines count must be between 1 and {(grid_size * grid_size) // 2 - 1}"}), 400
        
        # Get user and check balance
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        if bet_amount > user.wallet:
            return jsonify({"success": False, "error": "Insufficient balance"}), 400
        
        # Deduct bet amount from wallet
        user.wallet -= bet_amount
        db.session.commit()
        
        # Generate mine positions
        total_cells = grid_size * grid_size
        all_positions = list(range(total_cells))
        random.shuffle(all_positions)
        mine_positions = all_positions[:mines_count]
        
        # Calculate multiplier table based on grid size and mines count
        # The more mines, the higher the potential multiplier
        base_multiplier = 1 + (mines_count / (grid_size * grid_size)) * 10
        multipliers = []
        
        for i in range(1, total_cells - mines_count + 1):
            # Multiplier increases as more cells are revealed
            # Higher risk (more revealed cells) = higher reward
            multiplier = base_multiplier * (1 + (i / (total_cells - mines_count)) * mines_count)
            multipliers.append(round(multiplier, 2))
        
        # Store game state in session
        session['mine_game'] = {
            'bet_amount': bet_amount,
            'grid_size': grid_size,
            'mines_count': mines_count,
            'mine_positions': mine_positions,
            'revealed_positions': [],
            'current_multiplier': 1.0,
            'multiplier_table': multipliers,
            'game_over': False,
            'result': None
        }
        
        return jsonify({
            "success": True,
            "grid_size": grid_size,
            "mines_count": mines_count,
            "multiplier_table": multipliers,
            "new_balance": user.wallet
        })
    
    except Exception as e:
        db.session.rollback()
        print("Error starting mine game:", str(e))
        return jsonify({"success": False, "error": "Failed to start game"}), 500

@app.route('/mine-betting/reveal', methods=['POST'])
def mine_betting_reveal():
    """Reveal a cell in the mine betting game"""
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401
    
    if 'mine_game' not in session:
        return jsonify({"success": False, "error": "No active game found"}), 400
    
    try:
        data = request.get_json()
        position = int(data.get('position', -1))
        
        game = session['mine_game']
        
        # Check if game is already over
        if game['game_over']:
            return jsonify({"success": False, "error": "Game is already over"}), 400
        
        # Check if position is valid
        if position < 0 or position >= game['grid_size'] * game['grid_size']:
            return jsonify({"success": False, "error": "Invalid position"}), 400
        
        # Check if position is already revealed
        if position in game['revealed_positions']:
            return jsonify({"success": False, "error": "Cell already revealed"}), 400
        
        # Check if position has a mine
        hit_mine = position in game['mine_positions']
        
        # Add position to revealed positions
        game['revealed_positions'].append(position)
        
        # Update game state
        if hit_mine:
            game['game_over'] = True
            game['result'] = 'lose'
            winnings = 0
        else:
            # Update multiplier based on number of revealed cells
            revealed_count = len(game['revealed_positions'])
            
            if revealed_count <= len(game['multiplier_table']):
                game['current_multiplier'] = game['multiplier_table'][revealed_count - 1]
            
            # Check if all safe cells are revealed
            if revealed_count == game['grid_size'] * game['grid_size'] - game['mines_count']:
                game['game_over'] = True
                game['result'] = 'win'
                winnings = game['bet_amount'] * game['current_multiplier']
            else:
                winnings = 0  # Game still in progress
        
        # Update session
        session['mine_game'] = game
        
        # If game is over, save to history and update wallet
        if game['game_over']:
            user = User.query.get(session['user_id'])
            
            # If won, add winnings to wallet
            if game['result'] == 'win':
                user.wallet += winnings
            
            # Save game to history
            history = MineBettingHistory(
                user_id=user.id,
                bet_amount=game['bet_amount'],
                grid_size=game['grid_size'],
                mines_count=game['mines_count'],
                cells_revealed=len(game['revealed_positions']),
                mine_positions=game['mine_positions'],
                revealed_positions=game['revealed_positions'],
                multiplier_achieved=game['current_multiplier'],
                result=game['result'],
                winnings=winnings
            )
            db.session.add(history)
            db.session.commit()
            
            return jsonify({
                "success": True,
                "hit_mine": hit_mine,
                "game_over": True,
                "result": game['result'],
                "multiplier": game['current_multiplier'],
                "winnings": winnings,
                "mine_positions": game['mine_positions'],
                "new_balance": user.wallet
            })
        
        return jsonify({
            "success": True,
            "hit_mine": hit_mine,
            "game_over": False,
            "multiplier": game['current_multiplier'],
            "revealed_position": position
        })
    
    except Exception as e:
        db.session.rollback()
        print("Error revealing cell:", str(e))
        return jsonify({"success": False, "error": "Failed to reveal cell"}), 500

@app.route('/mine-betting/cashout', methods=['POST'])
def mine_betting_cashout():
    """Cash out current winnings and end the game"""
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401
    
    if 'mine_game' not in session:
        return jsonify({"success": False, "error": "No active game found"}), 400
    
    try:
        game = session['mine_game']
        
        # Check if game is already over
        if game['game_over']:
            return jsonify({"success": False, "error": "Game is already over"}), 400
        
        # Calculate winnings
        winnings = game['bet_amount'] * game['current_multiplier']
        
        # Update game state
        game['game_over'] = True
        game['result'] = 'win'
        
        # Update user wallet
        user = User.query.get(session['user_id'])
        user.wallet += winnings
        
        # Save game to history
        history = MineBettingHistory(
            user_id=user.id,
            bet_amount=game['bet_amount'],
            grid_size=game['grid_size'],
            mines_count=game['mines_count'],
            cells_revealed=len(game['revealed_positions']),
            mine_positions=game['mine_positions'],
            revealed_positions=game['revealed_positions'],
            multiplier_achieved=game['current_multiplier'],
            result='win',
            winnings=winnings
        )
        
        db.session.add(history)
        db.session.commit()
        
        # Update session
        session['mine_game'] = game
        
        return jsonify({
            "success": True,
            "game_over": True,
            "result": 'win',
            "multiplier": game['current_multiplier'],
            "winnings": winnings,
            "mine_positions": game['mine_positions'],
            "new_balance": user.wallet
        })
    
    except Exception as e:
        db.session.rollback()
        print("Error cashing out:", str(e))
        return jsonify({"success": False, "error": "Failed to cash out"}), 500

@app.route('/mine-betting/history')
def mine_betting_history():
    """Get user's mine betting history"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    history = MineBettingHistory.query.filter_by(
        user_id=session['user_id']
    ).order_by(MineBettingHistory.timestamp.desc()).limit(20).all()
    
    history_data = []
    for game in history:
        history_data.append({
            "id": game.id,
            "bet_amount": game.bet_amount,
            "grid_size": game.grid_size,
            "mines_count": game.mines_count,
            "cells_revealed": game.cells_revealed,
            "multiplier": game.multiplier_achieved,
            "result": game.result,
            "winnings": game.winnings,
            "timestamp": game.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return render_template('mine_betting_history.html', history=history_data)




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Add this function to migrate the database
def migrate_database():
    try:
        print("Starting database migration...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Alter treasure_hunt_game table to increase result column size
        cursor.execute("ALTER TABLE treasure_hunt_game MODIFY COLUMN result VARCHAR(20) NOT NULL DEFAULT 'in_progress'")
        
        conn.commit()
        conn.close()
        print("Database migration completed successfully")
        
    except Exception as e:
        print(f"Error during database migration: {str(e)}")
        if 'conn' in locals() and conn:
            conn.close()

# Run migration when app starts
with app.app_context():
    migrate_database()
    
def verify_recaptcha(response):
    data = {
        'secret': app.config['RECAPTCHA_SECRET_KEY'],
        'response': response
    }
    result = requests.post(app.config['RECAPTCHA_VERIFY_URL'], data=data)
    return result.json().get('success', False)

def verify_captcha(user_answer):
    """Verify if the user's answer matches the captcha"""
    correct_answer = session.get('captcha_answer')
    if not correct_answer:
        return False
    return user_answer == correct_answer

# Simple captcha generator function
def generate_captcha():
    """Generate a simple math-based captcha"""
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operation = random.choice(['+', '-', '*'])
    
    if operation == '+':
        answer = num1 + num2
    elif operation == '-':
        # Make sure the result is positive
        if num1 < num2:
            num1, num2 = num2, num1
        answer = num1 - num2
    else:  # multiplication
        answer = num1 * num2
    
    question = f"{num1} {operation} {num2} = ?"
    # Store answer in session
    session['captcha_answer'] = str(answer)
    
    return question

@app.route('/refresh-captcha', methods=['GET'])
def refresh_captcha():
    captcha = generate_captcha()
    return jsonify({'captcha': captcha})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('main'))

@app.route('/mines', methods=['GET'])
@login_required
def mines():
    return render_template('mines.html', balance=current_user.wallet_balance)

@app.route('/mines/start', methods=['POST'])
@login_required
def start_mines_game():
    try:
        data = request.get_json()
        bet_amount = float(data.get('bet_amount', 0))
        grid_size = int(data.get('grid_size', 5))
        mines_count = int(data.get('mines_count', 3))
        
        # Enhanced validation with specific error messages
        if bet_amount <= 0:
            return jsonify({'success': False, 'error': 'Please enter a valid bet amount greater than 0'})
        
        if grid_size not in [3, 5, 7, 9]:  # Added 3x3 grid option
            return jsonify({'success': False, 'error': f'Invalid grid size: {grid_size}. Choose from 3x3, 5x5, 7x7, or 9x9'})
        
        max_mines = (grid_size * grid_size) - 2  # Ensure at least 2 safe cells
        if mines_count < 1:
            return jsonify({'success': False, 'error': 'You must place at least 1 mine'})
        elif mines_count > max_mines:
            return jsonify({'success': False, 'error': f'Too many mines! Maximum allowed: {max_mines}'})
        
        if current_user.wallet_balance < bet_amount:
            return jsonify({'success': False, 'error': f'Insufficient balance. You have ₹{current_user.wallet_balance:.2f}'})
        
        # Create a grid of valid positions
        total_cells = grid_size * grid_size
        all_positions = list(range(total_cells))
        
        # Randomly place mines
        mine_positions = random.sample(all_positions, mines_count)
        
        # Calculate max potential multiplier for this configuration
        # Higher risk (more mines) = higher potential reward
        difficulty_factor = mines_count / total_cells
        base_max_multiplier = 2.0  # Minimum max multiplier
        max_potential_multiplier = round(base_max_multiplier / (1 - difficulty_factor) * 2, 2)
        
        # Deduct bet amount from wallet
        current_user.wallet_balance -= bet_amount
        
        # Create a new game
        game = MinesGame(
            user_id=current_user.id,
            bet_amount=bet_amount,
            grid_size=grid_size,
            mines_count=mines_count,
            mine_positions=mine_positions,
            revealed_positions=[],
            multiplier=1.0,
            result="active",  # Changed from "in_progress" to shorter "active"
            winnings=None
        )
        
        db.session.add(game)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'game_id': game.id,
            'grid_size': grid_size,
            'mines_count': mines_count,
            'multiplier': 1.0,
            'max_potential_multiplier': max_potential_multiplier,
            'wallet_balance': current_user.wallet_balance,
            'remaining_safe_cells': total_cells - mines_count
        })
        
    except ValueError as ve:
        db.session.rollback()
        print(f"Value error in start_mines_game: {str(ve)}")
        return jsonify({'success': False, 'error': 'Please enter valid values for bet amount, grid size and mines count'})
    except Exception as e:
        db.session.rollback()
        print(f"Error in start_mines_game: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred while starting the game'})

@app.route('/mines/reveal', methods=['POST'])
@login_required
def reveal_mines_cell():
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        position = int(data.get('position', -1))
        
        # Fast validation checks first
        if position < 0:
            return jsonify({'success': False, 'error': 'Please select a valid position'})
        
        # Find the game with optimized query (select only needed fields)
        game = MinesGame.query.filter_by(id=game_id, user_id=current_user.id).first()
        
        # Security validations
        if not game:
            return jsonify({'success': False, 'error': 'Game not found. Please start a new game.'})
            
        if game.result != 'active':
            return jsonify({'success': False, 'error': 'This game is already over'})
        
        # Get revealed positions and mine positions
        revealed_positions = game.revealed_positions or []
        mine_positions = game.mine_positions
        
        # Basic validations
        if position in revealed_positions:
            return jsonify({'success': False, 'error': 'This cell has already been revealed'})
        
        total_cells = game.grid_size * game.grid_size
        if position >= total_cells:
            return jsonify({'success': False, 'error': f'Invalid position: {position}. Position must be between 0 and {total_cells-1}'})
        
        # Add position to revealed positions
        revealed_positions.append(position)
        game.revealed_positions = revealed_positions
        
        # Check if hit a mine (fast path for failure case)
        if position in mine_positions:
            game.result = 'lost'
            game.winnings = 0
            
            # Create history record for lost game
            history = MineBettingHistory(
                user_id=current_user.id,
                bet_amount=game.bet_amount,
                grid_size=game.grid_size,
                mines_count=game.mines_count,
                cells_revealed=len(revealed_positions),
                mine_positions=game.mine_positions,
                revealed_positions=revealed_positions,
                multiplier_achieved=game.multiplier,
                result='lose',
                winnings=0
            )
            
            db.session.add(history)
            # Commit asynchronously after response for faster UI
            db.session.commit()
            
            return jsonify({
                'success': True,
                'hit_mine': True,
                'mine_positions': mine_positions,
                'revealed_positions': revealed_positions,
                'result': 'lost',
                'wallet_balance': current_user.wallet_balance,
                'message': 'BOOM! You hit a mine. Game over!'
            })
        
        # Calculate new multiplier with optimized formula
        cells_revealed = len(revealed_positions)
        safe_cells = total_cells - game.mines_count
        progress = cells_revealed / safe_cells
        risk_factor = game.mines_count / total_cells
        
        # Use pre-calculated formula values
        base_multiplier = 1.0
        progress_bonus = pow(progress, 1.2)
        risk_bonus = 1.0 + (risk_factor * 10.0)
        new_multiplier = base_multiplier + (risk_bonus * progress_bonus)
        max_multiplier = 1.0 + (safe_cells * risk_factor * 5)
        
        # Round the multiplier
        game.multiplier = round(min(new_multiplier, max_multiplier), 2)
        
        # Calculate potential winnings
        potential_winnings = game.bet_amount * game.multiplier
        
        # Save game state
        db.session.commit()
        
        # Check if all safe cells revealed for auto-cashout
        remaining_safe = safe_cells - cells_revealed
        if remaining_safe == 0:
            return cashout_mines_auto(game)
        
        # Return minimal required data for UI update
        return jsonify({
            'success': True,
            'hit_mine': False,
            'revealed_positions': revealed_positions,
            'multiplier': game.multiplier,
            'potential_winnings': potential_winnings,
            'remaining_safe_cells': remaining_safe
        })
    
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid position value'})
    except Exception as e:
        db.session.rollback()
        print(f"Error in reveal_mines_cell: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred'})

# Helper function for auto-cashout when all safe cells revealed
def cashout_mines_auto(game):
    try:
        # Calculate winnings
        winnings = game.bet_amount * game.multiplier
        
        # Add bonus for clearing all safe cells
        bonus_multiplier = 1.5
        winnings = winnings * bonus_multiplier
        
        # Update user balance
        user = User.query.get(game.user_id)
        user.wallet_balance += winnings
        
        # Update game
        game.result = 'won'
        game.winnings = winnings
        
        # Create history record
        history = MineBettingHistory(
            user_id=game.user_id,
            bet_amount=game.bet_amount,
            grid_size=game.grid_size,
            mines_count=game.mines_count,
            cells_revealed=len(game.revealed_positions),
            mine_positions=game.mine_positions,
            revealed_positions=game.revealed_positions,
            multiplier_achieved=game.multiplier * bonus_multiplier,
            result='win',
            winnings=winnings
        )
        
        db.session.add(history)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'auto_cashout': True,
            'winnings': winnings,
            'bonus_applied': True,
            'bonus_multiplier': bonus_multiplier,
            'wallet_balance': user.wallet_balance,
            'mine_positions': game.mine_positions,
            'message': 'All safe cells cleared! Bonus applied to your winnings!'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error in auto cashout: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred during auto-cashout'})

@app.route('/mines/cashout', methods=['POST'])
@login_required
def cashout_mines():
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        
        game = MinesGame.query.get(game_id)
        if not game:
            return jsonify({'success': False, 'error': 'Game not found'})
            
        if game.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized access'})
            
        if game.result != 'active':
            return jsonify({'success': False, 'error': 'Game is already over'})
        
        # Calculate how many safe cells were revealed
        revealed_count = len(game.revealed_positions)
        
        # Prevent cashout if no cells revealed yet
        if revealed_count == 0:
            return jsonify({'success': False, 'error': 'You must reveal at least one cell before cashing out'})
    
        # Calculate winnings
        winnings = game.bet_amount * game.multiplier
        
        # Update user balance
        current_user.wallet_balance += winnings
        
        # Update game
        game.result = 'won'
        game.winnings = winnings
        
        # Create history record
        history = MineBettingHistory(
            user_id=current_user.id,
            bet_amount=game.bet_amount,
            grid_size=game.grid_size,
            mines_count=game.mines_count,
            cells_revealed=revealed_count,
            mine_positions=game.mine_positions,
            revealed_positions=game.revealed_positions,
            multiplier_achieved=game.multiplier,
            result='win',
            winnings=winnings
        )
        
        db.session.add(history)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'winnings': winnings,
            'cells_revealed': revealed_count,
            'multiplier': game.multiplier,
            'wallet_balance': current_user.wallet_balance,
            'mine_positions': game.mine_positions,
            'message': f'Cashed out with {revealed_count} safe cells revealed!'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error in cashout_mines: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred during cashout'})



#



@app.route('/plinko')
@login_required
def plinko_game():
    return render_template('plinko.html', balance=current_user.wallet_balance)

@app.route('/plinko/place-bet', methods=['POST'])
@login_required
def plinko_place_bet():
    try:
        data = request.get_json()
        bet_amount = float(data.get('bet_amount', 0))
        risk_level = data.get('risk_level', 'low')
        rows = int(data.get('rows', 12))
        
        # Validate inputs
        if bet_amount <= 0:
            return jsonify({'success': False, 'error': 'Invalid bet amount'})
        
        if current_user.wallet_balance < bet_amount:
            return jsonify({'success': False, 'error': 'Insufficient balance'})
        
        if risk_level not in ['low', 'medium', 'high']:
            return jsonify({'success': False, 'error': 'Invalid risk level'})
        
        if rows not in [8, 12, 16]:
            return jsonify({'success': False, 'error': 'Invalid rows'})
        
        # Generate path
        path = generate_plinko_path(rows)
        
        # Calculate landing position
        landing_position = calculate_landing_position(path, rows)
        
        # Get multiplier based on landing position and risk level
        multiplier = get_plinko_multiplier(landing_position, rows, risk_level)
    
        # Calculate winnings
        winnings = bet_amount * multiplier
    
        # Update user balance
        current_user.wallet_balance -= bet_amount
        
        if multiplier > 0:
            current_user.wallet_balance += winnings
            
        # Save game
        game = PlinkoGame(
            user_id=current_user.id,
            bet_amount=bet_amount,
            risk_level=risk_level,
            rows=rows,
            path=''.join(path),
            landing_position=landing_position,
            multiplier=multiplier,
            winnings=winnings
        )
        
        db.session.add(game)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'bet_id': game.id,
            'path': path,
            'landing_position': landing_position,
            'multiplier': multiplier,
            'winnings': winnings,
            'new_balance': current_user.wallet_balance
        })
    except Exception as e:
        db.session.rollback()
        print("Error in plinko_place_bet:", str(e))
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/plinko/check-bet', methods=['POST'])
@login_required
def plinko_check_bet():
    try:
        data = request.get_json()
        bet_id = data.get('bet_id')
        
        if not bet_id:
            return jsonify({'success': False, 'error': 'Invalid bet ID'})
        
        # Find the bet in the database
        game = PlinkoGame.query.filter_by(id=bet_id, user_id=current_user.id).first()
        
        if not game:
            return jsonify({'success': False, 'error': 'Bet not found'})
        
        # Convert path string back to list
        path = list(game.path)
        
        return jsonify({
            'success': True,
            'bet_id': game.id,
            'path': path,
            'landing_position': game.landing_position,
            'multiplier': game.multiplier,
            'winnings': game.winnings,
            'current_balance': current_user.wallet_balance
        })
    except Exception as e:
        print("Error in plinko_check_bet:", str(e))
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/plinko/history')
@login_required
def plinko_history():
    try:
        # Get user's recent games
        games = PlinkoGame.query.filter_by(
            user_id=current_user.id
        ).order_by(PlinkoGame.timestamp.desc()).limit(20).all()
        
        history = []
        for game in games:
            history.append({
                'bet_amount': game.bet_amount,
                'risk_level': game.risk_level,
                'rows': game.rows,
                'multiplier': game.multiplier,
                'winnings': game.winnings,
                'timestamp': game.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        print("Error in plinko_history:", str(e))
        return jsonify({'success': False, 'error': 'An error occurred'})

# Helper functions for Plinko
def generate_plinko_path(rows):
    """Generate a random path for the plinko ball"""
    path = []
    for _ in range(rows):
        # Each pin has 50% chance of going left or right
        direction = 'L' if random.random() < 0.5 else 'R'
        path.append(direction)
    return path

def calculate_landing_position(path, rows):
    """Calculate the final landing position based on the path"""
    position = 0
    for direction in path:
        if direction == 'R':
            position += 1
    
    # The number of buckets is rows + 1
    return position

def get_plinko_multiplier(position, rows, risk_level):
    """Get the multiplier based on landing position, rows, and risk level"""
    # Multiplier tables
    multiplier_tables = {
        'low': {
            8: [2, 1.4, 1.2, 0.9, 0.5, 0.9, 1.2, 1.4, 2],
            12: [8, 3, 2, 1.5, 1.2, 0.8, 0.5, 0.8, 1.2, 1.5, 2, 3, 8],
            16: [15, 5, 3, 2, 1.4, 1.1, 0.8, 0.5, 0.3, 0.5, 0.8, 1.1, 1.4, 2, 3, 5, 15]
        },
        'medium': {
            8: [3.5, 2, 1.3, 0.7, 0.3, 0.7, 1.3, 2, 3.5],
            12: [12, 5, 3, 1.6, 1.1, 0.7, 0.3, 0.7, 1.1, 1.6, 3, 5, 12],
            16: [25, 8, 4, 2.4, 1.6, 1, 0.7, 0.4, 0.2, 0.4, 0.7, 1, 1.6, 2.4, 4, 8, 25]
        },
        'high': {
            8: [5, 2.5, 1.4, 0.4, 0.1, 0.4, 1.4, 2.5, 5],
            12: [18, 8, 3, 1.5, 0.8, 0.3, 0.1, 0.3, 0.8, 1.5, 3, 8, 18],
            16: [50, 12, 5, 3, 1.8, 1, 0.4, 0.2, 0.1, 0.2, 0.4, 1, 1.8, 3, 5, 12, 50]
        }
    }
    
    return multiplier_tables[risk_level][rows][position]

# Slot Game Model
class SlotGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    symbols = db.Column(db.String(50), nullable=False)  # Store the symbols as a string
    multiplier = db.Column(db.Float, nullable=False)
    winnings = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='slot_games')

@app.route('/slots')
@login_required
def slots_game():
    return render_template('slots.html', balance=current_user.wallet_balance)

@app.route('/slots/spin', methods=['POST'])
@login_required
def slots_spin():
    try:
        data = request.get_json()
        bet_amount = float(data.get('bet_amount', 0))
        
        # Validate inputs
        if bet_amount <= 0:
            return jsonify({'success': False, 'error': 'Invalid bet amount'})
        
        if current_user.wallet_balance < bet_amount:
            return jsonify({'success': False, 'error': 'Insufficient balance'})
        
        # Define symbols and their probabilities
        symbols = ["🍒", "🍋", "🍇", "🍉", "🔔", "💎", "7️⃣", "🎰"]
        probabilities = [0.30, 0.25, 0.20, 0.15, 0.05, 0.03, 0.015, 0.005]
        
        # Generate random symbols for each reel
        result = []
        for _ in range(3):  # 3 reels
            symbol = random.choices(symbols, weights=probabilities, k=1)[0]
            result.append(symbol)
        
        # Calculate multiplier based on result
        multiplier = get_slot_multiplier(result)
        
        # Calculate winnings
        winnings = bet_amount * multiplier
        
        # Update user balance
        current_user.wallet_balance -= bet_amount
        if multiplier > 0:
            current_user.wallet_balance += winnings
        
        # Save game
        game = SlotGame(
            user_id=current_user.id,
            bet_amount=bet_amount,
            symbols=",".join(result),
            multiplier=multiplier,
            winnings=winnings
        )
        
        db.session.add(game)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'bet_id': game.id,
            'symbols': result,
            'multiplier': multiplier,
            'winnings': winnings,
            'new_balance': current_user.wallet_balance
        })
    except Exception as e:
        db.session.rollback()
        print("Error in slots_spin:", str(e))
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/slots/history')
@login_required
def slots_history():
    try:
        # Get user's recent games
        games = SlotGame.query.filter_by(
            user_id=current_user.id
        ).order_by(SlotGame.timestamp.desc()).limit(20).all()
        
        history = []
        for game in games:
            history.append({
                'bet_amount': game.bet_amount,
                'symbols': game.symbols.split(','),
                'multiplier': game.multiplier,
                'winnings': game.winnings,
                'timestamp': game.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        print("Error in slots_history:", str(e))
        return jsonify({'success': False, 'error': 'An error occurred'})

# Helper function for Slots
def get_slot_multiplier(symbols):
    """Calculate multiplier based on slot symbols combination"""
    # All symbols are the same (jackpot)
    if symbols[0] == symbols[1] == symbols[2]:
        if symbols[0] == "🎰":  # Triple 777
            return 100.0
        elif symbols[0] == "7️⃣":  # Triple 7
            return 50.0
        elif symbols[0] == "💎":  # Triple diamond
            return 25.0
        elif symbols[0] == "🔔":  # Triple bell
            return 15.0
        elif symbols[0] == "🍉":  # Triple watermelon
            return 10.0
        elif symbols[0] == "🍇":  # Triple grape
            return 5.0
        elif symbols[0] == "🍋":  # Triple lemon
            return 3.0
        elif symbols[0] == "🍒":  # Triple cherry
            return 2.0
    
    # Two same symbols
    elif (symbols[0] == symbols[1]) or (symbols[1] == symbols[2]) or (symbols[0] == symbols[2]):
        if "🎰" in symbols:
            return 15.0
        elif "7️⃣" in symbols:
            return 10.0
        elif "💎" in symbols:
            return 5.0
        elif "🔔" in symbols:
            return 3.0
        elif "🍉" in symbols:
            return 2.0
        elif "🍇" in symbols:
            return 1.5
        elif "🍋" in symbols:
            return 1.2
        elif "🍒" in symbols:
            return 1.1
    
    # Any combination with at least one 7
    elif "7️⃣" in symbols or "🎰" in symbols:
        return 0.5
    
    # No win
    return 0.0

@app.route('/megaslots')
@login_required
def mega_slots_game():
    return render_template('megaslots.html', balance=current_user.wallet_balance)

@app.route('/megaslots/spin', methods=['POST'])
@login_required
def mega_slots_spin():
    try:
        data = request.get_json()
        bet_amount = float(data.get('bet_amount', 0))
        
        # Validate inputs
        if bet_amount <= 0:
            return jsonify({'success': False, 'error': 'Invalid bet amount'})
        
        if current_user.wallet_balance < bet_amount:
            return jsonify({'success': False, 'error': 'Insufficient balance'})
        
        # Define symbols and their probabilities (more premium symbols)
        symbols = ["🍒", "🍋", "🍇", "🍉", "🍊", "🍎", "🔔", "💎", "⭐", "🎯", "7️⃣", "🎰"]
        probabilities = [0.20, 0.18, 0.15, 0.12, 0.10, 0.08, 0.05, 0.045, 0.035, 0.025, 0.01, 0.005]
        
        # Generate random symbols for each reel (5 reels)
        result = []
        for _ in range(5):  # 5 reels
            symbol = random.choices(symbols, weights=probabilities, k=1)[0]
            result.append(symbol)
        
        # Calculate multiplier based on result
        multiplier = get_mega_slot_multiplier(result)
        
        # Calculate winnings
        winnings = bet_amount * multiplier
        
        # Update user balance
        current_user.wallet_balance -= bet_amount
        if multiplier > 0:
            current_user.wallet_balance += winnings
        
        # Save game
        game = MegaSlotGame(
            user_id=current_user.id,
            bet_amount=bet_amount,
            symbols=",".join(result),
            multiplier=multiplier,
            winnings=winnings
        )
        
        db.session.add(game)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'bet_id': game.id,
            'symbols': result,
            'multiplier': multiplier,
            'winnings': winnings,
            'new_balance': current_user.wallet_balance
        })
    except Exception as e:
        db.session.rollback()
        print("Error in mega_slots_spin:", str(e))
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/megaslots/history')
@login_required
def mega_slots_history():
    try:
        # Get user's recent games
        games = MegaSlotGame.query.filter_by(
            user_id=current_user.id
        ).order_by(MegaSlotGame.timestamp.desc()).limit(20).all()
        
        history = []
        for game in games:
            history.append({
                'bet_amount': game.bet_amount,
                'symbols': game.symbols.split(','),
                'multiplier': game.multiplier,
                'winnings': game.winnings,
                'timestamp': game.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        print("Error in mega_slots_history:", str(e))
        return jsonify({'success': False, 'error': 'An error occurred'})

# Helper function for MegaSlots
def get_mega_slot_multiplier(symbols):
    """Calculate multiplier based on mega slot symbols combination"""
    # Count symbols
    symbol_count = {}
    for s in symbols:
        symbol_count[s] = symbol_count.get(s, 0) + 1
    
    # Get the most frequent symbol and its count
    most_common = max(symbol_count.items(), key=lambda x: x[1])
    most_common_symbol = most_common[0]
    most_common_count = most_common[1]
    
    # All 5 symbols are the same (mega jackpot)
    if most_common_count == 5:
        if most_common_symbol == "🎰":  # Five slots
            return 1000.0
        elif most_common_symbol == "7️⃣":  # Five 7s
            return 500.0
        elif most_common_symbol == "🎯":  # Five targets
            return 250.0
        elif most_common_symbol == "⭐":  # Five stars
            return 200.0
        elif most_common_symbol == "💎":  # Five diamonds
            return 150.0
        elif most_common_symbol == "🔔":  # Five bells
            return 100.0
        elif most_common_symbol in ["🍎", "🍊"]:  # Five premium fruits
            return 50.0
        elif most_common_symbol in ["🍉", "🍇"]:  # Five middle fruits
            return 25.0
        elif most_common_symbol in ["🍋", "🍒"]:  # Five basic fruits
            return 15.0
    
    # Four of a kind
    elif most_common_count == 4:
        if most_common_symbol == "🎰":
            return 100.0
        elif most_common_symbol == "7️⃣":
            return 75.0
        elif most_common_symbol in ["🎯", "⭐", "💎"]:
            return 50.0
        elif most_common_symbol in ["🔔", "🍎", "🍊"]:
            return 25.0
        elif most_common_symbol in ["🍉", "🍇"]:
            return 10.0
        elif most_common_symbol in ["🍋", "🍒"]:
            return 5.0
    
    # Three of a kind
    elif most_common_count == 3:
        if most_common_symbol == "🎰":
            return 25.0
        elif most_common_symbol == "7️⃣":
            return 15.0
        elif most_common_symbol in ["🎯", "⭐", "💎"]:
            return 10.0
        elif most_common_symbol in ["🔔", "🍎", "🍊"]:
            return 5.0
        elif most_common_symbol in ["🍉", "🍇"]:
            return 2.5
        elif most_common_symbol in ["🍋", "🍒"]:
            return 1.5
    
    # Two pairs
    pairs = sum(1 for count in symbol_count.values() if count >= 2)
    if pairs >= 2:
        if "🎰" in symbol_count and symbol_count["🎰"] >= 2:
            return 10.0
        elif "7️⃣" in symbol_count and symbol_count["7️⃣"] >= 2:
            return 5.0
        elif any(s in ["🎯", "⭐", "💎"] and symbol_count[s] >= 2 for s in symbol_count):
            return 3.0
        else:
            return 2.0
    
    # One pair of premium symbols
    elif most_common_count == 2:
        if most_common_symbol in ["🎰", "7️⃣", "🎯", "⭐", "💎"]:
            return 1.5
    
    # Special combination: any 7 or slot machine
    if "7️⃣" in symbols or "🎰" in symbols:
        return 0.5
    
    # No win
    return 0.0

@app.route('/luckywheel')
@login_required
def lucky_wheel_game():
    return render_template('luckywheel.html', balance=current_user.wallet_balance)

@app.route('/luckywheel/spin', methods=['POST'])
@login_required
def lucky_wheel_spin():
    try:
        data = request.get_json()
        bet_amount = float(data.get('bet_amount', 0))
        
        # Validate inputs
        if bet_amount <= 0:
            return jsonify({'success': False, 'error': 'Invalid bet amount'})
        
        if current_user.wallet_balance < bet_amount:
            return jsonify({'success': False, 'error': 'Insufficient balance'})
        
        # Define wheel segments and their values
        wheel_segments = [
            {"position": 0, "symbol": "⭐", "multiplier": 5.0},    # Star - high value
            {"position": 1, "symbol": "🍒", "multiplier": 1.5},    # Cherry - low value
            {"position": 2, "symbol": "💎", "multiplier": 10.0},   # Diamond - high value
            {"position": 3, "symbol": "🍋", "multiplier": 1.2},    # Lemon - low value
            {"position": 4, "symbol": "7️⃣", "multiplier": 25.0},   # Seven - jackpot
            {"position": 5, "symbol": "🍉", "multiplier": 2.0},    # Watermelon - medium value
            {"position": 6, "symbol": "🎯", "multiplier": 4.0},    # Target - medium-high value
            {"position": 7, "symbol": "🍇", "multiplier": 1.8},    # Grapes - medium-low value
            {"position": 8, "symbol": "🔔", "multiplier": 3.0},    # Bell - medium value
            {"position": 9, "symbol": "❌", "multiplier": 0.0},    # X - lose
            {"position": 10, "symbol": "🎰", "multiplier": 15.0},  # Slot machine - high value
            {"position": 11, "symbol": "🍊", "multiplier": 1.3}    # Orange - low value
        ]
        
        # Weights for each position (adjust probability)
        weights = [
            0.03,   # ⭐ - 3%
            0.12,   # 🍒 - 12%
            0.02,   # 💎 - 2%
            0.12,   # 🍋 - 12%
            0.01,   # 7️⃣ - 1% (rare jackpot)
            0.10,   # 🍉 - 10%
            0.05,   # 🎯 - 5%
            0.10,   # 🍇 - 10%
            0.08,   # 🔔 - 8%
            0.20,   # ❌ - 20% (lose)
            0.02,   # 🎰 - 2%
            0.15    # 🍊 - 15%
        ]
        
        # Randomly select a wheel position based on weights
        position = random.choices(range(len(wheel_segments)), weights=weights, k=1)[0]
        selected_segment = wheel_segments[position]
        
        # Calculate winnings
        multiplier = selected_segment['multiplier']
        winnings = bet_amount * multiplier
        
        # Update user balance
        current_user.wallet_balance -= bet_amount
        if multiplier > 0:
            current_user.wallet_balance += winnings
        
        # Save game
        game = LuckyWheelSlot(
            user_id=current_user.id,
            bet_amount=bet_amount,
            wheel_position=position,
            symbol=selected_segment['symbol'],
            multiplier=multiplier,
            winnings=winnings
        )
        
        db.session.add(game)
        db.session.commit()
        
        # Return result to client
        return jsonify({
            'success': True,
            'wheel_position': position,
            'symbol': selected_segment['symbol'],
            'multiplier': multiplier,
            'winnings': winnings,
            'new_balance': current_user.wallet_balance
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in lucky_wheel_spin: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/luckywheel/history')
@login_required
def lucky_wheel_history():
    try:
        # Get user's recent games
        games = LuckyWheelSlot.query.filter_by(
            user_id=current_user.id
        ).order_by(LuckyWheelSlot.timestamp.desc()).limit(20).all()
        
        history = []
        for game in games:
            history.append({
                'bet_amount': game.bet_amount,
                'wheel_position': game.wheel_position,
                'symbol': game.symbol,
                'multiplier': game.multiplier,
                'winnings': game.winnings,
                'timestamp': game.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        print(f"Error in lucky_wheel_history: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/aviator')
@login_required
def aviator_game():
    return render_template('aviator.html')

@app.route('/aviator/place-bet', methods=['POST'])
@login_required
def aviator_place_bet():
    try:
        data = request.get_json()
        bet_amount = float(data.get('bet_amount', 0))
        auto_cashout = data.get('auto_cashout')
        
        if bet_amount <= 0:
            return jsonify({'success': False, 'error': 'Invalid bet amount'})
        
        if current_user.wallet_balance < bet_amount:
            return jsonify({'success': False, 'error': 'Insufficient balance'})
        
        # Generate a crash point - this determines when the game will end
        # Higher values are less likely (exponential distribution)
        crash_point = 1.00
        r = random.random()
        if r < 0.99:  # 99% chance the game will continue beyond 1.00
            # Generate crash point between 1.01 and 100.00
            crash_point = round(math.floor(100 * math.log(1 / (1 - random.random() * 0.99)) / math.log(100)) / 100 + 1.00, 2)
        
        # Deduct bet amount from user balance
        current_user.wallet_balance -= bet_amount
        
        # Create a pending game record
        game = AviatorHistory(
            user_id=current_user.id,
            bet_amount=bet_amount,
            multiplier=1.0,
            auto_cashout=auto_cashout,
            winnings=0.0,
            result='pending'
        )
        db.session.add(game)
        db.session.commit()
        
        # Return game data
        return jsonify({
            'success': True,
            'new_balance': current_user.wallet_balance,
            'crash_point': crash_point,
            'bet_id': game.id,
            'username': current_user.name  # Include username for display in active bets
        })
    except Exception as e:
        db.session.rollback()
        print("Error in aviator_place_bet:", str(e))
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/aviator/cashout', methods=['POST'])
@login_required
def aviator_cashout():
    try:
        data = request.get_json()
        multiplier = float(data.get('multiplier', 1.00))
        bet_id = data.get('bet_id')
        
        # Find the game by ID
        game = AviatorHistory.query.get(bet_id)
        
        if not game or game.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Game not found'})
            
        if game.result != 'pending':
            return jsonify({'success': False, 'error': 'Game already completed'})
            
        # Calculate winnings
        winnings = game.bet_amount * multiplier
        
        # Update user balance
        current_user.wallet_balance += winnings
        
        # Update game record
        game.multiplier = multiplier
        game.winnings = winnings
        game.result = 'win'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'new_balance': current_user.wallet_balance,
            'winnings': winnings,
            'username': current_user.name  # Include username for display in active bets
        })
    except Exception as e:
        db.session.rollback()
        print("Error in aviator_cashout:", str(e))
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/aviator/history')
@login_required
def aviator_history():
    try:
        # Get user's recent games
        games = AviatorHistory.query.filter_by(
            user_id=current_user.id
        ).order_by(AviatorHistory.timestamp.desc()).limit(20).all()
        
        history = []
        for game in games:
            history.append({
                'bet_amount': game.bet_amount,
                'multiplier': game.multiplier,
                'auto_cashout': game.auto_cashout,
                'winnings': game.winnings,
                'result': game.result,
                'timestamp': game.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        print("Error in aviator_history:", str(e))
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/aviator/crash', methods=['POST'])
@login_required
def aviator_crash():
    try:
        data = request.get_json()
        bet_id = data.get('bet_id')
        crash_point = float(data.get('crash_point', 1.00))
        
        # Find the game
        game = AviatorHistory.query.get(bet_id)
        
        if not game or game.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Game not found'})
            
        if game.result != 'pending':
            return jsonify({'success': False, 'error': 'Game already completed'})
        
        # Update game record to show loss
        game.multiplier = crash_point
        game.winnings = 0
        game.result = 'loss'
        db.session.commit()
        
        return jsonify({
            'success': True
        })
    except Exception as e:
        db.session.rollback()
        print("Error in aviator_crash:", str(e))
        return jsonify({'success': False, 'error': 'An error occurred'})

# Fix mines_game table result column length
@app.route('/fix-mines-game-table', methods=['GET'])
@login_required
def fix_mines_game_table():
    try:
        # Check if the user is admin (you can add your own admin check logic)
        if current_user.id != 1:  # Assuming user id 1 is admin
            flash('Unauthorized access', 'danger')
            return redirect(url_for('home'))
            
        # Execute raw SQL to alter the table
        with db.engine.connect() as connection:
            # First check if the column needs modification
            connection.execute(db.text("ALTER TABLE mines_game MODIFY COLUMN result VARCHAR(20);"))
            
        flash('Mines game table structure updated successfully!', 'success')
        return redirect(url_for('home'))
    except Exception as e:
        flash(f'Error updating database: {str(e)}', 'danger')
        return redirect(url_for('home'))

@app.route('/dice-betting')
@login_required
def dice_betting():
    return render_template('dice_betting.html', balance=current_user.wallet_balance)

@app.route('/dice-betting/play', methods=['POST'])
@login_required
def dice_betting_play():
    try:
        data = request.get_json()
        bet_amount = float(data.get('bet_amount', 0))
        bet_type = data.get('bet_type')
        bet_value = data.get('bet_value')
        
        # Validate bet amount
        if bet_amount <= 0:
            return jsonify({'success': False, 'error': 'Please enter a valid bet amount'})
            
        if current_user.wallet_balance < bet_amount:
            return jsonify({'success': False, 'error': f'Insufficient balance. You have ₹{current_user.wallet_balance:.2f}'})
        
        # Validate bet type
        if bet_type not in ['exact', 'range', 'odd_even', 'high_low']:
            return jsonify({'success': False, 'error': 'Invalid bet type'})
        
        # Roll the dice (1-6)
        dice_result = random.randint(1, 6)
        
        # Determine if bet won and calculate multiplier/winnings
        won = False
        multiplier = 0
        
        if bet_type == 'exact':
            # Exact number prediction (1-6)
            try:
                exact_number = int(bet_value)
                if exact_number < 1 or exact_number > 6:
                    return jsonify({'success': False, 'error': 'Number must be between 1 and 6'})
                
                won = (dice_result == exact_number)
                multiplier = 6.0 if won else 0  # 6:1 payout for exact match
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid number format'})
                
        elif bet_type == 'range':
            # Range prediction (e.g., "1-3" or "4-6")
            try:
                start, end = map(int, bet_value.split('-'))
                if start < 1 or end > 6 or start > end:
                    return jsonify({'success': False, 'error': 'Invalid range'})
                
                won = (dice_result >= start and dice_result <= end)
                range_size = end - start + 1
                multiplier = 6.0 / range_size if won else 0  # Adjust payout based on range size
            except (ValueError, IndexError):
                return jsonify({'success': False, 'error': 'Invalid range format'})
                
        elif bet_type == 'odd_even':
            # Odd/Even prediction
            if bet_value not in ['odd', 'even']:
                return jsonify({'success': False, 'error': 'Value must be "odd" or "even"'})
                
            is_odd = (dice_result % 2 == 1)
            won = (bet_value == 'odd' and is_odd) or (bet_value == 'even' and not is_odd)
            multiplier = 2.0 if won else 0  # 2:1 payout for odd/even
            
        elif bet_type == 'high_low':
            # High/Low prediction
            if bet_value not in ['high', 'low']:
                return jsonify({'success': False, 'error': 'Value must be "high" or "low"'})
                
            is_high = dice_result > 3
            won = (bet_value == 'high' and is_high) or (bet_value == 'low' and not is_high)
            multiplier = 2.0 if won else 0  # 2:1 payout for high/low
        
        # Calculate winnings
        winnings = bet_amount * multiplier if won else 0
        
        # Update user balance
        current_user.wallet_balance -= bet_amount
        if won:
            current_user.wallet_balance += winnings
        
        # Create game record
        game = EnhancedDiceGame(
            user_id=current_user.id,
            bet_amount=bet_amount,
            bet_type=bet_type,
            bet_value=bet_value,
            dice_result=dice_result,
            multiplier=multiplier,
            winnings=winnings,
            result='win' if won else 'lose'
        )
        
        db.session.add(game)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'dice_result': dice_result,
            'won': won,
            'multiplier': multiplier,
            'winnings': winnings,
            'new_balance': current_user.wallet_balance
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in dice_betting_play: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/dice-betting/history')
@login_required
def dice_betting_history():
    try:
        # Get user's recent games
        games = EnhancedDiceGame.query.filter_by(
            user_id=current_user.id
        ).order_by(EnhancedDiceGame.timestamp.desc()).limit(20).all()
        
        history = []
        for game in games:
            history.append({
                'bet_amount': game.bet_amount,
                'bet_type': game.bet_type,
                'bet_value': game.bet_value,
                'dice_result': game.dice_result,
                'multiplier': game.multiplier,
                'winnings': game.winnings,
                'result': game.result,
                'timestamp': game.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        print(f"Error in dice_betting_history: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/coin-flip')
@login_required
def coin_flip():
    return render_template('coin_flip.html', balance=current_user.wallet_balance)

@app.route('/coin-flip/play', methods=['POST'])
@login_required
def coin_flip_play():
    try:
        data = request.get_json()
        bet_amount = float(data.get('bet_amount', 0))
        user_choice = data.get('user_choice')  # 'heads' or 'tails'
        
        # Validate bet amount
        if bet_amount <= 0:
            return jsonify({'success': False, 'error': 'Please enter a valid bet amount'})
        
        if current_user.wallet_balance < bet_amount:
            return jsonify({'success': False, 'error': f'Insufficient balance. You have ₹{current_user.wallet_balance:.2f}'})
        
        # Validate bet choice
        if user_choice not in ['heads', 'tails']:
            return jsonify({'success': False, 'error': 'Invalid choice. Please select heads or tails'})
        
        # Generate a random number between 1 and 100
        random_num = random.randint(1, 100)
        
        # 10% winning chance
        # If random number is 1-10, user wins, regardless of their choice
        # Then set the result to match their choice for a "fair" appearance
        will_win = random_num <= 10
        
        if will_win:
            # User will win, set result to match their choice
            result = user_choice
        else:
            # User will lose, set result opposite to their choice
            result = 'tails' if user_choice == 'heads' else 'heads'
        
        # Determine if bet won (should match the will_win variable)
        won = (user_choice == result)  # This should always match will_win now
        multiplier = 9.5  # 9.5x payout (matches approximately 10% win rate)
        
        # Calculate winnings
        winnings = bet_amount * multiplier if won else 0
        
        # Update user balance
        current_user.wallet_balance -= bet_amount
        if won:
            current_user.wallet_balance += winnings
        
        # Create game record
        game = CoinFlipGame(
            user_id=current_user.id,
            bet_amount=bet_amount,
            user_choice=user_choice,
            result=result,
            outcome='win' if won else 'lose',
            multiplier=multiplier,
            winnings=winnings
        )
        
        db.session.add(game)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'result': result,
            'won': won,
            'winnings': winnings,
            'new_balance': current_user.wallet_balance,
            'multiplier': multiplier
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in coin_flip_play: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/coin-flip/history')
@login_required
def coin_flip_history():
    try:
        # Get user's recent games
        games = CoinFlipGame.query.filter_by(
            user_id=current_user.id
        ).order_by(CoinFlipGame.timestamp.desc()).limit(20).all()
        
        history = []
        for game in games:
            history.append({
                'bet_amount': game.bet_amount,
                'user_choice': game.user_choice,
                'result': game.result,
                'outcome': game.outcome,
                'winnings': game.winnings,
                'timestamp': game.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        print(f"Error in coin_flip_history: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/odd-even-betting')
@login_required
def odd_even_betting():
    return render_template('odd_even_betting.html', balance=current_user.wallet_balance)

@app.route('/odd-even-betting/play', methods=['POST'])
@login_required
def odd_even_betting_play():
    try:
        data = request.get_json()
        bet_amount = float(data.get('bet_amount', 0))
        user_choice = data.get('user_choice')  # 'odd' or 'even'
        
        # Validate bet amount
        if bet_amount <= 0:
            return jsonify({'success': False, 'error': 'Please enter a valid bet amount'})
            
        if current_user.wallet_balance < bet_amount:
            return jsonify({'success': False, 'error': f'Insufficient balance. You have ₹{current_user.wallet_balance:.2f}'})
        
        # Validate user choice
        if user_choice not in ['odd', 'even']:
            return jsonify({'success': False, 'error': 'Invalid choice. Please select odd or even'})
        
        # Generate a random number between 1 and 100
        number = random.randint(1, 100)
        
        # Determine if the number is odd or even
        is_odd = number % 2 == 1
        number_type = 'odd' if is_odd else 'even'
        
        # Determine if bet won
        won = (user_choice == number_type)
        multiplier = 1.9  # 1.9x payout for winning
        
        # Calculate winnings
        winnings = bet_amount * multiplier if won else 0
        
        # Update user balance
        current_user.wallet_balance -= bet_amount
        if won:
            current_user.wallet_balance += winnings
        
        # Create game record
        game = OddEvenBettingGame(
            user_id=current_user.id,
            bet_amount=bet_amount,
            user_choice=user_choice,
            number=number,
            result='win' if won else 'lose',
            multiplier=multiplier,
            winnings=winnings
        )
        
        db.session.add(game)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'number': number,
            'number_type': number_type,
            'won': won,
            'multiplier': multiplier,
            'winnings': winnings,
            'new_balance': current_user.wallet_balance
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in odd_even_betting_play: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/odd-even-betting/history')
@login_required
def odd_even_betting_history():
    try:
        # Get user's recent games
        games = OddEvenBettingGame.query.filter_by(
            user_id=current_user.id
        ).order_by(OddEvenBettingGame.timestamp.desc()).limit(20).all()
        
        history = []
        for game in games:
            history.append({
                'bet_amount': game.bet_amount,
                'user_choice': game.user_choice,
                'number': game.number,
                'number_type': 'odd' if game.number % 2 == 1 else 'even',
                'result': game.result,
                'winnings': game.winnings,
                'timestamp': game.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        print(f"Error in odd_even_betting_history: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/admin/games-management')
def admin_games_management():
    """Admin route for managing all games"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    return render_template('admin_games_management.html')

@app.route('/admin/game-settings', methods=['GET', 'POST'])
def admin_game_settings():
    """Admin route for updating game settings"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        game_type = request.form.get('game_type')
        action = request.form.get('action')
        
        # Example of toggling game status (you would need to add a game_status table in your database)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if action == 'toggle':
                # Toggle game status (enable/disable)
                cursor.execute("UPDATE game_settings SET is_active = NOT is_active WHERE game_type = %s", (game_type,))
                flash(f"{game_type} status toggled successfully", "success")
            elif action == 'update_odds':
                # Update game odds/multipliers
                multiplier = float(request.form.get('multiplier', 1.0))
                cursor.execute("UPDATE game_settings SET base_multiplier = %s WHERE game_type = %s", 
                              (multiplier, game_type))
                flash(f"{game_type} multiplier updated to {multiplier}", "success")
            
            conn.commit()
            conn.close()
        except Exception as e:
            flash(f"Error updating game settings: {str(e)}", "danger")
    
    # Fetch current game settings to display in the form
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM game_settings")
        game_settings = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"Error fetching game settings: {str(e)}")
        # If the table doesn't exist yet, create sample settings
        game_settings = [
            {'game_type': 'Mines', 'is_active': True, 'base_multiplier': 1.0},
            {'game_type': 'Plinko', 'is_active': True, 'base_multiplier': 1.0},
            {'game_type': 'Slots', 'is_active': True, 'base_multiplier': 1.0},
            {'game_type': 'MegaSlots', 'is_active': True, 'base_multiplier': 1.0},
            {'game_type': 'LuckyWheel', 'is_active': True, 'base_multiplier': 1.0},
            {'game_type': 'Aviator', 'is_active': True, 'base_multiplier': 1.0},
            {'game_type': 'CoinFlip', 'is_active': True, 'base_multiplier': 1.0},
            {'game_type': 'OddEven', 'is_active': True, 'base_multiplier': 1.0}
        ]
    
    return render_template('admin_game_settings.html', game_settings=game_settings)

@app.route('/admin/game-activity')
def admin_game_activity():
    """Admin route for viewing game activity"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    game_type = request.args.get('game_type', 'all')
    limit = int(request.args.get('limit', 50))
    
    activity = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if game_type == 'all':
            # Fetch from all game tables
            tables = [
                ('mines_game', 'Mines'),
                ('plinko_game', 'Plinko'),
                ('slot_game', 'Slots'),
                ('mega_slot_game', 'MegaSlots'),
                ('lucky_wheel_slot', 'LuckyWheel'),
                ('aviator_history', 'Aviator'),
                ('coin_flip_game', 'CoinFlip'),
                ('odd_even_betting_game', 'OddEven'),
                ('super_slot_game', 'SuperSlot'),
                ('treasure_hunt_game', 'TreasureHunt')
            ]
            
            # Union query to get recent activity from all games
            combined_query = ""
            for i, (table, name) in enumerate(tables):
                if i > 0:
                    combined_query += " UNION ALL "
                combined_query += f"""
                    (SELECT '{name}' as game_type, user_id, bet_amount, 
                        CASE 
                            WHEN result IS NOT NULL THEN result
                            WHEN winnings > 0 THEN 'win' 
                            ELSE 'lose' 
                        END as result, 
                        timestamp 
                    FROM {table} ORDER BY timestamp DESC LIMIT {limit})
                """
            
            combined_query += f" ORDER BY timestamp DESC LIMIT {limit}"
            cursor.execute(combined_query)
        else:
            # Query for a specific game type
            table_map = {
                'Mines': 'mines_game',
                'Plinko': 'plinko_game',
                'Slots': 'slot_game',
                'MegaSlots': 'mega_slot_game',
                'LuckyWheel': 'lucky_wheel_slot',
                'Aviator': 'aviator_history',
                'CoinFlip': 'coin_flip_game',
                'OddEven': 'odd_even_betting_game',
                'SuperSlot': 'super_slot_game',
                'TreasureHunt': 'treasure_hunt_game'
            }
            
            table = table_map.get(game_type)
            if table:
                cursor.execute(f"""
                    SELECT %s as game_type, user_id, bet_amount, 
                    CASE 
                        WHEN result IS NOT NULL THEN result
                        WHEN winnings > 0 THEN 'win' 
                        ELSE 'lose' 
                    END as result, 
                    timestamp 
                    FROM {table} ORDER BY timestamp DESC LIMIT %s
                """, (game_type, limit))
        
        activity = cursor.fetchall()
        
        # Get additional user info
        for item in activity:
            cursor.execute("SELECT name, phone FROM user WHERE id = %s", (item['user_id'],))
            user = cursor.fetchone()
            if user:
                item['user_name'] = user['name']
                item['user_phone'] = user['phone']
            else:
                item['user_name'] = 'Unknown'
                item['user_phone'] = 'Unknown'

    except Exception as e:
        print(f"Error fetching game activity: {str(e)}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
    
    return render_template('admin_game_activity.html', 
                          activity=activity, 
                          game_type=game_type,
                          game_types=['all', 'Mines', 'Plinko', 'Slots', 'MegaSlots', 
                                     'LuckyWheel', 'Aviator', 'CoinFlip', 'OddEven', 'SuperSlot', 'TreasureHunt'])

@app.route('/admin/game-statistics')
def admin_game_statistics():
    """Admin route for viewing game statistics"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Fetch aggregate statistics for each game
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get total bets, wins, and house edge for each game
        game_stats = []
        
        # Example for one game (repeat for each game)
        cursor.execute("""
            SELECT 
                COUNT(*) as total_games,
                SUM(bet_amount) as total_bet_amount,
                SUM(CASE WHEN result = 'win' THEN winnings ELSE 0 END) as total_winnings,
                SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as total_wins
            FROM mines_game
        """)
        mines_stats = cursor.fetchone()
        if mines_stats and mines_stats['total_games'] > 0:
            total_bet = float(mines_stats['total_bet_amount'] or 0)
            total_win = float(mines_stats['total_winnings'] or 0)
            house_edge = ((total_bet - total_win) / total_bet * 100) if total_bet > 0 else 0
            win_rate = (mines_stats['total_wins'] / mines_stats['total_games'] * 100) if mines_stats['total_games'] > 0 else 0
            
            game_stats.append({
                'game_type': 'Mines',
                'total_games': mines_stats['total_games'],
                'total_bet_amount': total_bet,
                'total_winnings': total_win,
                'house_edge': house_edge,
                'win_rate': win_rate
            })
        
        # Add similar queries for other games
        
        conn.close()
    except Exception as e:
        print(f"Error fetching game statistics: {str(e)}")
        game_stats = []
    
    return render_template('admin_game_statistics.html', game_stats=game_stats)

@app.route('/admin/update-house-edge', methods=['POST'])
def admin_update_house_edge():
    """Admin route for updating house edge/multipliers for games"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Not authorized'})
    
    try:
        data = request.get_json()
        game_type = data.get('game_type')
        multiplier = float(data.get('multiplier', 1.0))
        
        # Example implementation to update game settings in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update or insert settings
        cursor.execute("""
            INSERT INTO game_settings (game_type, base_multiplier) 
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE base_multiplier = %s
        """, (game_type, multiplier, multiplier))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': f"{game_type} multiplier updated successfully"})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/update_user_wallet', methods=['POST'])
def update_user_wallet():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Not authorized'})
    
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        amount = float(data.get('amount', 0))
        action = data.get('action')
        note = data.get('note', '')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # First get current wallet balance
        cursor.execute("SELECT wallet_balance FROM user WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({'success': False, 'message': 'User not found'})
            
        current_balance = user['wallet_balance']
        new_balance = current_balance
        
        # Calculate new balance based on action
        if action == 'add':
            new_balance = current_balance + amount
        elif action == 'subtract':
            new_balance = current_balance - amount
            if new_balance < 0:
                new_balance = 0  # Don't allow negative balance
        elif action == 'set':
            new_balance = amount
            
        # Update the user's wallet balance
        cursor.execute("UPDATE user SET wallet_balance = %s WHERE id = %s", 
                      (new_balance, user_id))
        
        # Record the transaction
        try:
            transaction_type = 'admin_adjustment'
            transaction_status = 'completed'
            transaction_details = json.dumps({
                'action': action,
                'previous_balance': current_balance,
                'admin_note': note
            })
            
            cursor.execute("""
                INSERT INTO transactions 
                (user_id, amount, type, status, payment_method, transaction_details) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, amount, transaction_type, transaction_status, 'admin', transaction_details))
        except Exception as e:
            # If transactions table doesn't exist yet, just log the error
            print(f"Could not record transaction: {str(e)}")
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'Wallet updated successfully. New balance: ₹{new_balance:.2f}',
            'new_balance': new_balance
        })
        
    except Exception as e:
        print(f"Error updating wallet: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/aviator/active-bets', methods=['GET'])
@login_required
def aviator_active_bets():
    try:
        # Get all pending games in the current round
        games = AviatorHistory.query.filter_by(result='pending').all()
        
        active_bets = []
        for game in games:
            # Get user information
            user = User.query.get(game.user_id)
            if user:
                active_bets.append({
                    'username': user.name,
                    'amount': game.bet_amount,
                    'status': 'betting',
                    'bet_id': game.id
                })
        
        return jsonify({
            'success': True,
            'active_bets': active_bets
        })
    except Exception as e:
        print("Error in aviator_active_bets:", str(e))
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/admin/withdraw-requests')
def admin_withdraw_requests():
    """Admin route for viewing and managing withdrawal requests"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Fetch all pending withdrawals with user info
        cursor.execute("""
            SELECT t.*, u.name, u.phone
            FROM transactions t
            JOIN user u ON t.user_id = u.id
            WHERE t.type = 'withdrawal' AND t.status = 'pending'
            ORDER BY t.created_at DESC
        """)
        
        withdraw_requests = cursor.fetchall()
        
        # Get withdrawal statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_requests,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount
            FROM transactions
            WHERE type = 'withdrawal' AND status = 'pending'
        """)
        
        stats = cursor.fetchone()
        
    except mysql.connector.errors.ProgrammingError as e:
        # Table doesn't exist
        if e.errno == 1146:  # "Table doesn't exist" error code
            withdraw_requests = []
            stats = {'total_requests': 0, 'total_amount': 0, 'avg_amount': 0}
            flash("Transactions table not found. Please run the database migration script.", "danger")
        else:
            # Re-raise if it's a different error
            raise
    except Exception as e:
        withdraw_requests = []
        stats = {'total_requests': 0, 'total_amount': 0, 'avg_amount': 0}
        flash(f"Error fetching withdrawal requests: {str(e)}", "danger")
    
    conn.close()
    
    return render_template('admin_withdraw_requests.html', 
                           withdraw_requests=withdraw_requests,
                           stats=stats)

# Reject Withdrawal
@app.route('/reject_withdrawal/<int:transaction_id>')
def reject_withdrawal(transaction_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # First get the transaction details
        cursor.execute("SELECT * FROM transactions WHERE id = %s AND type = 'withdrawal'", 
                      (transaction_id,))
        transaction = cursor.fetchone()
        
        if not transaction:
            flash("Transaction not found or not a withdrawal", "danger")
            conn.close()
            return redirect(url_for('admin_withdraw_requests'))
        
        # Get the user to refund the amount
        cursor.execute("SELECT * FROM user WHERE id = %s", (transaction['user_id'],))
        user = cursor.fetchone()
        
        if not user:
            flash("User not found for this transaction", "danger")
            conn.close()
            return redirect(url_for('admin_withdraw_requests'))
            
        # Update transaction status
        cursor.execute("UPDATE transactions SET status = 'cancelled' WHERE id = %s", 
                      (transaction_id,))
        
        # Refund the amount to user's wallet
        new_balance = user['wallet_balance'] + transaction['amount']
        cursor.execute("UPDATE user SET wallet_balance = %s WHERE id = %s", 
                      (new_balance, user['id']))
        
        # Add a refund transaction record
        refund_details = json.dumps({
            'original_transaction_id': transaction_id,
            'admin_note': 'Withdrawal request rejected and amount refunded'
        })
        
        cursor.execute("""
            INSERT INTO transactions 
            (user_id, amount, type, status, payment_method, transaction_details) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user['id'], transaction['amount'], 'refund', 'completed', 'system', refund_details))
        
        conn.commit()
        flash(f"Withdrawal rejected and ₹{transaction['amount']} refunded to user's wallet", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error rejecting withdrawal: {str(e)}", "danger")
    
    conn.close()
    return redirect(url_for('admin_withdraw_requests'))

# SuperSlot Game Routes
@app.route('/superslot')
@login_required
def superslot_game():
    return render_template('superslot/superslot.html', balance=current_user.wallet_balance)

@app.route('/superslot/spin', methods=['POST'])
@login_required
def superslot_spin():
    data = request.get_json()
    bet_amount = float(data.get('bet_amount', 0))
    bet_level = int(data.get('bet_level', 1))
    is_free_spin = data.get('free_spin', False)
    current_multiplier = float(data.get('current_multiplier', 1.0))
    
    # Check if bet amount is valid
    if not is_free_spin and (bet_amount <= 0 or current_user.wallet_balance < bet_amount):
        return jsonify({'success': False, 'error': 'Invalid bet amount or insufficient balance'})
    
    # Get or create progressive multiplier for user
    progressive = SuperSlotMultiplier.query.filter_by(user_id=current_user.id).first()
    if not progressive:
        progressive = SuperSlotMultiplier(
            user_id=current_user.id,
            current_multiplier=1.0,
            consecutive_losses=0
        )
        db.session.add(progressive)
    
    # Deduct from wallet balance if not a free spin
    if not is_free_spin:
        current_user.wallet_balance -= bet_amount
        
        # Update jackpot with contribution - Fix to handle when jackpot doesn't exist
        jackpot = SuperSlotJackpot.query.first()
        if not jackpot:
            # Create a new jackpot with default values
            jackpot = SuperSlotJackpot(
                current_amount=20000.0,
                total_contributions=0.0,
                last_updated=datetime.utcnow()
            )
            db.session.add(jackpot)
            db.session.flush()  # This adds the jackpot to the database session but doesn't commit yet
        
        contribution = bet_amount * 0.01
        jackpot.current_amount += contribution
        jackpot.total_contributions += contribution
        jackpot.last_updated = datetime.utcnow()
    
    # Generate random symbols for the reels (5x3 grid = 15 symbols)
    symbols = ["🍒", "🍋", "🍇", "🔔", "7️⃣", "💎", "🎰", "🎯", "⭐"]
    result_symbols = []
    
    # More advanced random generation with weighted probabilities
    weights = [20, 18, 15, 12, 10, 8, 5, 3, 2]
    
    for _ in range(15):
        # Use weights to determine symbol probability
        total = sum(weights)
        r = random.random() * total
        cumulative = 0
        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                result_symbols.append(symbols[i])
                break
    
    # Calculate winnings
    rows = [result_symbols[0:5], result_symbols[5:10], result_symbols[10:15]]
    winnings = 0
    special_feature = None
    
    # Apply progressive multiplier to the current spin
    effective_multiplier = current_multiplier * progressive.current_multiplier
    
    # Check for winning combinations in each row
    for row in rows:
        # Count consecutive symbols from left
        for i in range(len(symbols)):
            symbol = symbols[i]
            count = 0
            for j in range(5):
                if j < len(row) and row[j] == symbol:
                    count += 1
                else:
                    break
            
            if count >= 3:
                # Apply multiplier based on symbol and count
                multiplier = get_superslot_multiplier(symbol * count)
                winnings += bet_amount * multiplier * effective_multiplier
    
    # Special feature: Free Spins (triggered by 3+ scatter symbols)
    scatter_count = sum(1 for s in result_symbols if s == "⭐")
    if scatter_count >= 3:
        special_feature = f"Free Spins Bonus! You've won {scatter_count * 3} free spins!"
    
    # Special feature: Mega multiplier (5 wilds in a row)
    wild_count_in_row = max([row.count("🎯") for row in rows])
    if wild_count_in_row >= 4:
        multiplier_boost = wild_count_in_row * 2
        special_feature = f"Mega Multiplier! {multiplier_boost}x on your next spin!"
    
    # Super Jackpot (extremely rare - all 🎰 symbols)
    if result_symbols.count("🎰") >= 10:
        # Check if jackpot exists
        jackpot = SuperSlotJackpot.query.first()
        if jackpot:
            special_feature = f"SUPER JACKPOT! You've won ₹{jackpot.current_amount:.2f}!"
            winnings += jackpot.current_amount
            
            # Record jackpot win
            jackpot.last_winner_id = current_user.id
            jackpot.last_win_amount = jackpot.current_amount
            jackpot.last_win_date = datetime.utcnow()
            
            # Create achievement record
            achievement = SuperSlotAchievement(
                user_id=current_user.id,
                achievement_type='jackpot',
                achievement_value=jackpot.current_amount
            )
            db.session.add(achievement)
            
            # Reset jackpot to base amount
            jackpot.current_amount = 20000.0
    
    # Update progressive multiplier based on win/loss
    if winnings > 0:
        # Win - reset progressive multiplier
        progressive.current_multiplier = 1.0
        progressive.consecutive_losses = 0
    else:
        # Loss - increase progressive multiplier
        progressive.consecutive_losses += 1
        # Increase multiplier by 0.1 for each consecutive loss, up to max of 3.0
        progressive.current_multiplier = min(1.0 + (progressive.consecutive_losses * 0.1), 3.0)
    
    progressive.last_updated = datetime.utcnow()
    
    # Create game record
    game = SuperSlotGame(
        user_id=current_user.id,
        bet_amount=bet_amount,
        symbols=','.join(result_symbols),
        multiplier=current_multiplier,
        special_feature=special_feature,
        winnings=winnings,
        bet_level=bet_level,
        free_spins_used=1 if is_free_spin else 0,
        progressive_multiplier=progressive.current_multiplier
    )
    db.session.add(game)
    
    # Update user balance with winnings
    current_user.wallet_balance += winnings
    
    # Check for achievement: Big win (10x bet or more)
    if winnings >= bet_amount * 10:
        achievement = SuperSlotAchievement(
            user_id=current_user.id,
            achievement_type='big_win',
            achievement_value=winnings,
            game_id=game.id
        )
        db.session.add(achievement)
    
    # Commit all changes to database
    db.session.commit()
    
    # Return result
    response = {
        'success': True,
        'symbols': result_symbols,
        'winnings': winnings,
        'new_balance': current_user.wallet_balance,
        'special_feature': special_feature,
        'progressive_multiplier': progressive.current_multiplier
    }
    
    return jsonify(response)

@app.route('/superslot/achievements')
@login_required
def superslot_achievements():
    # Get user's achievements
    achievements = SuperSlotAchievement.query.filter_by(user_id=current_user.id).order_by(SuperSlotAchievement.timestamp.desc()).all()
    
    # Get jackpot info
    jackpot = SuperSlotJackpot.query.first()
    if not jackpot:
        jackpot = SuperSlotJackpot()
        db.session.add(jackpot)
        db.session.commit()
    
    # Get user stats
    total_games = SuperSlotGame.query.filter_by(user_id=current_user.id).count()
    total_won = db.session.query(func.sum(SuperSlotGame.winnings)).filter_by(user_id=current_user.id).scalar() or 0
    total_bet = db.session.query(func.sum(SuperSlotGame.bet_amount)).filter_by(user_id=current_user.id).scalar() or 0
    biggest_win = db.session.query(func.max(SuperSlotGame.winnings)).filter_by(user_id=current_user.id).scalar() or 0
    
    # Get max progressive multiplier achieved
    max_progressive = db.session.query(func.max(SuperSlotGame.progressive_multiplier)).filter_by(user_id=current_user.id).scalar() or 1.0
    
    # Check if user has achieved a high progressive multiplier (2.0x or higher)
    if max_progressive >= 2.0:
        # Check if user already has this achievement
        existing_achievement = SuperSlotAchievement.query.filter_by(
            user_id=current_user.id,
            achievement_type='progressive_master'
        ).first()
        
        # Only create new achievement if user doesn't have one or achieved a higher multiplier
        if not existing_achievement or existing_achievement.achievement_value < max_progressive:
            if existing_achievement:
                # Update existing achievement
                existing_achievement.achievement_value = max_progressive
                existing_achievement.timestamp = datetime.utcnow()
                existing_achievement.is_claimed = False
            else:
                # Create new achievement
                new_achievement = SuperSlotAchievement(
                    user_id=current_user.id,
                    achievement_type='progressive_master',
                    achievement_value=max_progressive,
                    is_claimed=False
                )
                db.session.add(new_achievement)
            
            db.session.commit()
            
            # Refresh achievements list
            achievements = SuperSlotAchievement.query.filter_by(user_id=current_user.id).order_by(SuperSlotAchievement.timestamp.desc()).all()
    
    return render_template('superslot/achievements.html', 
                          achievements=achievements,
                          jackpot=jackpot,
                          total_games=total_games,
                          total_won=total_won,
                          total_bet=total_bet,
                          biggest_win=biggest_win,
                          max_progressive=max_progressive)

@app.route('/superslot/history')
@login_required
def superslot_history():
    try:
        # Get user's recent games
        games = SuperSlotGame.query.filter_by(
            user_id=current_user.id
        ).order_by(SuperSlotGame.timestamp.desc()).limit(20).all()
        
        return render_template('superslot/history.html', history=games)
    except Exception as e:
        print("Error in superslot_history:", str(e))
        flash("Error loading game history", "danger")
        return redirect(url_for('superslot_game'))

# Helper function for SuperSlot
def get_superslot_multiplier(symbols):
    """Calculate multiplier based on SuperSlot symbols combination"""
    multiplier = 0
    
    # Check for horizontal lines (assuming 5x3 grid)
    rows = [symbols[i:i+5] for i in range(0, len(symbols), 5)]
    
    # Check each row
    for row in rows:
        # Count consecutive symbols starting from left
        for symbol in set(row):
            if symbol == "🎯":  # Skip wild symbol check
                continue
                
            consecutive = 0
            for i in range(len(row)):
                if row[i] == symbol or row[i] == "🎯":  # Symbol or wild
                    consecutive += 1
                else:
                    break
            
            if consecutive >= 3:
                # Add multiplier based on symbol and consecutive count
                if symbol == "🎰":
                    multiplier += [0, 0, 0, 50, 100, 500][consecutive]
                elif symbol == "💎":
                    multiplier += [0, 0, 0, 25, 50, 200][consecutive]
                elif symbol == "7️⃣":
                    multiplier += [0, 0, 0, 10, 25, 100][consecutive]
                elif symbol == "🔔":
                    multiplier += [0, 0, 0, 5, 15, 50][consecutive]
                elif symbol == "🍇":
                    multiplier += [0, 0, 0, 3, 10, 25][consecutive]
                elif symbol == "🍋":
                    multiplier += [0, 0, 0, 2, 5, 15][consecutive]
                elif symbol == "🍒":
                    multiplier += [0, 0, 0, 1.5, 4, 10][consecutive]
                elif symbol == "⭐":
                    multiplier += [0, 0, 0, 5, 15, 50][consecutive]
    
    # Check for scattered stars (paying anywhere)
    star_count = symbols.count("⭐")
    if star_count >= 3:
        multiplier += [0, 0, 0, 5, 10, 50][min(star_count, 5)]
    
    return multiplier

@app.route('/superslot/claim-achievement', methods=['POST'])
@login_required
def claim_achievement():
    try:
        data = request.get_json()
        achievement_id = data.get('achievement_id')
        
        # Find the achievement
        achievement = SuperSlotAchievement.query.filter_by(id=achievement_id, user_id=current_user.id, is_claimed=False).first()
        
        if not achievement:
            return jsonify({'success': False, 'error': 'Achievement not found or already claimed'})
        
        # Calculate reward based on achievement type
        reward = 0
        if achievement.achievement_type == 'jackpot':
            # Jackpot achievements already gave their reward
            reward = 0
        elif achievement.achievement_type == 'big_win':
            # Bonus for big win - 5% of the win amount
            reward = achievement.achievement_value * 0.05
        elif achievement.achievement_type == 'free_spins_complete':
            # Fixed reward for completing free spins
            reward = 100
        else:
            # Default reward
            reward = 50
        
        # Add reward to user's balance
        if reward > 0:
            current_user.wallet_balance += reward
        
        # Mark achievement as claimed
        achievement.is_claimed = True
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'reward': reward,
            'new_balance': current_user.wallet_balance
        })
    
    except Exception as e:
        db.session.rollback()
        print("Error in claim_achievement:", str(e))
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/treasurehunt')
@login_required
def treasure_hunt_game():
    return render_template('treasurehunt/treasurehunt.html', balance=current_user.wallet_balance)

@app.route('/treasurehunt/start', methods=['POST'])
@login_required
def treasure_hunt_start():
    try:
        data = request.get_json()
        bet_amount = float(data.get('bet_amount', 0))
        grid_size = int(data.get('grid_size', 5))
        
        # Validate inputs
        if bet_amount <= 0:
            return jsonify({'success': False, 'error': 'Invalid bet amount'})
        
        if current_user.wallet_balance < bet_amount:
            return jsonify({'success': False, 'error': 'Insufficient balance'})
        
        if grid_size not in [4, 5, 6]:  # Available grid sizes
            return jsonify({'success': False, 'error': 'Invalid grid size'})
        
        # Deduct bet amount
        current_user.wallet_balance -= bet_amount
        
        # Generate treasure and trap positions
        total_cells = grid_size * grid_size
        
        # Number of treasures and traps based on grid size
        num_treasures = max(3, grid_size - 1)  # More treasures for larger grids
        num_traps = max(3, grid_size)  # More traps for larger grids
        
        # Generate random positions for treasures and traps (ensure no overlap)
        all_positions = list(range(total_cells))
        random.shuffle(all_positions)
        
        treasure_positions = all_positions[:num_treasures]
        trap_positions = all_positions[num_treasures:num_treasures + num_traps]
        
        # Create new game
        game = TreasureHuntGame(
            user_id=current_user.id,
            bet_amount=bet_amount,
            grid_size=grid_size,
            treasure_positions=treasure_positions,
            trap_positions=trap_positions,
            revealed_positions=[],
            multiplier=1.0,
            result='progress',  # Changed from 'in_progress' to 'progress' (shorter string)
            game_state='active'
        )
        
        db.session.add(game)
        db.session.commit()
        
        # Return game state (hide treasure and trap positions from client)
        return jsonify({
            'success': True,
            'game_id': game.id,
            'grid_size': grid_size,
            'total_treasures': num_treasures,
            'total_traps': num_traps,
            'new_balance': current_user.wallet_balance
        })
        
    except Exception as e:
        db.session.rollback()
        print("Error in treasure_hunt_start:", str(e))
        # Return a user-friendly error message
        return jsonify({
            'success': False, 
            'error': 'Game could not be started. Please try again later.'
        })

@app.route('/treasurehunt/reveal', methods=['POST'])
@login_required
def treasure_hunt_reveal():
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        position = int(data.get('position', 0))
        
        # Get the game
        game = TreasureHuntGame.query.get(game_id)
        
        # Validate game
        if not game or game.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Invalid game'})
        
        if game.game_state != 'active' or game.result != 'progress':
            return jsonify({'success': False, 'error': 'Game already completed'})
        
        # Check if position already revealed
        if position in game.revealed_positions:
            return jsonify({'success': False, 'error': 'Position already revealed'})
        
        # Check position validity
        total_cells = game.grid_size * game.grid_size
        if position < 0 or position >= total_cells:
            return jsonify({'success': False, 'error': 'Invalid position'})
        
        # Add position to revealed positions
        revealed = game.revealed_positions.copy()
        revealed.append(position)
        game.revealed_positions = revealed
        
        # Check if position contains treasure or trap
        cell_type = 'empty'
        if position in game.treasure_positions:
            cell_type = 'treasure'
            # Update multiplier (treasures increase multiplier)
            treasures_found = sum(1 for pos in revealed if pos in game.treasure_positions)
            # Exponential multiplier growth
            game.multiplier = 1.0 + (treasures_found * 0.5) ** 1.2
            
            # Check if all treasures found
            if treasures_found == len(game.treasure_positions):
                game.result = 'win'
                game.game_state = 'completed'
                game.winnings = game.bet_amount * game.multiplier
                current_user.wallet_balance += game.winnings
                
                # Add achievement for finding all treasures
                achievement = TreasureHuntAchievement(
                    user_id=current_user.id,
                    achievement_type='treasure_master',
                    achievement_value=len(game.treasure_positions),
                    game_id=game.id
                )
                db.session.add(achievement)
                
                # Add achievement for big win if applicable
                if game.multiplier >= 3.0:
                    achievement = TreasureHuntAchievement(
                        user_id=current_user.id,
                        achievement_type='big_win',
                        achievement_value=game.multiplier,
                        game_id=game.id
                    )
                    db.session.add(achievement)
        
        elif position in game.trap_positions:
            cell_type = 'trap'
            game.result = 'lose'
            game.game_state = 'completed'
            game.winnings = 0
            
            # If player revealed more than half of treasures before hitting trap,
            # give them a partial win
            treasures_found = sum(1 for pos in revealed if pos in game.treasure_positions)
            if treasures_found > len(game.treasure_positions) / 2:
                partial_winnings = game.bet_amount * (treasures_found / len(game.treasure_positions)) * 0.5
                game.winnings = partial_winnings
                current_user.wallet_balance += partial_winnings
        
        # Save game state
        db.session.commit()
        
        # Return updated game state
        return jsonify({
            'success': True,
            'cell_type': cell_type,
            'position': position,
            'multiplier': game.multiplier,
            'revealed_positions': game.revealed_positions,
            'result': game.result,
            'game_state': game.game_state,
            'winnings': game.winnings if game.winnings else 0,
            'new_balance': current_user.wallet_balance
        })
        
    except Exception as e:
        db.session.rollback()
        print("Error in treasure_hunt_reveal:", str(e))
        return jsonify({'success': False, 'error': 'An error occurred while revealing the cell. Please try again.'})

@app.route('/treasurehunt/cashout', methods=['POST'])
@login_required
def treasure_hunt_cashout():
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        
        # Get the game
        game = TreasureHuntGame.query.get(game_id)
        
        # Validate game
        if not game or game.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Invalid game'})
        
        if game.game_state != 'active' or game.result != 'progress':
            return jsonify({'success': False, 'error': 'Game already completed'})
        
        # Calculate winnings based on current multiplier
        winnings = game.bet_amount * game.multiplier
        
        # Update game state
        game.result = 'win'
        game.game_state = 'completed'
        game.winnings = winnings
        
        # Add winnings to user balance
        current_user.wallet_balance += winnings
        
        # Check for trap evader achievement (cashing out without hitting a trap)
        revealed_count = len(game.revealed_positions)
        treasures_found = sum(1 for pos in game.revealed_positions if pos in game.treasure_positions)
        
        # If player revealed > 50% of the grid without hitting a trap
        grid_size = game.grid_size * game.grid_size
        if revealed_count > grid_size * 0.5:
            achievement = TreasureHuntAchievement(
                user_id=current_user.id,
                achievement_type='trap_evader',
                achievement_value=revealed_count,
                game_id=game.id
            )
            db.session.add(achievement)
        
        # If player found at least 2 treasures
        if treasures_found >= 2:
            achievement = TreasureHuntAchievement(
                user_id=current_user.id,
                achievement_type='treasure_hunter',
                achievement_value=treasures_found,
                game_id=game.id
            )
            db.session.add(achievement)
        
        # Save game state
        db.session.commit()
        
        # Return updated game state
        return jsonify({
            'success': True,
            'winnings': winnings,
            'new_balance': current_user.wallet_balance
        })
        
    except Exception as e:
        db.session.rollback()
        print("Error in treasure_hunt_cashout:", str(e))
        return jsonify({'success': False, 'error': 'An error occurred while cashing out. Please try again.'})

@app.route('/treasurehunt/history')
@login_required
def treasure_hunt_history():
    # Get user's game history
    games = TreasureHuntGame.query.filter_by(user_id=current_user.id)\
        .order_by(TreasureHuntGame.timestamp.desc()).limit(50).all()
    
    return render_template('treasurehunt/history.html', games=games)

@app.route('/treasurehunt/achievements')
@login_required
def treasure_hunt_achievements():
    # Get user's achievements
    achievements = TreasureHuntAchievement.query.filter_by(user_id=current_user.id)\
        .order_by(TreasureHuntAchievement.timestamp.desc()).all()
    
    # Get user stats
    total_games = TreasureHuntGame.query.filter_by(user_id=current_user.id).count()
    total_won = db.session.query(func.sum(TreasureHuntGame.winnings))\
        .filter(TreasureHuntGame.user_id == current_user.id, TreasureHuntGame.result == 'win').scalar() or 0
    total_bet = db.session.query(func.sum(TreasureHuntGame.bet_amount))\
        .filter_by(user_id=current_user.id).scalar() or 0
    
    # Calculate treasure and trap stats
    games = TreasureHuntGame.query.filter_by(user_id=current_user.id).all()
    total_treasures_found = 0
    total_traps_hit = 0
    
    for game in games:
        treasures = set(game.treasure_positions)
        traps = set(game.trap_positions)
        revealed = set(game.revealed_positions)
        
        total_treasures_found += len(treasures.intersection(revealed))
        total_traps_hit += len(traps.intersection(revealed))
    
    return render_template('treasurehunt/achievements.html', 
                          achievements=achievements,
                          total_games=total_games,
                          total_won=total_won,
                          total_bet=total_bet,
                          total_treasures_found=total_treasures_found,
                          total_traps_hit=total_traps_hit)

@app.route('/treasurehunt/claim-achievement', methods=['POST'])
@login_required
def claim_treasure_achievement():
    try:
        data = request.get_json()
        achievement_id = data.get('achievement_id')
        
        # Find the achievement
        achievement = TreasureHuntAchievement.query.filter_by(
            id=achievement_id, user_id=current_user.id, is_claimed=False
        ).first()
        
        if not achievement:
            return jsonify({'success': False, 'error': 'Achievement not found or already claimed'})
        
        # Calculate reward based on achievement type
        reward = 0
        if achievement.achievement_type == 'treasure_master':
            # Reward based on number of treasures found
            reward = 50 * achievement.achievement_value
        elif achievement.achievement_type == 'trap_evader':
            # Reward for avoiding traps
            reward = 100
        elif achievement.achievement_type == 'big_win':
            # Bonus for big win - 5% of the multiplier as a flat bonus
            reward = 100 * achievement.achievement_value * 0.05
        elif achievement.achievement_type == 'treasure_hunter':
            # Reward for finding treasures
            reward = 25 * achievement.achievement_value
        
        # Add reward to user's balance
        if reward > 0:
            current_user.wallet_balance += reward
        
        # Mark achievement as claimed
        achievement.is_claimed = True
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'reward': reward,
            'new_balance': current_user.wallet_balance
        })
    
    except Exception as e:
        db.session.rollback()
        print("Error in claim_treasure_achievement:", str(e))
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/andarbahar')
@login_required
def andar_bahar_game():
    # Get user's last 10 games
    user_games = AndarBaharGame.query.filter_by(user_id=current_user.id).order_by(AndarBaharGame.timestamp.desc()).limit(10).all()
    
    # Calculate game statistics
    total_games = AndarBaharGame.query.filter_by(user_id=current_user.id).count()
    total_wins = AndarBaharGame.query.filter_by(user_id=current_user.id, result='win').count()
    win_percentage = round((total_wins / total_games) * 100, 1) if total_games > 0 else 0
    andar_wins = AndarBaharGame.query.filter_by(user_id=current_user.id, winning_side='andar').count()
    bahar_wins = AndarBaharGame.query.filter_by(user_id=current_user.id, winning_side='bahar').count()
    
    return render_template('andarbahar/andarbahar.html', 
                           balance=current_user.wallet_balance,
                           user_games=user_games,
                           total_games=total_games,
                           total_wins=total_wins,
                           win_percentage=win_percentage,
                           andar_wins=andar_wins,
                           bahar_wins=bahar_wins)

@app.route('/andarbahar/place-bet', methods=['POST'])
@login_required
def andarbahar_place_bet():
    try:
        data = request.get_json()
        bet_side = data.get('side')
        bet_amount = float(data.get('amount'))
        
        # Validate input
        if bet_side not in ['andar', 'bahar']:
            return jsonify({'status': 'error', 'error': 'Invalid bet side'})
        
        if bet_amount <= 0:
            return jsonify({'status': 'error', 'error': 'Bet amount must be positive'})
        
        if bet_amount > current_user.wallet_balance:
            return jsonify({'status': 'error', 'error': 'Insufficient balance'})
        
        # Deduct bet amount from balance
        current_user.wallet_balance -= bet_amount
        
        # Create deck of cards
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = [{'suit': suit, 'value': value} for suit in suits for value in values]
        
        # Shuffle the deck
        random.shuffle(deck)
        
        # Draw joker card
        joker_card = deck.pop(0)
        joker_card_str = f"{joker_card['value']} of {joker_card['suit']}"
        
        # Deal cards until a matching card is found
        cards = []
        matching_index = -1
        current_side = 'andar'  # Start with Andar
        
        for i, card in enumerate(deck):
            cards.append(card)
            
            # Check if this card matches the joker card value
            if card['value'] == joker_card['value']:
                matching_index = i
                winning_side = current_side
                winning_card = f"{card['value']} of {card['suit']}"
                break
            
            # Alternate between Andar and Bahar
            current_side = 'bahar' if current_side == 'andar' else 'andar'
        
        # Determine if user won
        result = 'win' if bet_side == winning_side else 'lose'
        
        # Calculate multiplier based on cards drawn
        # First 5 cards pay 1.9x, cards 6-10 pay 2x, cards 11-15 pay 2.1x, etc.
        multiplier = 1.9 + (min(math.floor((matching_index + 1) / 5), 5) * 0.1)
        
        # Calculate winnings
        winnings = bet_amount * multiplier if result == 'win' else 0
        
        # Add winnings to user balance if won
        if result == 'win':
            current_user.wallet_balance += winnings
        
        # Save the game result to the database
        game = AndarBaharGame(
            user_id=current_user.id,
            bet_amount=bet_amount,
            bet_side=bet_side,
            joker_card=joker_card_str,
            winning_side=winning_side,
            winning_card=winning_card,
            cards_drawn=matching_index + 1,
            result=result,
            multiplier=multiplier,
            winnings=winnings
        )
        db.session.add(game)
        
        # Check for achievements
        AndarBaharAchievement.check_and_create_achievements(current_user.id, game)
        
        db.session.commit()
        
        # Calculate game statistics for response
        total_games = AndarBaharGame.query.filter_by(user_id=current_user.id).count()
        total_wins = AndarBaharGame.query.filter_by(user_id=current_user.id, result='win').count()
        win_percentage = round((total_wins / total_games) * 100, 1) if total_games > 0 else 0
        andar_wins = AndarBaharGame.query.filter_by(user_id=current_user.id, winning_side='andar').count()
        bahar_wins = AndarBaharGame.query.filter_by(user_id=current_user.id, winning_side='bahar').count()
        
        return jsonify({
            'status': 'success',
            'joker_card_str': joker_card_str,
            'joker': joker_card,
            'cards': cards,
            'matching_index': matching_index,
            'winning_side': winning_side,
            'result': result,
            'multiplier': multiplier,
            'winnings': winnings,
            'new_balance': current_user.wallet_balance,
            'stats': {
                'total_games': total_games,
                'total_wins': total_wins,
                'win_percentage': win_percentage,
                'andar_wins': andar_wins,
                'bahar_wins': bahar_wins
            }
        })
        
    except Exception as e:
        # Roll back any changes if an error occurs
        db.session.rollback()
        current_user.wallet_balance += bet_amount  # Restore bet amount
        db.session.commit()
        
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/andarbahar/history')
@login_required
def andar_bahar_history():
    games = AndarBaharGame.query.filter_by(user_id=current_user.id).order_by(AndarBaharGame.timestamp.desc()).limit(50).all()
    return render_template('andarbahar/history.html', games=games)

@app.route('/andarbahar/achievements')
@login_required
def andar_bahar_achievements():
    # Get user's achievements
    achievements = AndarBaharAchievement.query.filter_by(user_id=current_user.id).order_by(AndarBaharAchievement.timestamp.desc()).all()
    
    # Calculate game statistics
    total_games = AndarBaharGame.query.filter_by(user_id=current_user.id).count()
    total_wins = AndarBaharGame.query.filter_by(user_id=current_user.id, result='win').count()
    win_percentage = round((total_wins / total_games) * 100, 1) if total_games > 0 else 0
    
    # Calculate total winnings
    total_winnings = db.session.query(func.sum(AndarBaharGame.winnings)).filter_by(user_id=current_user.id).scalar() or 0
    
    # Get highest bet amount
    highest_bet = db.session.query(func.max(AndarBaharGame.bet_amount)).filter_by(user_id=current_user.id).scalar() or 0
    
    # Calculate current win streak
    games = AndarBaharGame.query.filter_by(user_id=current_user.id).order_by(AndarBaharGame.timestamp.desc()).limit(10).all()
    current_streak = 0
    for game in games:
        if game.result == 'win':
            current_streak += 1
        else:
            break
    
    # Format achievements for display
    formatted_achievements = []
    for achievement in achievements:
        achievement_data = {
            'id': achievement.id,
            'type': achievement.achievement_type,
            'value': achievement.achievement_value,
            'is_claimed': achievement.is_claimed,
            'created_at': achievement.timestamp,
            'title': get_achievement_title(achievement.achievement_type),
            'description': get_achievement_description(achievement.achievement_type, achievement.achievement_value)
        }
        formatted_achievements.append(achievement_data)
    
    # Prepare stats for the template
    stats = {
        'total_games': total_games,
        'total_wins': total_wins,
        'win_ratio': win_percentage,
        'total_winnings': total_winnings,
        'highest_bet': highest_bet,
        'current_streak': current_streak
    }
    
    return render_template('andarbahar/achievements.html', 
                          achievements=formatted_achievements,
                          stats=stats)

@app.route('/andarbahar/claim-achievement', methods=['POST'])
@login_required
def claim_andar_bahar_achievement():
    try:
        data = request.get_json()
        achievement_id = data.get('achievement_id')
        
        # Find the achievement
        achievement = AndarBaharAchievement.query.filter_by(
            id=achievement_id, user_id=current_user.id, is_claimed=False
        ).first()
        
        if not achievement:
            return jsonify({'success': False, 'error': 'Achievement not found or already claimed'})
        
        # Calculate reward based on achievement type
        reward = 0
        if achievement.achievement_type == 'big_win':
            # Higher reward for bigger multiplier wins
            if achievement.achievement_value >= 20:
                reward = 500
            elif achievement.achievement_value >= 10:
                reward = 150
            else:
                reward = 50
        elif achievement.achievement_type == 'win_streak':
            # Reward based on streak length
            reward = min(achievement.achievement_value * 30, 1000)
        elif achievement.achievement_type == 'long_game_win':
            # Reward for winning with many cards drawn
            reward = min(achievement.achievement_value * 5, 500)
        elif achievement.achievement_type == 'consistent_player':
            # Reward for playing many games
            if achievement.achievement_value >= 1000:
                reward = 2000
            elif achievement.achievement_value >= 500:
                reward = 1000
            elif achievement.achievement_value >= 100:
                reward = 500
            elif achievement.achievement_value >= 50:
                reward = 200
            elif achievement.achievement_value >= 10:
                reward = 50
        
        # Add reward to user's balance
        if reward > 0:
            current_user.wallet_balance += reward
        
        # Mark achievement as claimed
        achievement.is_claimed = True
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'reward': reward,
            'new_balance': current_user.wallet_balance
        })
    
    except Exception as e:
        db.session.rollback()
        print("Error in claim_andar_bahar_achievement:", str(e))
        return jsonify({'success': False, 'error': 'An error occurred'})

# Helper functions for andar bahar achievements
def get_achievement_title(achievement_type):
    titles = {
        'big_win': 'Big Winner',
        'win_streak': 'Hot Streak',
        'long_game_win': 'Patience Pays',
        'consistent_player': 'Dedicated Player'
    }
    return titles.get(achievement_type, 'Achievement')

def get_achievement_description(achievement_type, value):
    if achievement_type == 'big_win':
        return f'Won {value}x your bet amount in a single game'
    elif achievement_type == 'win_streak':
        return f'Won {value} games in a row'
    elif achievement_type == 'long_game_win':
        return f'Won after {value} cards were drawn'
    elif achievement_type == 'consistent_player':
        return f'Played {value} Andar Bahar games'
    else:
        return 'Unlocked an achievement'

@app.route('/teenpatti')
@login_required
def teenpatti_game():
    # Get user's last 10 games
    games = TeenPattiGame.query.filter_by(user_id=current_user.id).order_by(TeenPattiGame.timestamp.desc()).limit(10).all()
    
    # Calculate stats
    total_games = TeenPattiGame.query.filter_by(user_id=current_user.id).count()
    total_wins = TeenPattiGame.query.filter_by(user_id=current_user.id, result='win').count()
    win_percentage = (total_wins / total_games * 100) if total_games > 0 else 0
    
    stats = {
        'total_games': total_games,
        'total_wins': total_wins,
        'win_percentage': round(win_percentage, 1)
    }
    
    return render_template('teenpatti/teenpatti.html', games=games, stats=stats)

@app.route('/teenpatti/play', methods=['POST'])
@login_required
def teenpatti_play():
    try:
        data = request.get_json()
        bet_amount = float(data.get('bet_amount', 0))
        game_type = data.get('game_type', 'classic')
        
        # Validate inputs
        if bet_amount <= 0:
            return jsonify({'success': False, 'error': 'Invalid bet amount'})
        
        if current_user.wallet_balance < bet_amount:
            return jsonify({'success': False, 'error': 'Insufficient balance'})
        
        if game_type not in ['classic', 'AK47', 'muflis']:
            return jsonify({'success': False, 'error': 'Invalid game type'})
        
        # Create a deck of cards
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        
        # Modify deck for different game types
        if game_type == 'AK47':
            # AK47 variation: Only A, K, 4, 7 cards
            ranks = ['4', '7', 'K', 'A']
        elif game_type == 'muflis':
            # Muflis variation: Cards from 2 to 10 only
            ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10']
        
        deck = [f"{rank}{suit}" for suit in suits for rank in ranks]
        random.shuffle(deck)
        
        # Deal cards
        player_cards = [deck.pop() for _ in range(3)]
        dealer_cards = [deck.pop() for _ in range(3)]
        
        # Evaluate hands
        player_rank = evaluate_teenpatti_hand(player_cards)
        dealer_rank = evaluate_teenpatti_hand(dealer_cards)
        
        # Determine winner
        winner = determine_teenpatti_winner(player_rank, dealer_rank, player_cards, dealer_cards)
        
        # Set multiplier based on hand rank
        multipliers = {
            'trail': 5.0,      # Three of a kind
            'pure_sequence': 4.5,  # Straight flush
            'sequence': 4.0,   # Straight
            'color': 3.5,      # Flush
            'pair': 3.0,       # Pair
            'high_card': 2.0   # High card
        }
        
        multiplier = multipliers.get(player_rank, 2.0)
        
        # Calculate result and winnings
        result = ''
        winnings = 0
        
        if winner == 'player':
            result = 'win'
            winnings = bet_amount * multiplier
            current_user.wallet_balance += winnings - bet_amount  # Subtract bet amount as it was already collected
        elif winner == 'dealer':
            result = 'lose'
            current_user.wallet_balance -= bet_amount
            winnings = 0
        else:  # Tie
            result = 'tie'
            # Return the bet amount in case of a tie
            winnings = bet_amount
        
        # Create game record
        game = TeenPattiGame(
            user_id=current_user.id,
            bet_amount=bet_amount,
            game_type=game_type,
            player_cards=json.dumps(player_cards),
            dealer_cards=json.dumps(dealer_cards),
            player_rank=player_rank,
            dealer_rank=dealer_rank,
            result=result,
            multiplier=multiplier,
            winnings=winnings
        )
        
        db.session.add(game)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'player_cards': player_cards,
            'dealer_cards': dealer_cards,
            'player_rank': player_rank,
            'dealer_rank': dealer_rank,
            'result': result,
            'winnings': winnings,
            'new_balance': current_user.wallet_balance
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/teenpatti/history')
@login_required
def teenpatti_history():
    # Get page parameter for pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get paginated games
    pagination = TeenPattiGame.query.filter_by(user_id=current_user.id)\
        .order_by(TeenPattiGame.timestamp.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    games = pagination.items
    
    # Calculate stats
    total_games = TeenPattiGame.query.filter_by(user_id=current_user.id).count()
    total_wins = TeenPattiGame.query.filter_by(user_id=current_user.id, result='win').count()
    win_rate = round((total_wins / total_games * 100) if total_games > 0 else 0, 1)
    
    # Calculate profit
    total_bet = db.session.query(func.sum(TeenPattiGame.bet_amount))\
        .filter_by(user_id=current_user.id).scalar() or 0
    total_winnings = db.session.query(func.sum(TeenPattiGame.winnings))\
        .filter_by(user_id=current_user.id).scalar() or 0
    profit = total_winnings - total_bet
    
    return render_template('teenpatti/history.html', 
                          games=games, 
                          page=page,
                          pages=pagination.pages,
                          total_games=total_games,
                          total_wins=total_wins,
                          win_rate=win_rate,
                          profit=profit)

# Helper functions for Teen Patti
def evaluate_teenpatti_hand(cards):
    # Extract ranks and suits
    ranks = [card[:-1] for card in cards]
    suits = [card[-1] for card in cards]
    
    # Convert face cards to numerical values for comparison
    rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 
                   'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    
    # Sort cards by rank
    sorted_ranks = sorted([rank_values.get(r, 0) for r in ranks])
    
    # Check for trail (three of a kind)
    if len(set(ranks)) == 1:
        return 'trail'
    
    # Check for pure sequence (straight flush)
    if (len(set(suits)) == 1 and 
        sorted_ranks[0] == sorted_ranks[1] - 1 and 
        sorted_ranks[1] == sorted_ranks[2] - 1):
        return 'pure_sequence'
    
    # Special case for A-2-3 straight
    if set(sorted_ranks) == {2, 3, 14}:
        if len(set(suits)) == 1:
            return 'pure_sequence'
        else:
            return 'sequence'
    
    # Check for sequence (straight)
    if (sorted_ranks[0] == sorted_ranks[1] - 1 and 
        sorted_ranks[1] == sorted_ranks[2] - 1):
        return 'sequence'
    
    # Check for color (flush)
    if len(set(suits)) == 1:
        return 'color'
    
    # Check for pair
    if len(set(ranks)) == 2:
        return 'pair'
    
    # High card
    return 'high_card'

def determine_teenpatti_winner(player_rank, dealer_rank, player_cards, dealer_cards):
    # Hand rankings from highest to lowest
    rankings = ['trail', 'pure_sequence', 'sequence', 'color', 'pair', 'high_card']
    
    # Compare hand ranks
    player_rank_value = rankings.index(player_rank)
    dealer_rank_value = rankings.index(dealer_rank)
    
    if player_rank_value < dealer_rank_value:
        return 'player'
    elif dealer_rank_value < player_rank_value:
        return 'dealer'
    else:
        # Same rank, compare high cards
        return compare_high_cards(player_rank, player_cards, dealer_cards)

def compare_high_cards(rank_type, player_cards, dealer_cards):
    # Extract ranks and convert to numerical values
    rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 
                   'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    
    player_ranks = [rank_values.get(card[:-1], 0) for card in player_cards]
    dealer_ranks = [rank_values.get(card[:-1], 0) for card in dealer_cards]
    
    # Sort ranks in descending order
    player_ranks.sort(reverse=True)
    dealer_ranks.sort(reverse=True)
    
    if rank_type == 'pair':
        # Find the pair value for each hand
        player_pair = find_pair_value(player_ranks)
        dealer_pair = find_pair_value(dealer_ranks)
        
        if player_pair > dealer_pair:
            return 'player'
        elif dealer_pair > player_pair:
            return 'dealer'
        else:
            # Compare the kicker (remaining card)
            player_kicker = [r for r in player_ranks if r != player_pair][0]
            dealer_kicker = [r for r in dealer_ranks if r != dealer_pair][0]
            
            if player_kicker > dealer_kicker:
                return 'player'
            elif dealer_kicker > player_kicker:
                return 'dealer'
            else:
                return 'tie'
    else:
        # For other rank types, just compare cards from highest to lowest
        for p, d in zip(player_ranks, dealer_ranks):
            if p > d:
                return 'player'
            elif d > p:
                return 'dealer'
        
        # All cards equal
        return 'tie'

def find_pair_value(ranks):
    # Find the value of the pair in a hand
    for r in ranks:
        if ranks.count(r) == 2:
            return r
    return 0

@app.route('/colorprediction')
def colorprediction():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    # Get last 10 games
    last_games = ColorPredictionGame.query.filter_by(user_id=current_user.id).order_by(ColorPredictionGame.timestamp.desc()).limit(10).all()
    
    # Calculate stats
    total_games = ColorPredictionGame.query.filter_by(user_id=current_user.id).count()
    wins = ColorPredictionGame.query.filter_by(user_id=current_user.id, result='win').count()
    win_percentage = (wins / total_games * 100) if total_games > 0 else 0
    
    return render_template('colorprediction/colorprediction.html', last_games=last_games, 
                          total_games=total_games, wins=wins, win_percentage=win_percentage)

@app.route('/colorprediction/play', methods=['POST'])
def colorprediction_play():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Please log in'}), 401
    
    try:
        data = request.get_json()
        bet_amount = float(data.get('bet_amount', 0))
        selected_color = data.get('selected_color', '')
        
        # Validate inputs
        if bet_amount <= 0:
            return jsonify({'success': False, 'message': 'Invalid bet amount'}), 400
        
        if selected_color not in ['red', 'green', 'blue', 'yellow', 'orange', 'purple']:
            return jsonify({'success': False, 'message': 'Invalid color selection'}), 400
        
        # Check if user has enough balance
        if current_user.wallet_balance < bet_amount:
            return jsonify({'success': False, 'message': 'Insufficient balance'}), 400
        
        # Determine the winning color
        colors = ['red', 'green', 'blue', 'yellow', 'orange', 'purple']
        result_color = random.choice(colors)
        
        # Determine multiplier based on color
        # Standard multiplier is 2x
        multiplier = 2.0
        
        # Check if player won
        if selected_color == result_color:
            result = 'win'
            winnings = bet_amount * multiplier
            new_balance = current_user.wallet_balance - bet_amount + winnings
        else:
            result = 'loss'
            winnings = 0
            new_balance = current_user.wallet_balance - bet_amount
        
        # Update user balance
        current_user.wallet_balance = new_balance
        
        # Create game record
        game = ColorPredictionGame(
            user_id=current_user.id,
            bet_amount=bet_amount,
            selected_color=selected_color,
            result_color=result_color,
            multiplier=multiplier,
            winnings=winnings,
            result=result
        )
        
        db.session.add(game)
        db.session.commit()
        
        # Return result to client
        return jsonify({
            'success': True,
            'result': result,
            'result_color': result_color,
            'winnings': winnings,
            'new_balance': new_balance
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/colorprediction/history')
@login_required
def colorprediction_history():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get paginated game history
    pagination = ColorPredictionGame.query.filter_by(user_id=current_user.id)\
        .order_by(ColorPredictionGame.timestamp.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    games = pagination.items
    
    # Calculate stats
    total_games = ColorPredictionGame.query.filter_by(user_id=current_user.id).count()
    total_wins = ColorPredictionGame.query.filter_by(user_id=current_user.id, result='win').count()
    win_rate = round((total_wins / total_games * 100) if total_games > 0 else 0, 2)
    
    # Calculate total profit
    profit_query = db.session.query(db.func.sum(ColorPredictionGame.winnings))\
        .filter_by(user_id=current_user.id)
    profit = profit_query.scalar() or 0
    
    return render_template('colorprediction/history.html', 
                          games=games,
                          page=page,
                          pages=pagination.pages,
                          total_games=total_games,
                          total_wins=total_wins,
                          win_rate=win_rate,
                          profit=profit)

@app.route('/cricket-t20')
@login_required
def cricket_t20():
    return render_template('cricket_t20.html', user=current_user)

@app.route('/cricket-t20/place-bet', methods=['POST'])
@login_required
def cricket_t20_place_bet():
    try:
        data = request.get_json()
        
        match_name = data.get('match_name')
        team_a = data.get('team_a')
        team_b = data.get('team_b')
        selected_team = data.get('selected_team')
        bet_amount = float(data.get('bet_amount', 0))
        odds = float(data.get('odds', 1.8))
        
        # Validate the inputs
        if not match_name or not team_a or not team_b or not selected_team or bet_amount <= 0:
            return jsonify({'success': False, 'error': 'Missing or invalid parameters'})
            
        # Check if user has sufficient balance
        if current_user.wallet_balance < bet_amount:
            return jsonify({'success': False, 'error': f'Insufficient balance. You have ₹{current_user.wallet_balance:.2f}'})
        
        # Validate selected team is either team_a or team_b
        if selected_team not in [team_a, team_b]:
            return jsonify({'success': False, 'error': 'Selected team must be one of the playing teams'})
        
        # Deduct bet amount from user balance
        current_user.wallet_balance -= bet_amount
        
        # Create new bet
        bet = CricketT20Bet(
            user_id=current_user.id,
            match_name=match_name,
            team_a=team_a,
            team_b=team_b,
            selected_team=selected_team,
            bet_amount=bet_amount,
            odds=odds,
            result='pending'
        )
        
        db.session.add(bet)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Bet placed successfully on {selected_team}',
            'new_balance': current_user.wallet_balance
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error in cricket_t20_place_bet: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred while placing your bet'})

@app.route('/cricket-t20/history')
@login_required
def cricket_t20_history():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        # Get user's cricket T20 betting history with pagination
        pagination = CricketT20Bet.query.filter_by(user_id=current_user.id)\
            .order_by(CricketT20Bet.timestamp.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        bets = pagination.items
        
        # Calculate total bets, wins, and profit
        total_bets = CricketT20Bet.query.filter_by(user_id=current_user.id).count()
        total_wins = CricketT20Bet.query.filter_by(user_id=current_user.id, result='win').count()
        win_rate = (total_wins / total_bets * 100) if total_bets > 0 else 0
        
        total_profit = db.session.query(func.sum(CricketT20Bet.winnings))\
            .filter(CricketT20Bet.user_id == current_user.id)\
            .scalar() or 0
            
        # Subtract total bet amounts to get actual profit
        total_bet_amount = db.session.query(func.sum(CricketT20Bet.bet_amount))\
            .filter(CricketT20Bet.user_id == current_user.id)\
            .scalar() or 0
        
        actual_profit = total_profit - total_bet_amount
        
        return render_template(
            'cricket_t20_history.html',
            bets=bets,
            pagination=pagination,
            total_bets=total_bets,
            total_wins=total_wins,
            win_rate=win_rate,
            profit=actual_profit,
            user=current_user
        )
    
    except Exception as e:
        print(f"Error in cricket_t20_history: {str(e)}")
        flash('An error occurred while fetching your history', 'danger')
        return redirect(url_for('cricket_t20'))

@app.route('/cricket-t20/settle-bet/<int:bet_id>', methods=['POST'])
@login_required
def cricket_t20_settle_bet(bet_id):
    try:
        # This would typically be an admin function, but we're making it available for demo purposes
        data = request.get_json()
        result = data.get('result')  # 'win' or 'lose'
        
        if result not in ['win', 'lose']:
            return jsonify({'success': False, 'error': 'Invalid result'})
        
        bet = CricketT20Bet.query.get(bet_id)
        
        if not bet or bet.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Bet not found'})
        
        if bet.result != 'pending':
            return jsonify({'success': False, 'error': 'Bet has already been settled'})
        
        bet.result = result
        
        if result == 'win':
            winnings = bet.bet_amount * bet.odds
            bet.winnings = winnings
            current_user.wallet_balance += winnings
        else:
            bet.winnings = 0
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Bet settled as {result}',
            'new_balance': current_user.wallet_balance
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error in cricket_t20_settle_bet: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred while settling the bet'})

@app.route('/roulette')
@login_required
def roulette_game():
    return render_template('roulette/roulette.html', user=current_user)

@app.route('/roulette/spin', methods=['POST'])
@login_required
def roulette_spin():
    data = request.get_json()
    
    bet_type = data.get('bet_type')
    bet_value = data.get('bet_value')
    bet_amount = float(data.get('bet_amount', 10))
    
    # Check wallet balance
    if current_user.wallet < bet_amount:
        return jsonify({'success': False, 'message': 'Insufficient balance'}), 400
    
    # Deduct bet amount from wallet
    current_user.wallet -= bet_amount
    
    # Spin the wheel (European Roulette: 0-36)
    result_number = random.randint(0, 36)
    
    # Determine color
    green_numbers = [0]
    red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    result_color = 'green' if result_number in green_numbers else 'red' if result_number in red_numbers else 'black'
    
    # Define multipliers and determine win
    multipliers = {'number': 36, 'color': 2, 'even_odd': 2, 'low_high': 2, 'dozen': 3, 'column': 3}
    is_win = False
    multiplier = 0
    
    # Check win conditions based on bet type
    if bet_type == 'number' and str(result_number) == bet_value:
        is_win = True
        multiplier = multipliers['number']
    elif bet_type == 'color' and result_color == bet_value:
        is_win = True
        multiplier = multipliers['color']
    elif bet_type == 'even_odd':
        if (bet_value == 'even' and result_number % 2 == 0 and result_number != 0) or \
           (bet_value == 'odd' and result_number % 2 == 1):
            is_win = True
            multiplier = multipliers['even_odd']
    elif bet_type == 'low_high':
        if (bet_value == 'low' and 1 <= result_number <= 18) or \
           (bet_value == 'high' and 19 <= result_number <= 36):
            is_win = True
            multiplier = multipliers['low_high']
    
    # Calculate winnings and update wallet
    winnings = bet_amount * multiplier if is_win else 0
    if is_win:
        current_user.wallet += winnings
    
    # Save game to database
    game = RouletteGame(
        user_id=current_user.id,
        bet_amount=bet_amount,
        bet_type=bet_type,
        bet_value=bet_value,
        result_number=result_number,
        result_color=result_color,
        is_win=is_win,
        multiplier=multiplier,
        winnings=winnings
    )
    db.session.add(game)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'result_number': result_number,
        'result_color': result_color,
        'is_win': is_win,
        'winnings': winnings,
        'wallet_balance': current_user.wallet
    })

@app.route('/api/colorprediction/bet-history')
@login_required
def api_colorprediction_bet_history():
    try:
        # Get user's recent bets
        history = ColorPredictionGame.query.filter_by(
            user_id=current_user.id
        ).order_by(ColorPredictionGame.timestamp.desc()).limit(10).all()
        
        history_data = []
        for bet in history:
            history_data.append({
                'type': 'color',  # Simplified for demonstration
                'value': bet.selected_color,
                'amount': float(bet.bet_amount),
                'result': 'win' if bet.result == 'win' else 'lose',
                'winnings': float(bet.winnings),
                'timestamp': bet.timestamp.isoformat()
            })
        
        return jsonify({
            'success': True,
            'history': history_data
        })
    except Exception as e:
        print(f"Error in api_colorprediction_bet_history: {str(e)}")
        return jsonify({'success': False, 'error': 'Error fetching bet history'})

@app.route('/api/colorprediction/place-bet', methods=['POST'])
@login_required
def api_colorprediction_place_bet():
    try:
        data = request.get_json()
        bet_amount = float(data.get('betAmount', 0))
        bet_type = data.get('betType', '')
        selected_bet = data.get('selectedBet', '')
        
        # Validate inputs
        if bet_amount <= 0:
            return jsonify({'success': False, 'message': 'Invalid bet amount'})
        
        if bet_type not in ['color', 'number', 'odd-even']:
            return jsonify({'success': False, 'message': 'Invalid bet type'})
        
        # Validate selected bet based on type
        if bet_type == 'color' and selected_bet not in ['red', 'green', 'blue']:
            return jsonify({'success': False, 'message': 'Invalid color selection'})
        elif bet_type == 'number' and not (0 <= int(selected_bet) <= 9):
            return jsonify({'success': False, 'message': 'Invalid number selection'})
        elif bet_type == 'odd-even' and selected_bet not in ['odd', 'even']:
            return jsonify({'success': False, 'message': 'Invalid odd/even selection'})
        
        # Check if user has enough balance
        if current_user.wallet_balance < bet_amount:
            return jsonify({'success': False, 'message': 'Insufficient balance'})
        
        # Process the bet (just record it, actual result determined later)
        # In a real implementation, you might use WebSockets for real-time updates
        
        return jsonify({
            'success': True,
            'message': 'Bet placed successfully',
            'bet_id': 12345  # Placeholder ID
        })
    except Exception as e:
        print(f"Error in api_colorprediction_place_bet: {str(e)}")
        return jsonify({'success': False, 'message': 'Error placing bet'})

@app.route('/api/colorprediction/get-result')
@login_required
def api_colorprediction_get_result():
    try:
        # In a real implementation, this would get the latest game result from the server
        # For demo purposes, generate a random result
        result_types = ['color', 'number', 'odd-even']
        result_type = random.choice(result_types)
        
        if result_type == 'color':
            colors = ['red', 'green', 'blue']
            result_value = random.choice(colors)
        elif result_type == 'number':
            result_value = str(random.randint(0, 9))
        else:  # odd-even
            result_value = 'odd' if random.randint(0, 9) % 2 == 1 else 'even'
        
        return jsonify({
            'success': True,
            'result': {
                'type': result_type,
                'value': result_value
            }
        })
    except Exception as e:
        print(f"Error in api_colorprediction_get_result: {str(e)}")
        return jsonify({'success': False, 'error': 'Error getting game result'})

@app.route('/api/colorprediction/history')
@login_required
def api_colorprediction_history():
    try:
        # In a real implementation, this would get the game history from the database
        # For demo purposes, generate 10 random results
        history = []
        result_types = ['color', 'number', 'odd-even']
        colors = ['red', 'green', 'blue']
        
        for _ in range(10):
            result_type = random.choice(result_types)
            
            if result_type == 'color':
                result_value = random.choice(colors)
            elif result_type == 'number':
                result_value = str(random.randint(0, 9))
            else:  # odd-even
                result_value = 'odd' if random.randint(0, 9) % 2 == 1 else 'even'
            
            history.append({
                'type': result_type,
                'value': result_value
            })
        
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        print(f"Error in api_colorprediction_history: {str(e)}")
        return jsonify({'success': False, 'error': 'Error fetching game history'})

if __name__ == '__main__':
    # Add a migration script to handle the new progressive_multiplier column
    with app.app_context():
        try:
            # Check if the column already exists
            db.session.execute(db.text("SELECT progressive_multiplier FROM super_slot_game LIMIT 1"))
            print("Column progressive_multiplier already exists")
        except Exception as e:
            print("Adding progressive_multiplier column to super_slot_game table")
            try:
                # Add the column
                db.session.execute(db.text("ALTER TABLE super_slot_game ADD COLUMN progressive_multiplier FLOAT NULL"))
                db.session.commit()
                print("Column added successfully")
            except Exception as e:
                print(f"Error adding column: {str(e)}")
                db.session.rollback()
        
        try:
            # Check if SuperSlotMultiplier table exists
            db.session.execute(db.text("SELECT * FROM super_slot_multiplier LIMIT 1"))
            print("Table super_slot_multiplier already exists")
        except Exception as e:
            print("Creating super_slot_multiplier table")
            db.create_all()
            db.session.commit()
            print("Table created successfully")
    
    app.run(debug=True)