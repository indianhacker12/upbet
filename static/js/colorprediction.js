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
    const betHistoryBody = document.getElementById('betHistoryBody');
    const colorsBettingSection = document.getElementById('colorsBettingSection');
    const numbersBettingSection = document.getElementById('numbersBettingSection');
    const oddEvenBettingSection = document.getElementById('oddEvenBettingSection');
    
    // Game variables
    let userBalance = parseFloat(userBalanceElement.textContent.replace('₹', '').replace(/,/g, ''));
    let betAmount = 10;
    let isBetPlaced = false;
    let selectedBet = null;
    let betType = null; // 'color', 'number', or 'odd-even'
    let countdownInterval;
    let timeLeft = 30;
    let gameHistory = [];
    let betHistory = [];
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
        // Fetch bet history
        fetchBetHistory();
    }
    
    // Betting functions
    function decreaseBet() {
        if (betAmount > 10) {
            betAmount -= 10;
            betAmountDisplay.textContent = betAmount;
            document.getElementById('betAmount').textContent = betAmount;
            playSound(clickSound);
        }
    }
    
    function increaseBet() {
        if (betAmount < 1000) {
            betAmount += 10;
            betAmountDisplay.textContent = betAmount;
            document.getElementById('betAmount').textContent = betAmount;
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
        if (isBetPlaced || selectedBet === null) {
            showNotification('Please select a bet option first!', 'error');
            return;
        }
        
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
                
                // Add to local bet history
                addBetToHistory({
                    type: betType,
                    value: selectedBet,
                    amount: betAmount,
                    result: 'pending',
                    timestamp: new Date()
                });
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
            
            // Update last bet history entry
            updateLastBetResult('win', winAmount);
        } else {
            showNotification('Better luck next time!', 'error');
            playSound(loseSound);
            
            // Update last bet history entry
            updateLastBetResult('lose', 0);
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
    
    // Fetch bet history from server
    function fetchBetHistory() {
        fetch('/api/colorprediction/bet-history')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                betHistory = data.history.slice(0, 10);
                updateBetHistoryDisplay();
            }
        })
        .catch(error => {
            console.error('Error fetching bet history:', error);
            // Use mock data for demo purposes
            betHistory = [];
            updateBetHistoryDisplay();
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
    
    // Update bet history display
    function updateBetHistoryDisplay() {
        betHistoryBody.innerHTML = '';
        
        betHistory.forEach(bet => {
            const row = document.createElement('tr');
            
            // Time column
            const timeCell = document.createElement('td');
            const betTime = new Date(bet.timestamp);
            timeCell.textContent = betTime.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
            
            // Bet column
            const betCell = document.createElement('td');
            if (bet.type === 'color') {
                betCell.textContent = bet.value.charAt(0).toUpperCase() + bet.value.slice(1);
            } else if (bet.type === 'number') {
                betCell.textContent = 'Number ' + bet.value;
            } else if (bet.type === 'odd-even') {
                betCell.textContent = bet.value.charAt(0).toUpperCase() + bet.value.slice(1);
            }
            
            // Amount column
            const amountCell = document.createElement('td');
            amountCell.textContent = '₹' + bet.amount;
            
            // Result column
            const resultCell = document.createElement('td');
            if (bet.result === 'win') {
                resultCell.textContent = '₹' + (bet.winnings || 0);
                resultCell.style.color = '#2ecc71';
            } else if (bet.result === 'lose') {
                resultCell.textContent = '-₹' + bet.amount;
                resultCell.style.color = '#e74c3c';
            } else {
                resultCell.textContent = 'Pending';
                resultCell.style.color = '#f39c12';
            }
            
            // Append cells to row
            row.appendChild(timeCell);
            row.appendChild(betCell);
            row.appendChild(amountCell);
            row.appendChild(resultCell);
            
            // Append row to table
            betHistoryBody.appendChild(row);
        });
    }
    
    // Add bet to history
    function addBetToHistory(bet) {
        betHistory.unshift(bet);
        if (betHistory.length > 10) {
            betHistory.pop();
        }
        updateBetHistoryDisplay();
    }
    
    // Update last bet result
    function updateLastBetResult(result, winnings) {
        if (betHistory.length > 0) {
            betHistory[0].result = result;
            betHistory[0].winnings = winnings;
            updateBetHistoryDisplay();
        }
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