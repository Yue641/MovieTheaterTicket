-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th12 30, 2024 lúc 03:03 PM
-- Phiên bản máy phục vụ: 10.4.28-MariaDB
-- Phiên bản PHP: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `dbtheatre`
--

DELIMITER $$
--
-- Thủ tục
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `delete_old` ()   begin

	declare curdate date;
set curdate=curdate();

DELETE FROM shows 
WHERE datediff(Date,curdate)<0;

DELETE FROM shows 
WHERE movie_id IN 
(SELECT movie_id 
FROM movies
WHERE datediff(show_end,curdate)<0);

DELETE FROM movies 
WHERE datediff(show_end,curdate)<0;

end$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `booked_tickets`
--

CREATE TABLE `booked_tickets` (
  `ticket_no` int(11) NOT NULL,
  `show_id` int(11) NOT NULL,
  `seat_no` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `booked_tickets`
--

INSERT INTO `booked_tickets` (`ticket_no`, `show_id`, `seat_no`) VALUES
(186393464, 1857151805, 1011),
(202068624, 1443748345, 11),
(452039845, 1015025678, 1018),
(1259920277, 1443748345, 39),
(1324787581, 1857151805, 1024),
(1687265870, 413408296, 88),
(1690239834, 1443748345, 1019),
(1724999093, 1016691532, 1018);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `halls`
--

CREATE TABLE `halls` (
  `hall_id` int(11) NOT NULL,
  `class` varchar(10) NOT NULL,
  `no_of_seats` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `halls`
--

INSERT INTO `halls` (`hall_id`, `class`, `no_of_seats`) VALUES
(1, 'gold', 35),
(1, 'standard', 75),
(2, 'gold', 27),
(2, 'standard', 97),
(3, 'gold', 26),
(3, 'standard', 98);

--
-- Bẫy `halls`
--
DELIMITER $$
CREATE TRIGGER `get_price` AFTER INSERT ON `halls` FOR EACH ROW begin

UPDATE shows s, price_listing p 
SET s.price_id=p.price_id 
WHERE p.price_id IN 
(SELECT price_id 
FROM price_listing p 
WHERE dayname(s.Date)=p.day AND s.type=p.type);

end
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `movies`
--

CREATE TABLE `movies` (
  `movie_id` int(11) NOT NULL,
  `movie_name` varchar(40) DEFAULT NULL,
  `length` int(11) DEFAULT NULL,
  `language` varchar(10) DEFAULT NULL,
  `show_start` date DEFAULT NULL,
  `show_end` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `movies`
--

INSERT INTO `movies` (`movie_id`, `movie_name`, `length`, `language`, `show_start`, `show_end`) VALUES
(120261508, 'The Conjuring 1', 150, 'English', '2024-12-05', '2025-01-01'),
(467963378, 'Batman 3', 150, 'English', '2024-12-05', '2025-01-10'),
(792620896, 'IT', 126, 'English', '2024-12-05', '2025-01-10'),
(809589785, 'Avatar', 120, 'English', '2024-12-05', '2025-01-01'),
(871785646, 'Dog Knows Everything', 126, 'Korean', '2024-12-05', '2025-01-10'),
(974753220, 'Batman', 90, 'English', '2024-11-30', '2024-12-30'),
(1256930880, 'The Spiderman 3', 150, 'English', '2024-12-06', '2024-12-31'),
(1681527525, 'Spider Man 2', 170, 'English', '2024-12-05', '2025-01-01'),
(1851824250, 'The Stranger by The Beach', 126, 'Japan', '2024-12-05', '2025-01-10');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `price_listing`
--

CREATE TABLE `price_listing` (
  `price_id` int(11) NOT NULL,
  `type` varchar(3) DEFAULT NULL,
  `day` varchar(10) DEFAULT NULL,
  `price` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `price_listing`
--

INSERT INTO `price_listing` (`price_id`, `type`, `day`, `price`) VALUES
(1, '2D', 'Monday', 10),
(2, '3D', 'Monday', 12),
(3, '4DX', 'Monday', 15),
(4, '2D', 'Tuesday', 10),
(5, '3D', 'Tuesday', 12),
(6, '4DX', 'Tuesday', 14),
(7, '2D', 'Wednesday', 8),
(8, '3D', 'Wednesday', 10),
(9, '4DX', 'Wednesday', 12),
(10, '2D', 'Thursday', 10),
(11, '3D', 'Thursday', 12),
(12, '4DX', 'Thursday', 15),
(13, '2D', 'Friday', 12),
(14, '3D', 'Friday', 15),
(15, '4DX', 'Friday', 22),
(16, '2D', 'Saturday', 12),
(17, '3D', 'Saturday', 15),
(18, '4DX', 'Saturday', 20),
(19, '2D', 'Sunday', 10),
(20, '3D', 'Sunday', 13),
(21, '4DX', 'Sunday', 17);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `shows`
--

CREATE TABLE `shows` (
  `show_id` int(11) NOT NULL,
  `movie_id` int(11) DEFAULT NULL,
  `hall_id` int(11) DEFAULT NULL,
  `type` varchar(3) DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  `Date` date DEFAULT NULL,
  `price_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `shows`
--

INSERT INTO `shows` (`show_id`, `movie_id`, `hall_id`, `type`, `time`, `Date`, `price_id`) VALUES
(158614666, 467963378, 2, '3D', 1300, '2024-12-23', 2),
(413408296, 871785646, 2, '2D', 1000, '2024-12-06', 13),
(834380546, 120261508, 1, '2D', 1145, '2024-12-16', 1),
(1015025678, 1256930880, 3, '2D', 1115, '2024-12-10', 4),
(1016691532, 974753220, 2, '3D', 1715, '2024-12-05', 11),
(1246716363, 120261508, 3, '3D', 1000, '2024-12-15', 20),
(1443748345, 974753220, 3, '3D', 1200, '2024-12-25', 8),
(1477340058, 809589785, 3, '4DX', 1145, '2024-12-24', 6),
(1857151805, 809589785, 2, '4DX', 1300, '2024-12-08', 21),
(1978053906, 1681527525, 2, '4DX', 1230, '2024-12-10', 6),
(2094335307, 1851824250, 2, '2D', 1015, '2024-12-07', 16);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `types`
--

CREATE TABLE `types` (
  `movie_id` int(11) NOT NULL,
  `type1` varchar(3) DEFAULT NULL,
  `type2` varchar(3) DEFAULT NULL,
  `type3` varchar(3) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `types`
--

INSERT INTO `types` (`movie_id`, `type1`, `type2`, `type3`) VALUES
(120261508, '2D', '3D', 'NUL'),
(467963378, '2D', '3D', 'NUL'),
(792620896, '2D', 'NUL', 'NUL'),
(809589785, '3D', '4DX', 'NUL'),
(871785646, '2D', 'NUL', 'NUL'),
(974753220, '3D', 'NUL', 'NUL'),
(1256930880, '2D', 'NUL', 'NUL'),
(1681527525, '2D', '4DX', 'NUL'),
(1851824250, '2D', 'NUL', 'NUL');

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `booked_tickets`
--
ALTER TABLE `booked_tickets`
  ADD PRIMARY KEY (`ticket_no`,`show_id`),
  ADD KEY `show_id` (`show_id`);

--
-- Chỉ mục cho bảng `halls`
--
ALTER TABLE `halls`
  ADD PRIMARY KEY (`hall_id`,`class`);

--
-- Chỉ mục cho bảng `movies`
--
ALTER TABLE `movies`
  ADD PRIMARY KEY (`movie_id`);

--
-- Chỉ mục cho bảng `price_listing`
--
ALTER TABLE `price_listing`
  ADD PRIMARY KEY (`price_id`);

--
-- Chỉ mục cho bảng `shows`
--
ALTER TABLE `shows`
  ADD PRIMARY KEY (`show_id`),
  ADD KEY `movie_id` (`movie_id`),
  ADD KEY `hall_id` (`hall_id`),
  ADD KEY `price_id` (`price_id`);

--
-- Chỉ mục cho bảng `types`
--
ALTER TABLE `types`
  ADD PRIMARY KEY (`movie_id`);

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `booked_tickets`
--
ALTER TABLE `booked_tickets`
  ADD CONSTRAINT `booked_tickets_ibfk_1` FOREIGN KEY (`show_id`) REFERENCES `shows` (`show_id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `shows`
--
ALTER TABLE `shows`
  ADD CONSTRAINT `shows_ibfk_1` FOREIGN KEY (`movie_id`) REFERENCES `movies` (`movie_id`),
  ADD CONSTRAINT `shows_ibfk_2` FOREIGN KEY (`hall_id`) REFERENCES `halls` (`hall_id`),
  ADD CONSTRAINT `shows_ibfk_3` FOREIGN KEY (`price_id`) REFERENCES `price_listing` (`price_id`) ON UPDATE CASCADE;

--
-- Các ràng buộc cho bảng `types`
--
ALTER TABLE `types`
  ADD CONSTRAINT `types_ibfk_1` FOREIGN KEY (`movie_id`) REFERENCES `movies` (`movie_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
