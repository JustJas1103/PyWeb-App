-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 22, 2025 at 07:26 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `pinoyluto_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `username`, `password`) VALUES
(5, 'admin', '$2b$12$hMQvKi0UEKWBqAfy4hsObeLn1IUI7yN1VIx/BuIORX9uZC/YR.ffW');

-- --------------------------------------------------------

--
-- Table structure for table `ingredients`
--

CREATE TABLE `ingredients` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `category` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `ingredients`
--

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

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `fullname` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `fullname`, `email`, `password`, `created_at`) VALUES
(6, 'Jas', 'jas@gmail.com', '$2b$12$1DNyCxprLXkkWy.OV7TC/uXyPqKNYAaLz7DWlkkbJ/TLnbcYyGoSe', '2025-10-12 10:31:48'),
(7, 'Carlos Miguel', 'torjarica@gmail.com', '$2b$12$g/FV.YNj1NRTt8lcYhW30eg/pFSP1azdg6QSYJ.PTYQk6nCBaYbNm', '2025-10-13 03:59:52');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `ingredients`
--
ALTER TABLE `ingredients`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `ingredients`
--
ALTER TABLE `ingredients`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
