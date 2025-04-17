-- Create transactions table if it doesn't exist
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    amount FLOAT NOT NULL,
    type ENUM('deposit', 'withdrawal', 'referral', 'bonus', 'game_win', 'game_loss') NOT NULL,
    status ENUM('pending', 'completed', 'failed', 'cancelled') NOT NULL DEFAULT 'pending',
    payment_method VARCHAR(50) NULL,
    transaction_details JSON NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- Create index for faster lookups
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_type ON transactions(type);
CREATE INDEX idx_transactions_status ON transactions(status);

-- Insert some sample data (for testing purposes only)
INSERT INTO transactions (user_id, amount, type, status, payment_method)
SELECT id, 1000.00, 'deposit', 'completed', 'razorpay'
FROM user
ORDER BY id
LIMIT 5;

INSERT INTO transactions (user_id, amount, type, status, payment_method)
SELECT id, 500.00, 'withdrawal', 'pending', 'bank_transfer'
FROM user
ORDER BY id
LIMIT 3; 