-- Create game_settings table if it doesn't exist
CREATE TABLE IF NOT EXISTS game_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    game_type VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    base_multiplier FLOAT NOT NULL DEFAULT 1.0,
    risk_factor FLOAT NULL DEFAULT 1.0,
    min_bet FLOAT NOT NULL DEFAULT 10.0,
    max_bet FLOAT NOT NULL DEFAULT 10000.0,
    house_edge FLOAT NOT NULL DEFAULT 0.03,
    custom_settings JSON NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_game_type (game_type)
);

-- Insert default game settings if not exists
INSERT INTO game_settings (game_type, is_active, base_multiplier, min_bet, max_bet, house_edge)
VALUES 
    ('Mines', TRUE, 1.0, 10.0, 5000.0, 0.03),
    ('Plinko', TRUE, 1.0, 10.0, 5000.0, 0.03),
    ('Slots', TRUE, 1.0, 10.0, 1000.0, 0.05),
    ('MegaSlots', TRUE, 1.0, 20.0, 2000.0, 0.04),
    ('LuckyWheel', TRUE, 1.0, 10.0, 1000.0, 0.03),
    ('Aviator', TRUE, 1.0, 10.0, 5000.0, 0.04),
    ('CoinFlip', TRUE, 1.0, 10.0, 3000.0, 0.03),
    ('OddEven', TRUE, 1.0, 10.0, 3000.0, 0.03)
ON DUPLICATE KEY UPDATE
    is_active = VALUES(is_active);

-- Add game-specific custom settings
UPDATE game_settings 
SET custom_settings = JSON_OBJECT(
    'grid_sizes', JSON_ARRAY(3, 5, 7),
    'max_mines', 24,
    'default_mines', 3
)
WHERE game_type = 'Mines';

UPDATE game_settings 
SET custom_settings = JSON_OBJECT(
    'available_rows', JSON_ARRAY(8, 12, 16),
    'risk_levels', JSON_OBJECT(
        'low', 1.0,
        'medium', 1.2,
        'high', 1.5
    )
)
WHERE game_type = 'Plinko';

UPDATE game_settings 
SET custom_settings = JSON_OBJECT(
    'crash_rate', 0.99,
    'max_multiplier', 100.0
)
WHERE game_type = 'Aviator';

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_game_settings_game_type ON game_settings(game_type); 