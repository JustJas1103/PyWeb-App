-- Railway-compatible MySQL dump for pinoyluto_db
-- Generated for Railway MySQL service
-- Compatible with MySQL 8.0+

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- Create database if not exists (Railway handles this, but included for completeness)
-- CREATE DATABASE IF NOT EXISTS `pinoyluto_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
-- USE `pinoyluto_db`;

-- Table structure for table `admin`
CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table `admin`
INSERT INTO `admin` (`id`, `username`, `password`) VALUES
(5, 'admin', '$2b$12$hMQvKi0UEKWBqAfy4hsObeLn1IUI7yN1VIx/BuIORX9uZC/YR.ffW');

-- Table structure for table `users`
CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `fullname` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `profile_pic` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table `users`
INSERT INTO `users` (`id`, `fullname`, `email`, `password`, `created_at`, `profile_pic`) VALUES
(6, 'Jas', 'jas@gmail.com', '$2b$12$1DNyCxprLXkkWy.OV7TC/uXyPqKNYAaLz7DWlkkbJ/TLnbcYyGoSe', '2025-10-12 10:31:48', NULL),
(7, 'Carlos Miguel', 'torjarica@gmail.com', '$2b$12$g/FV.YNj1NRTt8lcYhW30eg/pFSP1azdg6QSYJ.PTYQk6nCBaYbNm', '2025-10-13 03:59:52', NULL);

-- Table structure for table `ingredients`
CREATE TABLE `ingredients` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `category` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table `ingredients`
INSERT INTO `ingredients` (`id`, `name`, `category`) VALUES
(1, 'bangus', 'seafood'),
(2, 'tilapia', 'seafood'),
(3, 'shrimp', 'seafood'),
(4, 'crab', 'seafood'),
(5, 'squid', 'seafood'),
(6, 'chicken', 'meat'),
(7, 'pork belly', 'meat'),
(8, 'beef', 'meat'),
(9, 'eggplant', 'vegetable'),
(10, 'okra', 'vegetable'),
(11, 'ampalaya', 'vegetable'),
(12, 'squash', 'vegetable'),
(13, 'tomato', 'vegetable'),
(14, 'garlic', 'spice'),
(15, 'onion', 'spice'),
(16, 'ginger', 'spice'),
(17, 'soy sauce', 'spice'),
(18, 'vinegar', 'spice'),
(19, 'salt', 'spice'),
(20, 'pepper', 'spice'),
(21, 'sugar', 'spice'),
(22, 'coconut milk', 'dessert'),
(23, 'ube', 'dessert'),
(24, 'sweet potato', 'dessert'),
(25, 'sticky rice', 'dessert'),
(26, 'mango', 'dessert'),
(27, 'banana', 'dessert'),
(28, 'calamansi', 'spice'),
(29, 'fish sauce', 'spice'),
(31, 'fish', 'seafood');

-- Table structure for table `detections`
CREATE TABLE `detections` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `image_path` varchar(255) NOT NULL,
  `detected_foods` json NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- No initial data for detections

-- Table structure for table `chat_history`
CREATE TABLE `chat_history` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `question` text NOT NULL,
  `response` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- No initial data for chat_history

-- Table structure for table `favorites`
CREATE TABLE `favorites` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `food_name` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- No initial data for favorites

-- Indexes and constraints
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

ALTER TABLE `ingredients`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

ALTER TABLE `detections`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD CONSTRAINT `detections_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

ALTER TABLE `chat_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD CONSTRAINT `chat_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

ALTER TABLE `favorites`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD CONSTRAINT `favorites_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

-- Auto-increment settings
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

ALTER TABLE `ingredients`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

ALTER TABLE `detections`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `chat_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `favorites`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

COMMIT;