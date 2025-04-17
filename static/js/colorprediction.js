document.addEventListener('DOMContentLoaded', function() {
    // Game elements
    const userBalanceElement = document.getElementById('userBalance');
    const betAmountDisplay = document.getElementById('betAmountDisplay');
    const decreaseBetBtn = document.getElementById('decreaseBetBtn');
    const increaseBetBtn = document.getElementById('increaseBetBtn');
    const countdownElement = document.getElementById('countdown');
    const resultDisplay = document.getElementById('resultDisplay');
    const lastResultElement = document.getElementById('lastResult');
    const historyResults = document.getElementById('historyResults');
    const placeBetBtn = document.getElementById('placeBetBtn');
    const notification = document.getElementById('notification');
    const soundToggle = document.getElementById('soundToggle');
    const soundToggleCheckbox = document.getElementById('soundToggleCheckbox');
    const bettingCategories = document.querySelectorAll('.betting-category');
    const colorsBettingSection = document.getElementById('colorsBettingSection');
    const numbersBettingSection = document.getElementById('numbersBettingSection');
    const oddEvenBettingSection = document.getElementById('oddEvenBettingSection');
    
    // Game variables
    let userBalance = parseFloat(userBalanceElement.textContent.replace('₹', '').replace(/,/g, ''));
    let betAmount = 10;
    let isBetPlaced = false;
    let selectedBet = null;
    let betType = 'color'; // 'color', 'number', or 'odd-even'
    let countdownInterval;
    let timeLeft = 30;
    let gameHistory = [];
    let soundEnabled = localStorage.getItem('colorPredictionSoundEnabled') !== 'false';
    
    // Sound effects
    const betSound = new Audio('/static/sounds/bet.mp3');
    const winSound = new Audio('/static/sounds/win.mp3');
    const loseSound = new Audio('/static/sounds/lose.mp3');
    const clickSound = new Audio('/static/sounds/click.mp3');
    
    // Initialize game
    function initGame() {
        updateSoundToggle();
        startCountdown();
        
        // Set up event listeners
        decreaseBetBtn.addEventListener('click', decreaseBet);
        increaseBetBtn.addEventListener('click', increaseBet);
        placeBetBtn.addEventListener('click', placeBet);
        soundToggle.addEventListener('click', toggleSound);
        soundToggleCheckbox.addEventListener('change', toggleSound);
        
        // Set up betting options
        const colorBets = document.querySelectorAll('.color-bet');
        colorBets.forEach(bet => {
            bet.addEventListener('click', function() {
                selectBet(this, 'color');
            });
        });
        
        const numberBets = document.querySelectorAll('.number-bet');
        numberBets.forEach(bet => {
            bet.addEventListener('click', function() {
                selectBet(this, 'number');
            });
        });
        
        const oddEvenBets = document.querySelectorAll('.odd-even-bet');
        oddEvenBets.forEach(bet => {
            bet.addEventListener('click', function() {
                selectBet(this, 'odd-even');
            });
        });
        
        // Set up betting category tabs
        bettingCategories.forEach(category => {
            category.addEventListener('click', function() {
                const categoryType = this.dataset.category;
                
                // Update active category
                bettingCategories.forEach(cat => cat.classList.remove('active'));
                this.classList.add('active');
                
                // Show appropriate betting section
                colorsBettingSection.style.display = 'none';
                numbersBettingSection.style.display = 'none';
                oddEvenBettingSection.style.display = 'none';
                
                if (categoryType === 'colors') {
                    colorsBettingSection.style.display = 'grid';
                    betType = 'color';
                } else if (categoryType === 'numbers') {
                    numbersBettingSection.style.display = 'grid';
                    betType = 'number';
                } else if (categoryType === 'odd-even') {
                    oddEvenBettingSection.style.display = 'grid';
                    betType = 'odd-even';
                }
                
                // Clear any selected bet
                clearSelectedBets();
                selectedBet = null;
                playSound(clickSound);
            });
        });
        
        // Set up tabs in rules section
        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const tabId = this.dataset.tab;
                
                // Update active button
                tabButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Show appropriate tab content
                const tabPanes = document.querySelectorAll('.tab-pane');
                tabPanes.forEach(pane => pane.classList.remove('active'));
                document.getElementById(tabId).classList.add('active');
                
                playSound(clickSound);
            });
        });
        
        // Fetch game history
        fetchGameHistory();
    }
    
    // Betting functions
    function decreaseBet() {
        if (betAmount > 10) {
            betAmount -= 10;
            betAmountDisplay.textContent = betAmount;
            playSound(clickSound);
        }
    }
    
    function increaseBet() {
        if (betAmount < 1000) {
            betAmount += 10;
            betAmountDisplay.textContent = betAmount;
            playSound(clickSound);
        }
    }
    
    function selectBet(element, type) {
        if (isBetPlaced) return;
        
        // Clear previous selections
        clearSelectedBets();
        
        // Set new selection
        element.classList.add('selected');
        betType = type;
        
        if (type === 'color') {
            selectedBet = element.dataset.color;
        } else if (type === 'number') {
            selectedBet = element.dataset.number;
        } else if (type === 'odd-even') {
            selectedBet = element.dataset.bet;
        }
        
        playSound(clickSound);
    }
    
    function clearSelectedBets() {
        document.querySelectorAll('.bet-control').forEach(control => {
            control.classList.remove('selected');
        });
    }
    
    function placeBet() {
        if (isBetPlaced || selectedBet === null) return;
        
        if (betAmount > userBalance) {
            showNotification('Insufficient balance!', 'error');
            return;
        }
        
        // Send bet to server
        fetch('/api/colorprediction/place-bet', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                betAmount: betAmount,
                betType: betType,
                selectedBet: selectedBet
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                isBetPlaced = true;
                userBalance -= betAmount;
                userBalanceElement.textContent = '₹' + formatNumber(userBalance);
                placeBetBtn.disabled = true;
                placeBetBtn.textContent = 'Bet Placed';
                showNotification('Bet placed successfully!', 'success');
                playSound(betSound);
            } else {
                showNotification(data.message || 'Failed to place bet', 'error');
            }
        })
        .catch(error => {
            console.error('Error placing bet:', error);
            showNotification('Error placing bet. Please try again.', 'error');
        });
    }
    
    // Countdown and game logic
    function startCountdown() {
        timeLeft = 30;
        updateCountdown();
        
        countdownInterval = setInterval(() => {
            timeLeft--;
            
            if (timeLeft <= 0) {
                clearInterval(countdownInterval);
                endGame();
                setTimeout(() => {
                    startNewGame();
                }, 3000);
            }
            
            updateCountdown();
        }, 1000);
    }
    
    function updateCountdown() {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        countdownElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        if (timeLeft <= 5) {
            countdownElement.style.color = '#e74c3c';
        } else {
            countdownElement.style.color = '';
        }
    }
    
    function endGame() {
        // Get the game result from the server
        fetch('/api/colorprediction/get-result')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const result = data.result;
                displayResult(result);
                
                // Update game history
                gameHistory.unshift(result);
                if (gameHistory.length > 10) {
                    gameHistory.pop();
                }
                updateHistoryDisplay();
                
                // Check if user won
                if (isBetPlaced) {
                    setTimeout(() => {
                        checkWin(result);
                    }, 1000);
                }
            } else {
                showNotification('Failed to get game result', 'error');
            }
        })
        .catch(error => {
            console.error('Error getting game result:', error);
            showNotification('Error getting game result', 'error');
        });
    }
    
    function displayResult(result) {
        // Display result
        const resultType = result.type; // color, number, odd-even
        const resultValue = result.value;
        
        lastResultElement.textContent = '';
        
        if (resultType === 'color') {
            lastResultElement.textContent = resultValue.charAt(0).toUpperCase() + resultValue.slice(1);
            lastResultElement.className = 'result-value ' + resultValue;
        } else if (resultType === 'number') {
            lastResultElement.textContent = resultValue;
            
            // Assign color based on number
            if (resultValue % 3 === 0) {
                lastResultElement.className = 'result-value blue';
            } else if (resultValue % 3 === 1) {
                lastResultElement.className = 'result-value red';
            } else {
                lastResultElement.className = 'result-value green';
            }
        } else if (resultType === 'odd-even') {
            lastResultElement.textContent = resultValue.toUpperCase();
            
            if (resultValue === 'odd') {
                lastResultElement.className = 'result-value red';
            } else {
                lastResultElement.className = 'result-value blue';
            }
        }
    }
    
    function checkWin(result) {
        if (!isBetPlaced) return;
        
        let isWin = false;
        let multiplier = 1;
        
        if (betType === result.type && selectedBet === result.value) {
            isWin = true;
            
            if (betType === 'color') {
                multiplier = 3;
            } else if (betType === 'number') {
                multiplier = 9;
            } else if (betType === 'odd-even') {
                multiplier = 2;
            }
        } else if (betType === 'color' && result.type === 'number') {
            // Special case: number results can match color bets
            let numberColor;
            if (result.value % 3 === 0) {
                numberColor = 'blue';
            } else if (result.value % 3 === 1) {
                numberColor = 'red';
            } else {
                numberColor = 'green';
            }
            
            if (selectedBet === numberColor) {
                isWin = true;
                multiplier = 3;
            }
        }
        
        if (isWin) {
            const winAmount = betAmount * multiplier;
            userBalance += winAmount;
            userBalanceElement.textContent = '₹' + formatNumber(userBalance);
            showNotification(`Congratulations! You won ₹${formatNumber(winAmount - betAmount)}!`, 'success');
            playSound(winSound);
        } else {
            showNotification('Better luck next time!', 'error');
            playSound(loseSound);
        }
    }
    
    function startNewGame() {
        // Reset game state
        isBetPlaced = false;
        selectedBet = null;
        clearSelectedBets();
        
        // Reset UI
        placeBetBtn.disabled = false;
        placeBetBtn.textContent = 'Place Bet';
        
        // Start new countdown
        startCountdown();
    }
    
    // Fetch game history from server
    function fetchGameHistory() {
        fetch('/api/colorprediction/history')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                gameHistory = data.history.slice(0, 10);
                updateHistoryDisplay();
            }
        })
        .catch(error => {
            console.error('Error fetching history:', error);
        });
    }
    
    // Update history display
    function updateHistoryDisplay() {
        historyResults.innerHTML = '';
        
        gameHistory.forEach(result => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-result';
            
            if (result.type === 'color') {
                historyItem.classList.add(result.value);
            } else if (result.type === 'number') {
                historyItem.textContent = result.value;
                
                // Assign color based on number
                if (result.value % 3 === 0) {
                    historyItem.classList.add('blue');
                } else if (result.value % 3 === 1) {
                    historyItem.classList.add('red');
                } else {
                    historyItem.classList.add('green');
                }
            } else if (result.type === 'odd-even') {
                historyItem.textContent = result.value.charAt(0).toUpperCase();
                
                if (result.value === 'odd') {
                    historyItem.classList.add('red');
                } else {
                    historyItem.classList.add('blue');
                }
            }
            
            historyResults.appendChild(historyItem);
        });
    }
    
    // Utility functions
    function formatNumber(number) {
        return parseFloat(number).toLocaleString('en-IN', {
            maximumFractionDigits: 2,
            minimumFractionDigits: 2
        });
    }
    
    function showNotification(message, type) {
        notification.textContent = message;
        notification.className = 'notification ' + type;
        notification.classList.add('show');
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }
    
    function toggleSound() {
        soundEnabled = !soundEnabled;
        localStorage.setItem('colorPredictionSoundEnabled', soundEnabled);
        updateSoundToggle();
        playSound(clickSound);
    }
    
    function updateSoundToggle() {
        soundToggle.innerHTML = soundEnabled ? '<i class="fas fa-volume-up"></i>' : '<i class="fas fa-volume-mute"></i>';
        soundToggleCheckbox.checked = soundEnabled;
    }
    
    function playSound(sound) {
        if (soundEnabled) {
            sound.currentTime = 0;
            sound.play().catch(e => console.error('Error playing sound:', e));
        }
    }
    
    // Initialize the game
    initGame();
}); 