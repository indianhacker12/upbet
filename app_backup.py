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
from models import db, User, GameResult, OddEvenGameResult, ColorGameResult, GameHistory, MineBettingHistory, AviatorHistory, PlinkoHistory, MinesGame, PlinkoGame, SlotGame, CricketMatch, CricketMatchBet, CricketEvent, CricketEventOption, CricketEventBet, AviterHistory

# Secret key
razorpay_client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET))
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:ZzxLIsWgwxxLhUUiVCaAAIfHPsInegqs@shuttle.proxy.rlwy.net:43495/railway'  # MySQL database connection
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

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
        elif action == 'withdraw' and amount <= current_user.wallet_balance:
            current_user.wallet_balance -= amount
            db.session.commit()
            flash('Withdrawal successful!', 'success')
        else:
            flash('Insufficient balance or invalid action!', 'danger')
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
    if not payment_id:
        flash("Payment ID not found!", 'danger')
        return redirect(url_for('wallet'))
    
    amount = float(request.form.get('amount', 0))
    
    # If this is first recharge, unlock referral bonus
    if not current_user.has_recharged and current_user.referral_bonus > 0:
        current_user.wallet_balance += current_user.referral_bonus
        current_user.has_recharged = True
        flash(f'Congratulations! Your referral bonus of ₹{current_user.referral_bonus} has been unlocked!', 'success')
    
    current_user.wallet_balance += amount
    db.session.commit()
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
    
    return render_template('account.html',
                         current_user=current_user,
                         total_games=total_games,
                         total_winnings=total_winnings,
                         recent_activities=recent_activities,
                         account_created=current_user.date_created.strftime('%d %b %Y'),
                         last_login=current_user.last_login.strftime('%d %b %Y %H:%M') if current_user.last_login else 'Never')

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

    cursor.execute("SELECT COUNT(*) AS pending_withdrawals FROM transactions WHERE type='withdrawal' AND status='pending'")
    pending_withdrawals = cursor.fetchone()['pending_withdrawals']

    conn.close()

    return render_template('admin_dashboard.html', total_users=total_users, total_bets=total_bets, pending_withdrawals=pending_withdrawals)

# Manage Users
@app.route('/manage_users')
def manage_user():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    conn.close()

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

@app.route('/keno/play', methods=['POST'])
@login_required
def keno_play():
    try:
        data = request.get_json()
        bet_amount = float(data.get('bet_amount', 0))
        selected_numbers = data.get('selected_numbers', [])
        
        # Validate inputs with specific error messages
        if bet_amount <= 0:
            return jsonify({'success': False, 'error': 'Please enter a valid bet amount greater than 0'})
        
        if current_user.wallet_balance < bet_amount:
            return jsonify({'success': False, 'error': f'Insufficient balance. You have ₹{current_user.wallet_balance} available.'})
        
        # Validate selected numbers
        if not selected_numbers:
            return jsonify({'success': False, 'error': 'Please select at least one number to play'})
            
        if len(selected_numbers) > 10:
            return jsonify({'success': False, 'error': 'You can select maximum 10 numbers'})
        
        # Convert string numbers to integers if needed
        try:
            selected_numbers = [int(num) for num in selected_numbers]
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Invalid number selection format'})
        
        # Check if all selected numbers are within range 1-80
        invalid_nums = [num for num in selected_numbers if num < 1 or num > 80]
        if invalid_nums:
            return jsonify({'success': False, 'error': f'Invalid number(s): {", ".join(map(str, invalid_nums))}. Numbers must be between 1 and 80.'})
        
        # Check for duplicate numbers
        if len(selected_numbers) != len(set(selected_numbers)):
            return jsonify({'success': False, 'error': 'Please avoid selecting duplicate numbers'})
        
        # Generate 20 random numbers for the draw
        drawn_numbers = random.sample(range(1, 81), 20)
        
        # Count matches
        matches = len(set(selected_numbers) & set(drawn_numbers))
        
        # Calculate multiplier based on number of matches and selections
        try:
            multiplier = get_keno_multiplier(len(selected_numbers), matches)
        except KeyError:
            return jsonify({'success': False, 'error': 'Error calculating multiplier. Please try again.'})
        
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

            return jsonify({
                'success': True,
                'drawn_numbers': drawn_numbers,
                'matches': matches,
                'multiplier': multiplier,
                'winnings': winnings,
                'new_balance': current_user.wallet_balance
            })
        except Exception as db_error:
            db.session.rollback()
            print(f"Database error in keno_play: {str(db_error)}")
            # Still give the user their result but note the history error
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
            
    except ValueError as ve:
        db.session.rollback()
        print(f"Value error in keno_play: {str(ve)}")
        return jsonify({'success': False, 'error': 'Please enter valid number values'})
    except Exception as e:
        db.session.rollback()
        error_message = str(e)
        print(f"Error in keno_play: {error_message}")
        
        # Provide more helpful error messages based on exception type
        if "JSON" in error_message:
            return jsonify({'success': False, 'error': 'Invalid request format'})
        elif "NoneType" in error_message:
            return jsonify({'success': False, 'error': 'Missing required information'})
        else:
            return jsonify({'success': False, 'error': 'An error occurred. Please try again.'})

@app.route('/keno/history')
@login_required
def keno_history():
    try:
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
    except Exception as e:
        print(f"Error in keno_history: {str(e)}")
        return jsonify({'success': False, 'error': 'Error loading game history. Please try again later.'})

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
        with db.engine.connect() as conn:
            # Check and add date_created column
            result = conn.execute(db.text("SHOW COLUMNS FROM user LIKE 'date_created'"))
            has_date_created = result.fetchone() is not None
            if not has_date_created:
                print("Adding date_created column")
                conn.execute(db.text("ALTER TABLE user ADD COLUMN date_created DATETIME DEFAULT CURRENT_TIMESTAMP"))
            
            # Check and add last_login column
            result = conn.execute(db.text("SHOW COLUMNS FROM user LIKE 'last_login'"))
            has_last_login = result.fetchone() is not None
            if not has_last_login:
                print("Adding last_login column")
                conn.execute(db.text("ALTER TABLE user ADD COLUMN last_login DATETIME"))
            
            # Check and add referrer_id column
            result = conn.execute(db.text("SHOW COLUMNS FROM user LIKE 'referrer_id'"))
            has_referrer = result.fetchone() is not None
            if not has_referrer:
                print("Adding referrer_id column")
                conn.execute(db.text("ALTER TABLE user ADD COLUMN referrer_id INT"))
                conn.execute(db.text("ALTER TABLE user ADD FOREIGN KEY (referrer_id) REFERENCES user(id)"))
            
            # Check and add referral_bonus column
            result = conn.execute(db.text("SHOW COLUMNS FROM user LIKE 'referral_bonus'"))
            has_referral_bonus = result.fetchone() is not None
            if not has_referral_bonus:
                print("Adding referral_bonus column")
                conn.execute(db.text("ALTER TABLE user ADD COLUMN referral_bonus FLOAT DEFAULT 0.0"))
            
            # Check and add has_recharged column
            result = conn.execute(db.text("SHOW COLUMNS FROM user LIKE 'has_recharged'"))
            has_recharged = result.fetchone() is not None
            if not has_recharged:
                print("Adding has_recharged column")
                conn.execute(db.text("ALTER TABLE user ADD COLUMN has_recharged BOOLEAN DEFAULT FALSE"))
                
            # Create advanced color prediction game table if not exists
            result = conn.execute(db.text("SHOW TABLES LIKE 'advanced_color_prediction_game'"))
            if not result.fetchone():
                print("Creating advanced_color_prediction_game table")
                conn.execute(db.text("""
                    CREATE TABLE advanced_color_prediction_game (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        game_type VARCHAR(20),
                        start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                        end_time DATETIME,
                        result VARCHAR(20),
                        status VARCHAR(20) DEFAULT 'waiting'
                    )
                """))
                
            # Create slot_game table if not exists
            result = conn.execute(db.text("SHOW TABLES LIKE 'slot_game'"))
            if not result.fetchone():
                print("Creating slot_game table")
                conn.execute(db.text("""
                    CREATE TABLE slot_game (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        bet_amount FLOAT,
                        symbols VARCHAR(50),
                        multiplier FLOAT,
                        winnings FLOAT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user(id)
                    )
                """))
                
            # Create plinko game table if not exists
            result = conn.execute(db.text("SHOW TABLES LIKE 'plinko_game'"))
            if not result.fetchone():
                print("Creating plinko_game table")
                conn.execute(db.text("""
                    CREATE TABLE plinko_game (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        bet_amount FLOAT,
                        risk_level VARCHAR(10),
                        rows INT,
                        path VARCHAR(100),
                        landing_position INT,
                        multiplier FLOAT,
                        winnings FLOAT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user(id)
                    )
                """))
            
            # Check and add landing_position column to plinko_game table if it exists but doesn't have the column
            result = conn.execute(db.text("SHOW TABLES LIKE 'plinko_game'"))
            if result.fetchone():
                result = conn.execute(db.text("SHOW COLUMNS FROM plinko_game LIKE 'landing_position'"))
                has_landing_position = result.fetchone() is not None
                if not has_landing_position:
                    print("Adding landing_position column to plinko_game table")
                    conn.execute(db.text("ALTER TABLE plinko_game ADD COLUMN landing_position INT AFTER path"))
            
            # Create megaslot_game table if not exists
            result = conn.execute(db.text("SHOW TABLES LIKE 'mega_slot_game'"))
            if not result.fetchone():
                print("Creating mega_slot_game table")
                conn.execute(db.text("""
                    CREATE TABLE mega_slot_game (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        bet_amount FLOAT,
                        symbols VARCHAR(100),
                        multiplier FLOAT,
                        winnings FLOAT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user(id)
                    )
                """))
                
            # Create lucky_wheel_slot table if not exists
            result = conn.execute(db.text("SHOW TABLES LIKE 'lucky_wheel_slot'"))
            if not result.fetchone():
                print("Creating lucky_wheel_slot table")
                conn.execute(db.text("""
                    CREATE TABLE lucky_wheel_slot (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        bet_amount FLOAT,
                        wheel_position INT,
                        symbol VARCHAR(20),
                        multiplier FLOAT,
                        winnings FLOAT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user(id)
                    )
                """))
    except Exception as e:
        print(f"Migration error: {e}")
        
# Call migration after db.create_all()
with app.app_context():
    db.create_all()
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
            'bet_id': game.id
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
            'winnings': winnings
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
                'result': game.result,
                'multiplier': game.multiplier,
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

# Cricket Betting Game Routes
import requests
from datetime import datetime, timedelta

# Cricket API Configuration
CRICKET_API_KEY = "e614c53f-e9fa-4d21-9e53-0d62069380a6"
CRICKET_API_BASE_URL = "https://api.cricapi.com/v1"

def fetch_cricket_matches():
    """Fetch upcoming and live cricket matches from the API"""
    try:
        endpoint = f"{CRICKET_API_BASE_URL}/matches"
        params = {
            "apikey": CRICKET_API_KEY,
            "offset": 0
        }
        response = requests.get(endpoint, params=params)
        data = response.json()
        
        if data.get("status") != "success":
            print(f"API Error: {data.get('message', 'Unknown error')}")
            return []
            
        matches = data.get("data", [])
        return matches
    except Exception as e:
        print(f"Error fetching cricket matches: {str(e)}")
        return []

def fetch_match_details(match_id):
    """Fetch detailed information about a specific match"""
    try:
        endpoint = f"{CRICKET_API_BASE_URL}/match_info"
        params = {
            "apikey": CRICKET_API_KEY,
            "id": match_id
        }
        response = requests.get(endpoint, params=params)
        data = response.json()
        
        if data.get("status") != "success":
            print(f"API Error: {data.get('message', 'Unknown error')}")
            return None
            
        return data.get("data")
    except Exception as e:
        print(f"Error fetching match details: {str(e)}")
        return None

def update_match_database():
    """Update the database with the latest matches"""
    try:
        matches = fetch_cricket_matches()
        
        for match_data in matches:
            match_id = match_data.get("id")
            
            # Check if match already exists in database
            existing_match = CricketMatch.query.filter_by(match_id=match_id).first()
            
            if existing_match:
                # Update existing match
                existing_match.status = match_data.get("status", "unknown")
                if match_data.get("winner_team"):
                    existing_match.winner = match_data.get("winner_team")
                    existing_match.result = match_data.get("status_note", "Match completed")
                existing_match.updated_at = datetime.utcnow()
            else:
                # Parse match date
                try:
                    match_date_str = match_data.get("date", "")
                    match_date = datetime.strptime(match_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                except (ValueError, TypeError):
                    match_date = datetime.utcnow() + timedelta(days=1)  # Default to tomorrow
                
                # Create new match
                team1 = match_data.get("teams", ["Unknown Team 1", "Unknown Team 2"])[0]
                team2 = match_data.get("teams", ["Unknown Team 1", "Unknown Team 2"])[1] if len(match_data.get("teams", [])) > 1 else "Unknown Team 2"
                
                new_match = CricketMatch(
                    match_id=match_id,
                    team1=team1,
                    team2=team2,
                    match_date=match_date,
                    status=match_data.get("status", "upcoming"),
                    venue=match_data.get("venue", "Unknown Venue"),
                    match_type=match_data.get("match_type", "Unknown"),
                    series_name=match_data.get("series_name", "Unknown Series"),
                    team1_odds=2.0,  # Default odds
                    team2_odds=2.0   # Default odds
                )
                
                db.session.add(new_match)
                
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error updating match database: {str(e)}")
        return False

def calculate_odds(team1, team2):
    """
    Calculate betting odds based on team rankings or past performance
    This is a simple implementation and could be enhanced with real data
    """
    # In a real app, you would use team rankings, past performance, etc.
    # For now, returning fixed odds with slight randomization
    import random
    
    # Random factors to make odds slightly different each time
    factor1 = random.uniform(0.8, 1.2)
    factor2 = random.uniform(0.8, 1.2)
    
    # Base odds
    team1_odds = 1.8 * factor1
    team2_odds = 2.2 * factor2
    
    # Ensure minimum odds
    team1_odds = max(1.2, team1_odds)
    team2_odds = max(1.2, team2_odds)
    
    return round(team1_odds, 2), round(team2_odds, 2)

def setup_match_events(match_id):
    """
    Set up betting events for a match like total runs, wickets, etc.
    """
    match = CricketMatch.query.filter_by(id=match_id).first()
    if not match:
        return False
    
    # Check if events already exist for this match
    existing_events = CricketEvent.query.filter_by(match_id=match_id).count()
    if existing_events > 0:
        return True  # Events already set up
    
    try:
        # Event 1: Total Sixes
        total_sixes_event = CricketEvent(
            match_id=match_id,
            event_type="total_sixes",
            description=f"Total number of sixes in the {match.team1} vs {match.team2} match"
        )
        db.session.add(total_sixes_event)
        db.session.flush()  # Get ID before adding options
        
        # Options for total sixes
        sixes_options = [
            {"name": "0-4 sixes", "odds": 3.5},
            {"name": "5-8 sixes", "odds": 2.0},
            {"name": "9-12 sixes", "odds": 2.5},
            {"name": "13+ sixes", "odds": 3.0}
        ]
        
        for option in sixes_options:
            event_option = CricketEventOption(
                event_id=total_sixes_event.id,
                option_name=option["name"],
                odds=option["odds"]
            )
            db.session.add(event_option)
        
        # Event 2: Highest Run Scorer
        top_scorer_event = CricketEvent(
            match_id=match_id,
            event_type="top_scorer",
            description=f"Highest run scorer in the {match.team1} vs {match.team2} match"
        )
        db.session.add(top_scorer_event)
        db.session.flush()
        
        # Options for top scorer (team names as placeholders)
        scorer_options = [
            {"name": f"Player from {match.team1}", "odds": 2.0},
            {"name": f"Player from {match.team2}", "odds": 2.0}
        ]
        
        for option in scorer_options:
            event_option = CricketEventOption(
                event_id=top_scorer_event.id,
                option_name=option["name"],
                odds=option["odds"]
            )
            db.session.add(event_option)
        
        # Event 3: Total Wickets
        wickets_event = CricketEvent(
            match_id=match_id,
            event_type="total_wickets",
            description=f"Total wickets in the {match.team1} vs {match.team2} match"
        )
        db.session.add(wickets_event)
        db.session.flush()
        
        # Options for total wickets
        wickets_options = [
            {"name": "0-6 wickets", "odds": 3.0},
            {"name": "7-12 wickets", "odds": 2.0},
            {"name": "13-16 wickets", "odds": 2.5},
            {"name": "17+ wickets", "odds": 4.0}
        ]
        
        for option in wickets_options:
            event_option = CricketEventOption(
                event_id=wickets_event.id,
                option_name=option["name"],
                odds=option["odds"]
            )
            db.session.add(event_option)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error setting up match events: {str(e)}")
        return False

@app.route('/cricket')
@login_required
def cricket_betting():
    """Main cricket betting page"""
    # Update matches database
    update_match_database()
    
    # Get upcoming and live matches
    upcoming_matches = CricketMatch.query.filter_by(status="upcoming").order_by(CricketMatch.match_date.asc()).all()
    live_matches = CricketMatch.query.filter_by(status="live").all()
    
    return render_template(
        'cricket_betting.html',
        upcoming_matches=upcoming_matches,
        live_matches=live_matches,
        balance=current_user.wallet_balance
    )

@app.route('/cricket/matches')
@login_required
def cricket_matches():
    """API endpoint to get matches data"""
    # Update matches database
    update_match_database()
    
    # Get upcoming and live matches
    upcoming_matches = CricketMatch.query.filter_by(status="upcoming").order_by(CricketMatch.match_date.asc()).limit(10).all()
    live_matches = CricketMatch.query.filter_by(status="live").all()
    
    # Format response
    matches_data = {
        "upcoming": [
            {
                "id": match.id,
                "match_id": match.match_id,
                "team1": match.team1,
                "team2": match.team2,
                "match_date": match.match_date.strftime("%Y-%m-%d %H:%M"),
                "venue": match.venue,
                "match_type": match.match_type,
                "series_name": match.series_name,
                "team1_odds": match.team1_odds,
                "team2_odds": match.team2_odds
            } for match in upcoming_matches
        ],
        "live": [
            {
                "id": match.id,
                "match_id": match.match_id,
                "team1": match.team1,
                "team2": match.team2,
                "venue": match.venue,
                "match_type": match.match_type,
                "series_name": match.series_name,
                "team1_odds": match.team1_odds,
                "team2_odds": match.team2_odds
            } for match in live_matches
        ]
    }
    
    return jsonify({"success": True, "data": matches_data})

@app.route('/cricket/match/<int:match_id>')
@login_required
def cricket_match_detail(match_id):
    """Match details page with betting options"""
    match = CricketMatch.query.get_or_404(match_id)
    
    # Set up match events if not already
    setup_match_events(match_id)
    
    # Get events for this match
    events = CricketEvent.query.filter_by(match_id=match_id).all()
    
    # Get user's bets for this match
    match_bets = CricketMatchBet.query.filter_by(user_id=current_user.id, match_id=match_id).all()
    event_bets = CricketEventBet.query.filter_by(user_id=current_user.id, match_id=match_id).all()
    
    return render_template(
        'cricket_match.html',
        match=match,
        events=events,
        match_bets=match_bets,
        event_bets=event_bets,
        balance=current_user.wallet_balance
    )

@app.route('/cricket/place-match-bet', methods=['POST'])
@login_required
def place_match_bet():
    """Place a bet on match winner"""
    try:
        data = request.get_json()
        match_id = int(data.get('match_id', 0))
        bet_amount = float(data.get('bet_amount', 0))
        prediction = data.get('prediction', '')  # 'team1', 'team2', or 'draw'
        
        # Validate inputs
        if not match_id or not prediction or bet_amount <= 0:
            return jsonify({'success': False, 'error': 'Invalid input parameters'})
        
        # Check if user has sufficient balance
        if current_user.wallet_balance < bet_amount:
            return jsonify({'success': False, 'error': 'Insufficient balance'})
        
        # Get match details
        match = CricketMatch.query.get(match_id)
        if not match:
            return jsonify({'success': False, 'error': 'Match not found'})
        
        # Check if match is still open for betting
        if match.status not in ['upcoming', 'live']:
            return jsonify({'success': False, 'error': 'Match is not open for betting'})
        
        # Determine odds based on prediction
        if prediction == 'team1':
            odds = match.team1_odds
        elif prediction == 'team2':
            odds = match.team2_odds
        elif prediction == 'draw':
            odds = match.draw_odds
        else:
            return jsonify({'success': False, 'error': 'Invalid prediction'})
        
        # Deduct bet amount from user's wallet
        current_user.wallet_balance -= bet_amount
        
        # Create bet record
        bet = CricketMatchBet(
            user_id=current_user.id,
            match_id=match_id,
            bet_amount=bet_amount,
            prediction=prediction,
            odds=odds,
            status="pending"
        )
        
        db.session.add(bet)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Bet placed successfully',
            'bet_id': bet.id,
            'new_balance': current_user.wallet_balance
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error placing match bet: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/cricket/place-event-bet', methods=['POST'])
@login_required
def place_event_bet():
    """Place a bet on match event (total runs, wickets, etc.)"""
    try:
        data = request.get_json()
        match_id = int(data.get('match_id', 0))
        event_id = int(data.get('event_id', 0))
        option_id = int(data.get('option_id', 0))
        bet_amount = float(data.get('bet_amount', 0))
        
        # Validate inputs
        if not match_id or not event_id or not option_id or bet_amount <= 0:
            return jsonify({'success': False, 'error': 'Invalid input parameters'})
        
        # Check if user has sufficient balance
        if current_user.wallet_balance < bet_amount:
            return jsonify({'success': False, 'error': 'Insufficient balance'})
        
        # Get match, event, and option details
        match = CricketMatch.query.get(match_id)
        event = CricketEvent.query.get(event_id)
        option = CricketEventOption.query.get(option_id)
        
        if not match or not event or not option:
            return jsonify({'success': False, 'error': 'Match, event, or option not found'})
        
        # Check if match is still open for betting
        if match.status not in ['upcoming', 'live']:
            return jsonify({'success': False, 'error': 'Match is not open for betting'})
        
        # Check if event is still open
        if event.status != 'open':
            return jsonify({'success': False, 'error': 'This event is closed for betting'})
        
        # Deduct bet amount from user's wallet
        current_user.wallet_balance -= bet_amount
        
        # Create bet record
        bet = CricketEventBet(
            user_id=current_user.id,
            match_id=match_id,
            event_id=event_id,
            event_option_id=option_id,
            bet_amount=bet_amount,
            odds=option.odds,
            status="pending"
        )
        
        db.session.add(bet)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Bet placed successfully',
            'bet_id': bet.id,
            'new_balance': current_user.wallet_balance
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error placing event bet: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/cricket/my-bets')
@login_required
def my_cricket_bets():
    """View user's cricket betting history"""
    # Get user's match bets
    match_bets = CricketMatchBet.query.filter_by(user_id=current_user.id).order_by(CricketMatchBet.placed_at.desc()).all()
    
    # Get user's event bets
    event_bets = CricketEventBet.query.filter_by(user_id=current_user.id).order_by(CricketEventBet.placed_at.desc()).all()
    
    return render_template(
        'cricket_my_bets.html',
        match_bets=match_bets,
        event_bets=event_bets,
        balance=current_user.wallet_balance
    )

@app.route('/cricket/settle-bets', methods=['POST'])
@login_required
def admin_settle_cricket_bets():
    """Admin route to manually settle pending bets (for demonstration)"""
    # Check if user is admin (you can add your own admin check)
    if current_user.id != 1:  # Assuming user id 1 is admin
        return jsonify({'success': False, 'error': 'Unauthorized access'})
    
    try:
        data = request.get_json()
        match_id = int(data.get('match_id', 0))
        winner = data.get('winner', '')  # 'team1', 'team2', 'draw'
        
        # Validate inputs
        if not match_id or not winner:
            return jsonify({'success': False, 'error': 'Invalid input parameters'})
        
        # Get match details
        match = CricketMatch.query.get(match_id)
        if not match:
            return jsonify({'success': False, 'error': 'Match not found'})
        
        # Update match result
        match.status = "completed"
        match.winner = match.team1 if winner == 'team1' else match.team2 if winner == 'team2' else "Draw"
        match.result = f"Match won by {match.winner}" if winner != 'draw' else "Match ended in a draw"
        
        # Get all pending bets for this match
        pending_bets = CricketMatchBet.query.filter_by(match_id=match_id, status="pending").all()
        
        # Settle each bet
        for bet in pending_bets:
            if bet.prediction == winner:
                # User won the bet
                bet.status = "won"
                bet.winnings = bet.bet_amount * bet.odds
                
                # Update user wallet
                user = User.query.get(bet.user_id)
                if user:
                    user.wallet_balance += bet.winnings
            else:
                # User lost the bet
                bet.status = "lost"
                bet.winnings = 0
            
            bet.settled_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Match result recorded and bets settled successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error settling cricket bets: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/cricket/settle-event', methods=['POST'])
@login_required
def admin_settle_cricket_event():
    """Admin route to manually settle event bets (for demonstration)"""
    # Check if user is admin
    if current_user.id != 1:  # Assuming user id 1 is admin
        return jsonify({'success': False, 'error': 'Unauthorized access'})
    
    try:
        data = request.get_json()
        event_id = int(data.get('event_id', 0))
        winning_option_id = int(data.get('winning_option_id', 0))
        
        # Validate inputs
        if not event_id or not winning_option_id:
            return jsonify({'success': False, 'error': 'Invalid input parameters'})
        
        # Get event and option details
        event = CricketEvent.query.get(event_id)
        winning_option = CricketEventOption.query.get(winning_option_id)
        
        if not event or not winning_option:
            return jsonify({'success': False, 'error': 'Event or option not found'})
        
        # Update event status
        event.status = "settled"
        event.result = winning_option.option_name
        
        # Update option status
        for option in event.options:
            if option.id == winning_option_id:
                option.status = "winner"
            else:
                option.status = "inactive"
        
        # Get all pending bets for this event
        pending_bets = CricketEventBet.query.filter_by(event_id=event_id, status="pending").all()
        
        # Settle each bet
        for bet in pending_bets:
            if bet.event_option_id == winning_option_id:
                # User won the bet
                bet.status = "won"
                bet.winnings = bet.bet_amount * bet.odds
                
                # Update user wallet
                user = User.query.get(bet.user_id)
                if user:
                    user.wallet_balance += bet.winnings
            else:
                # User lost the bet
                bet.status = "lost"
                bet.winnings = 0
            
            bet.settled_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Event result recorded and bets settled successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error settling cricket event bets: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred'})

@app.route('/cricket/history')
@login_required
def cricket_history():
    """View cricket betting history"""
    # Get completed matches
    completed_matches = CricketMatch.query.filter_by(status="completed").order_by(CricketMatch.match_date.desc()).limit(10).all()
    
    # Format response
    matches_data = [
        {
            "id": match.id,
            "team1": match.team1,
            "team2": match.team2,
            "match_date": match.match_date.strftime("%Y-%m-%d %H:%M"),
            "venue": match.venue,
            "winner": match.winner,
            "result": match.result
        } for match in completed_matches
    ]
    
    return jsonify({"success": True, "data": matches_data})

if __name__ == '__main__':
    app.run(debug=True)
