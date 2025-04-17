-- Create slot_game table if it doesn't exist
CREATE TABLE IF NOT EXISTS `slot_game` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `bet_amount` float NOT NULL,
  `symbols` varchar(50) NOT NULL,
  `multiplier` float NOT NULL,
  `winnings` float NOT NULL,
  `timestamp` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `slot_game_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Create reference to User table
-- Make sure this reference matches your User table structure
-- The above FOREIGN KEY should work if your User table has 'id' as primary key 