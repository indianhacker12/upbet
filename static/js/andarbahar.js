// Andar Bahar Game Logic
$(document).ready(function() {
    // Game variables
    let selectedSide = ''; // 'andar' or 'bahar'
    let currentBet = 100;
    let gameActive = false;
    let soundEnabled = true;
    let balance = parseFloat($('#userBalance').text());
    
    // Card deck
    const suits = ['hearts', 'diamonds', 'clubs', 'spades'];
    const values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];
    
    // Sound effects
    const cardFlipSound = document.getElementById('cardFlipSound');
    const winSound = document.getElementById('winSound');
    const loseSound = document.getElementById('loseSound');
    const buttonClickSound = document.getElementById('buttonClickSound');
    
    // Init UI
    updateBetAmount();
    
    // Event Listeners
    $('#andarBetBtn').click(function() {
        if (gameActive) return;
        
        playSound(buttonClickSound);
        selectSide('andar');
    });
    
    $('#baharBetBtn').click(function() {
        if (gameActive) return;
        
        playSound(buttonClickSound);
        selectSide('bahar');
    });
    
    $('#decreaseBetBtn').click(function() {
        if (gameActive) return;
        
        playSound(buttonClickSound);
        currentBet = Math.max(10, currentBet - 10);
        updateBetAmount();
    });
    
    $('#increaseBetBtn').click(function() {
        if (gameActive) return;
        
        playSound(buttonClickSound);
        currentBet = Math.min(10000, currentBet + 10);
        updateBetAmount();
    });
    
    $('#betAmount').on('input', function() {
        if (gameActive) return;
        
        let amount = parseInt($(this).val());
        
        if (isNaN(amount)) {
            amount = 100;
        } else {
            amount = Math.max(10, Math.min(10000, amount));
        }
        
        currentBet = amount;
        updateBetAmount();
    });
    
    $('#playBtn').click(function() {
        if (gameActive || !selectedSide) return;
        
        playSound(buttonClickSound);
        startGame();
    });
    
    $('#soundToggle').click(function() {
        soundEnabled = !soundEnabled;
        $(this).text(soundEnabled ? '🔊' : '🔇');
    });
    
    // Helper functions
    function selectSide(side) {
        selectedSide = side;
        $('.bet-option').removeClass('selected');
        
        if (side === 'andar') {
            $('#andarBetBtn').addClass('selected');
            $('#andarLabel').addClass('highlight');
            $('#baharLabel').removeClass('highlight');
        } else {
            $('#baharBetBtn').addClass('selected');
            $('#baharLabel').addClass('highlight');
            $('#andarLabel').removeClass('highlight');
        }
    }
    
    function updateBetAmount() {
        $('#betAmount').val(currentBet);
    }
    
    function startGame() {
        // Validate bet
        if (balance < currentBet) {
            showNotification('Not enough balance to place this bet', 'error');
            return;
        }
        
        // Deduct bet from balance (visual only)
        balance -= currentBet;
        $('#userBalance').text(balance.toFixed(0));
        
        gameActive = true;
        clearGameBoard();
        
        // Send bet to server
        $.ajax({
            url: '/andarbahar/place-bet',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                side: selectedSide,
                amount: currentBet
            }),
            success: function(response) {
                if (response.status === 'success') {
                    // Prepare joker card for display
                    const jokerParts = response.joker_card_str.split(" of ");
                    const jokerValue = jokerParts[0];
                    const jokerSuit = jokerParts[1];
                    dealJokerCard(jokerValue + '-' + jokerSuit);
                    
                    // Process cards for display
                    const cardsToDisplay = [];
                    let andarCards = [];
                    let baharCards = [];
                    
                    // Create alternating arrays of cards
                    let currentSide = 'andar';
                    for (let i = 0; i < response.cards.length; i++) {
                        const card = response.cards[i];
                        const formattedCard = card.value + '-' + card.suit;
                        
                        if (currentSide === 'andar') {
                            andarCards.push(formattedCard);
                            currentSide = 'bahar';
                        } else {
                            baharCards.push(formattedCard);
                            currentSide = 'andar';
                        }
                        
                        // Stop at matching card
                        if (i === response.matching_index) {
                            break;
                        }
                    }
                    
                    setTimeout(() => {
                        dealGameCards(andarCards, baharCards, response.winning_side, response.winnings);
                    }, 1500);
                    
                    // Update user stats
                    $('#totalPlayed').text(parseInt($('#totalPlayed').text()) + 1);
                    if (response.result === 'win') {
                        $('#totalWins').text(parseInt($('#totalWins').text()) + 1);
                        if (response.winning_side === 'andar') {
                            $('#andarWins').text(parseInt($('#andarWins').text()) + 1);
                        } else {
                            $('#baharWins').text(parseInt($('#baharWins').text()) + 1);
                        }
                    }
                    
                    // Update win rate
                    const totalGames = parseInt($('#totalPlayed').text());
                    const totalWins = parseInt($('#totalWins').text());
                    const winRate = (totalWins / totalGames * 100).toFixed(1);
                    $('#winRate').text(winRate + '%');
                    
                    // Update balance from server
                    balance = response.new_balance;
                    $('#userBalance').text(balance.toFixed(0));
                } else {
                    showNotification(response.error || 'Error occurred', 'error');
                    gameActive = false;
                    
                    // Restore visual balance
                    balance += currentBet;
                    $('#userBalance').text(balance.toFixed(0));
                }
            },
            error: function(xhr, status, error) {
                showNotification('Error connecting to server: ' + error, 'error');
                gameActive = false;
                
                // Restore visual balance
                balance += currentBet;
                $('#userBalance').text(balance.toFixed(0));
            }
        });
    }
    
    function clearGameBoard() {
        $('#jokerCard').removeClass('flipped');
        $('#jokerCard .card-face.card-front .card-value').empty();
        $('#andarCards').empty();
        $('#baharCards').empty();
        $('#resultMessage').removeClass('win lose').empty().hide();
    }
    
    function dealJokerCard(cardStr) {
        const [value, suit] = cardStr.split('-');
        const cardColor = suit === 'hearts' || suit === 'diamonds' ? 'red' : 'black';
        
        // Create card content
        const cardContent = $('<div>').addClass(`card-content ${cardColor}`);
        cardContent.append($('<span>').addClass('card-value-top').text(value));
        cardContent.append($('<span>').addClass('card-suit').html(getSuitSymbol(suit)));
        cardContent.append($('<span>').addClass('card-value-bottom').text(value));
        
        // Add to DOM
        $('#jokerCard .card-face.card-front .card-value').html(cardContent);
        
        // Play sound
        playSound(cardFlipSound);
        
        // Flip animation
        setTimeout(() => {
            $('#jokerCard').addClass('flipped');
        }, 500);
    }
    
    function dealGameCards(andarCards, baharCards, winningSide, winnings) {
        const dealInterval = 300; // ms between cards
        let currentDelay = 0;
        
        // Deal Andar cards
        andarCards.forEach((card, index) => {
            setTimeout(() => {
                playSound(cardFlipSound);
                addCardToSection('andar', card, index === andarCards.length - 1 && winningSide === 'andar');
            }, currentDelay);
            currentDelay += dealInterval;
        });
        
        // Deal Bahar cards
        baharCards.forEach((card, index) => {
            setTimeout(() => {
                playSound(cardFlipSound);
                addCardToSection('bahar', card, index === baharCards.length - 1 && winningSide === 'bahar');
            }, currentDelay);
            currentDelay += dealInterval;
        });
        
        // Show result after cards are dealt
        setTimeout(() => {
            showResult(winningSide, winnings);
            gameActive = false;
        }, currentDelay + 500);
    }
    
    function addCardToSection(section, card, isWinningCard) {
        const [value, suit] = card.split('-');
        const cardColor = suit === 'hearts' || suit === 'diamonds' ? 'red' : 'black';
        
        const cardElement = $('<div>').addClass('game-card');
        
        if (isWinningCard) {
            cardElement.addClass('winning-card');
        }
        
        const cardContent = $('<div>').addClass(`card-content ${cardColor}`);
        cardContent.append($('<span>').addClass('card-value-top').text(value));
        cardContent.append($('<span>').addClass('card-suit').html(getSuitSymbol(suit)));
        cardContent.append($('<span>').addClass('card-value-bottom').text(value));
        
        cardElement.append(cardContent);
        
        $(`#${section}Cards`).append(cardElement);
    }
    
    function showResult(winningSide, winnings) {
        const resultElement = $('#resultMessage');
        
        if (winningSide === selectedSide) {
            playSound(winSound);
            resultElement.addClass('win').text(`You won ₹${winnings}!`).fadeIn();
        } else {
            playSound(loseSound);
            resultElement.addClass('lose').text('You lost!').fadeIn();
        }
        
        // Highlight winning side
        if (winningSide === 'andar') {
            $('#andarLabel').addClass('winner');
            setTimeout(() => {
                $('#andarLabel').removeClass('winner');
            }, 3000);
        } else {
            $('#baharLabel').addClass('winner');
            setTimeout(() => {
                $('#baharLabel').removeClass('winner');
            }, 3000);
        }
    }
    
    function showNotification(message, type = 'info') {
        const notification = $('#notification');
        notification.text(message).addClass(type).fadeIn();
        
        setTimeout(() => {
            notification.fadeOut(() => {
                notification.removeClass(type);
            });
        }, 3000);
    }
    
    function getSuitSymbol(suit) {
        switch (suit) {
            case 'hearts': return '❤️';
            case 'diamonds': return '♦️';
            case 'clubs': return '♣️';
            case 'spades': return '♠️';
            default: return '';
        }
    }
    
    function playSound(sound) {
        if (soundEnabled && sound) {
            sound.currentTime = 0;
            sound.play().catch(e => console.log('Sound play error:', e));
        }
    }
}); 