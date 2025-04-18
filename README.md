# XBetin - Online Betting Platform

XBetin is a comprehensive online betting platform offering multiple game options including Mines, Dice, Plinko, Slots, Mega Slots, Lucky Wheel, Aviator, Coin Flip, and Odd/Even betting.

## Features

- **Multiple Games**: Variety of betting games with different mechanics
- **User Management**: Registration, login, account management
- **Wallet System**: Deposit and withdrawal functionality via Razorpay integration
- **Game History**: Track your betting history for each game
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript
- **Payment Integration**: Razorpay

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/xbetin.git
   cd xbetin
   ```

2. Set up a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env.template` to `.env`
   - Add your Razorpay API keys

4. Set up Razorpay configuration:
   - Copy `razorpay_config.py.template` to `razorpay_config.py`
   - Add your Razorpay API keys

5. Initialize the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. Run the application:
   ```
   flask run
   ```

## Screenshots

(Add screenshots of different games and features here)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
