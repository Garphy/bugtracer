-- phpMyAdmin SQL Dump
-- version 4.3.11.1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: 2019-01-11 19:17:30
-- 服务器版本： 5.5.61-0ubuntu0.14.04.1
-- PHP Version: 5.5.37-1+deprecated+dontuse+deb.sury.org~trusty+1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `bug`
--

-- --------------------------------------------------------

--
-- 表的结构 `items`
--

DROP TABLE IF EXISTS `items`;
CREATE TABLE IF NOT EXISTS `items` (
  `id` mediumint(8) unsigned NOT NULL,
  `type` mediumint(6) unsigned NOT NULL,
  `status` smallint(1) unsigned NOT NULL DEFAULT '1',
  `ver` varchar(10) DEFAULT NULL,
  `content` mediumtext NOT NULL,
  `creator` mediumint(6) unsigned DEFAULT NULL,
  `assignto` mediumint(6) unsigned NOT NULL,
  `timestamp` int(10) unsigned NOT NULL,
  `lastchanger` mediumint(6) unsigned DEFAULT NULL,
  `changetime` int(10) unsigned NOT NULL,
  `fix_time` int(10) unsigned DEFAULT NULL,
  `close_reason` mediumtext,
  `files` varchar(255) DEFAULT NULL
) ENGINE=MyISAM AUTO_INCREMENT=492 DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `projects`
--

DROP TABLE IF EXISTS `projects`;
CREATE TABLE IF NOT EXISTS `projects` (
  `pid` mediumint(6) unsigned NOT NULL,
  `pname` varchar(50) NOT NULL,
  `members` varchar(255) DEFAULT NULL
) ENGINE=MyISAM AUTO_INCREMENT=17 DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `types`
--

DROP TABLE IF EXISTS `types`;
CREATE TABLE IF NOT EXISTS `types` (
  `tid` mediumint(6) unsigned NOT NULL,
  `pid` mediumint(6) unsigned NOT NULL,
  `name` varchar(20) NOT NULL
) ENGINE=MyISAM AUTO_INCREMENT=58 DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `uid` mediumint(6) unsigned NOT NULL,
  `username` varchar(20) NOT NULL,
  `password` char(32) NOT NULL DEFAULT 'e10adc3949ba59abbe56e057f20f883e',
  `fullname` varchar(10) NOT NULL,
  `role` varchar(10) NOT NULL
) ENGINE=MyISAM AUTO_INCREMENT=34 DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `items`
--
ALTER TABLE `items`
  ADD PRIMARY KEY (`id`), ADD UNIQUE KEY `type` (`id`,`type`,`status`,`creator`,`assignto`,`changetime`);

--
-- Indexes for table `projects`
--
ALTER TABLE `projects`
  ADD PRIMARY KEY (`pid`);

--
-- Indexes for table `types`
--
ALTER TABLE `types`
  ADD PRIMARY KEY (`tid`), ADD KEY `fid` (`pid`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`uid`), ADD UNIQUE KEY `username` (`uid`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `items`
--
ALTER TABLE `items`
  MODIFY `id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `projects`
--
ALTER TABLE `projects`
  MODIFY `pid` mediumint(6) unsigned NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `types`
--
ALTER TABLE `types`
  MODIFY `tid` mediumint(6) unsigned NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `uid` mediumint(6) unsigned NOT NULL AUTO_INCREMENT;
	
INSERT INTO `projects` (`pid`, `pname`, `members`) VALUES
(0, '公共模块', '');