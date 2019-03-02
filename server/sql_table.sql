CREATE TABLE `notams` (
  `id` varchar(100) NOT NULL,
  `entity` varchar(100) DEFAULT NULL,
  `status` varchar(100) DEFAULT NULL,
  `Qcode` varchar(100) DEFAULT NULL,
  `Area` varchar(100) DEFAULT NULL,
  `SubArea` varchar(100) DEFAULT NULL,
  `Condition` varchar(100) DEFAULT NULL,
  `Subject` varchar(100) DEFAULT NULL,
  `Modifier` varchar(100) DEFAULT NULL,
  `message` text,
  `startdate` datetime DEFAULT NULL,
  `enddate` datetime DEFAULT NULL,
  `all` text,
  `location` varchar(100) DEFAULT NULL,
  `isICAO` tinyint(1) DEFAULT NULL,
  `type` varchar(100) DEFAULT NULL,
  `StateCode` varchar(100) DEFAULT NULL,
  `StateName` varchar(100) DEFAULT NULL,
  `decoded` text,
  `priority` float DEFAULT '1',
  `UpdatedAt` timestamp NULL DEFAULT NULL,
  `Created` datetime DEFAULT NULL,
  `key` varchar(100) DEFAULT NULL,
  `q_status` varchar(100) DEFAULT NULL,
  `entity_category` varchar(100) DEFAULT NULL,
  `status_category` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE DEFINER=`root`@`localhost` PROCEDURE `haro`.`e_smooth`(
tam_id varchar(100),
feedback_value FLOAT,
alpha FLOAT
)
BEGIN
UPDATE haro.notams
SET priority = ( ( alpha * feedback_value ) + ( ( 1 - alpha ) * priority) )
WHERE id = tam_id;
END;
