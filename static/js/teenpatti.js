document.addEventListener('DOMContentLoaded', function() {
    // Game variables
    let currentBet = 50;
    let minBet = 10;
    let maxBet = 10000;
    let gameActive = false;
    let gameType = 'classic';
    let playerCards = [];
    let dealerCards = [];
    let showingCards = false;
    
    // DOM Elements
    const balanceElement = document.getElementById('balance');
    const gameTypeButtons = document.querySelectorAll('.game-type-btn');
    const betAmountInput = document.getElementById('betAmount');
    const decreaseBetBtn = document.getElementById('decreaseBet');
    const increaseBetBtn = document.getElementById('increaseBet');
    const playButton = document.getElementById('playButton');
    const showButton = document.getElementById('showButton');
    const foldButton = document.getElementById('foldButton');
    const playerCardsContainer = document.getElementById('playerCards');
    const dealerCardsContainer = document.getElementById('dealerCards');
    const resultMessage = document.getElementById('resultMessage');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const soundToggle = document.getElementById('soundToggle');
    
    // Sounds
    const cardSound = new Audio('/static/sounds/card_flip.mp3');
    const winSound = new Audio('/static/sounds/win.mp3');
    const loseSound = new Audio('/static/sounds/lose.mp3');
    const buttonSound = new Audio('/static/sounds/button_click.mp3');
    
    let soundEnabled = localStorage.getItem('teenPattiSoundEnabled') !== 'false';
    updateSoundToggle();
    
    // Initialize game
    initGame();
    
    function initGame() {
        // Set initial bet amount
        betAmountInput.value = currentBet;
        
        // Add event listeners
        gameTypeButtons.forEach(button => {
            button.addEventListener('click', function() {
                gameTypeButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                gameType = this.getAttribute('data-type');
                playSound(buttonSound);
            });
        });
        
        decreaseBetBtn.addEventListener('click', () => {
            adjustBet(-10);
            playSound(buttonSound);
        });
        
        increaseBetBtn.addEventListener('click', () => {
            adjustBet(10);
            playSound(buttonSound);
        });
        
        betAmountInput.addEventListener('change', function() {
            let value = parseInt(this.value.replace(/,/g, ''));
            if (isNaN(value)) value = minBet;
            value = Math.min(Math.max(value, minBet), maxBet);
            currentBet = value;
            this.value = value;
        });
        
        playButton.addEventListener('click', startGame);
        showButton.addEventListener('click', showCards);
        foldButton.addEventListener('click', foldCards);
        
        soundToggle.addEventListener('click', toggleSound);
    }
    
    function adjustBet(amount) {
        currentBet = parseInt(betAmountInput.value.replace(/,/g, '')) || currentBet;
        currentBet = Math.min(Math.max(currentBet + amount, minBet), maxBet);
        betAmountInput.value = currentBet;
    }
    
    function startGame() {
        if (gameActive) return;
        
        // Validate bet amount
        currentBet = parseInt(betAmountInput.value.replace(/,/g, '')) || currentBet;
        currentBet = Math.min(Math.max(currentBet, minBet), maxBet);
        betAmountInput.value = currentBet;
        
        // Check if player has enough balance
        const currentBalance = parseInt(balanceElement.textContent.replace(/[₹,]/g, ''));
        if (currentBalance < currentBet) {
            showNotification('Insufficient balance!', 'error');
            return;
        }
        
        // Start the game
        gameActive = true;
        showingCards = false;
        
        // Update UI
        playButton.disabled = true;
        showButton.disabled = false;
        foldButton.disabled = false;
        resultMessage.textContent = '';
        resultMessage.className = 'result-message';
        
        // Clear previous cards
        playerCardsContainer.innerHTML = '';
        dealerCardsContainer.innerHTML = '';
        playerCards = [];
        dealerCards = [];
        
        // Show loading spinner
        loadingSpinner.classList.remove('hidden');
        
        // Play sound
        playSound(buttonSound);
        
        // Send request to server
        fetch('/teenpatti/play', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                bet_amount: currentBet,
                game_type: gameType,
                action: 'start'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                loadingSpinner.classList.add('hidden');
                
                // Update balance
                balanceElement.textContent = '₹' + formatNumber(data.balance);
                
                // Deal player cards
                playerCards = data.player_cards;
                dealerCards = data.dealer_cards;
                
                // Display player cards
                dealCards(playerCards, playerCardsContainer, true);
                
                // Display dealer cards (face down)
                dealCards(dealerCards, dealerCardsContainer, false);
            } else {
                handleError(data.message);
            }
        })
        .catch(error => {
            handleError('Network error. Please try again.');
            console.error('Error:', error);
        });
    }
    
    function dealCards(cards, container, faceUp) {
        container.innerHTML = '';
        
        cards.forEach((card, index) => {
            setTimeout(() => {
                const cardElement = document.createElement('div');
                cardElement.className = 'game-card';
                
                if (faceUp) {
                    cardElement.classList.add('flipped');
                    cardElement.innerHTML = createCardHTML(card);
                } else {
                    cardElement.classList.add('back');
                }
                
                container.appendChild(cardElement);
                playSound(cardSound);
                
                setTimeout(() => {
                    cardElement.classList.add('dealt');
                }, 50);
            }, index * 300);
        });
    }
    
    function createCardHTML(card) {
        const [value, suit] = card.split('-');
        let suitSymbol = '';
        let suitColor = '';
        
        switch(suit) {
            case 'hearts':
                suitSymbol = '♥';
                suitColor = 'red';
                break;
            case 'diamonds':
                suitSymbol = '♦';
                suitColor = 'red';
                break;
            case 'clubs':
                suitSymbol = '♣';
                suitColor = 'black';
                break;
            case 'spades':
                suitSymbol = '♠';
                suitColor = 'black';
                break;
        }
        
        let valueDisplay = value;
        if (value === 'A') valueDisplay = 'A';
        if (value === 'K') valueDisplay = 'K';
        if (value === 'Q') valueDisplay = 'Q';
        if (value === 'J') valueDisplay = 'J';
        if (value === '10') valueDisplay = '10';
        
        return `
            <div class="card-content">
                <div class="card-value ${suitColor}">${valueDisplay}</div>
                <div class="card-suit ${suitColor}">${suitSymbol}</div>
            </div>
        `;
    }
    
    function showCards() {
        if (!gameActive || showingCards) return;
        showingCards = true;
        
        // Disable buttons during reveal
        showButton.disabled = true;
        foldButton.disabled = true;
        
        // Show loading spinner
        loadingSpinner.classList.remove('hidden');
        
        // Play sound
        playSound(buttonSound);
        
        // Send request to server
        fetch('/teenpatti/play', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                bet_amount: currentBet,
                game_type: gameType,
                action: 'show'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                loadingSpinner.classList.add('hidden');
                
                // Update balance
                balanceElement.textContent = '₹' + formatNumber(data.balance);
                
                // Reveal dealer cards
                revealDealerCards();
                
                // Display result
                setTimeout(() => {
                    displayResult(data.result, data.player_hand_type, data.dealer_hand_type, data.winnings);
                    
                    // Play appropriate sound
                    if (data.result === 'win') {
                        playSound(winSound);
                    } else {
                        playSound(loseSound);
                    }
                }, 1500);
                
                // Reset game state
                setTimeout(resetGameState, 3000);
            } else {
                handleError(data.message);
            }
        })
        .catch(error => {
            handleError('Network error. Please try again.');
            console.error('Error:', error);
        });
    }
    
    function foldCards() {
        if (!gameActive || showingCards) return;
        showingCards = true;
        
        // Disable buttons during fold
        showButton.disabled = true;
        foldButton.disabled = true;
        
        // Show loading spinner
        loadingSpinner.classList.remove('hidden');
        
        // Play sound
        playSound(buttonSound);
        
        // Send request to server
        fetch('/teenpatti/play', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                bet_amount: currentBet,
                game_type: gameType,
                action: 'fold'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                loadingSpinner.classList.add('hidden');
                
                // Update balance
                balanceElement.textContent = '₹' + formatNumber(data.balance);
                
                // Show fold message
                displayFold();
                
                // Play lose sound
                playSound(loseSound);
                
                // Reset game state
                setTimeout(resetGameState, 2000);
            } else {
                handleError(data.message);
            }
        })
        .catch(error => {
            handleError('Network error. Please try again.');
            console.error('Error:', error);
        });
    }
    
    function revealDealerCards() {
        const cardElements = dealerCardsContainer.querySelectorAll('.game-card');
        
        dealerCards.forEach((card, index) => {
            setTimeout(() => {
                if (cardElements[index]) {
                    cardElements[index].classList.remove('back');
                    cardElements[index].classList.add('flipped');
                    cardElements[index].innerHTML = createCardHTML(card);
                    playSound(cardSound);
                }
            }, index * 300);
        });
    }
    
    function displayResult(result, playerHandType, dealerHandType, winnings) {
        resultMessage.textContent = result === 'win' 
            ? `You win! ${playerHandType} beats ${dealerHandType}. +₹${formatNumber(winnings)}`
            : `You lose! ${dealerHandType} beats ${playerHandType}. -₹${formatNumber(currentBet)}`;
        
        resultMessage.className = 'result-message ' + (result === 'win' ? 'win' : 'loss');
        resultMessage.classList.add('animated');
    }
    
    function displayFold() {
        resultMessage.textContent = `You folded. -₹${formatNumber(currentBet)}`;
        resultMessage.className = 'result-message loss';
        resultMessage.classList.add('animated');
    }
    
    function resetGameState() {
        gameActive = false;
        showingCards = false;
        playButton.disabled = false;
        showButton.disabled = true;
        foldButton.disabled = true;
    }
    
    function handleError(message) {
        loadingSpinner.classList.add('hidden');
        showNotification(message, 'error');
        resetGameState();
    }
    
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = 'notification ' + type;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
    
    function formatNumber(number) {
        return new Intl.NumberFormat('en-IN').format(number);
    }
    
    function playSound(sound) {
        if (soundEnabled && sound) {
            sound.currentTime = 0;
            sound.play().catch(e => {
                // Autoplay policy restrictions, ignore error
            });
        }
    }
    
    function toggleSound() {
        soundEnabled = !soundEnabled;
        localStorage.setItem('teenPattiSoundEnabled', soundEnabled);
        updateSoundToggle();
        playSound(buttonSound);
    }
    
    function updateSoundToggle() {
        if (soundToggle) {
            soundToggle.innerHTML = soundEnabled 
                ? '<i class="fas fa-volume-up"></i>' 
                : '<i class="fas fa-volume-mute"></i>';
            soundToggle.title = soundEnabled ? 'Mute Sounds' : 'Enable Sounds';
        }
    }
}); 