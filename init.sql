--
-- Table structure for table `policy`
--

CREATE TABLE `policy` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(36) NOT NULL,
  `description` varchar(63) DEFAULT '',
  `enabled` tinyint(4) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


--
-- Table structure for table `subject`
--

CREATE TABLE `subject` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(36) NOT NULL,
  `description` varchar(63) DEFAULT '',
  `enabled` tinyint(4) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


--
-- Table structure for table `box`
--

CREATE TABLE `box` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(36) NOT NULL,
  `description` varchar(63) DEFAULT '',
  `policy_id` int(11) unsigned NOT NULL,
  `subject_id` int(11) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fkey_box_policy_id` (`policy_id`),
  KEY `fkey_box_subject_id` (`subject_id`),
  CONSTRAINT `fkey_box_policy_id` FOREIGN KEY (`policy_id`) REFERENCES `policy` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fkey_box_subject_id` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


--
-- Table structure for table `match_param`
--

CREATE TABLE `match_param` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(36) NOT NULL,
  `description` varchar(63) DEFAULT '',
  `params` varchar(512) NOT NULL,
  `type` varchar(36) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


--
-- Table structure for table `rule`
--

CREATE TABLE `rule` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(36) NOT NULL,
  `description` varchar(63) DEFAULT '',
  `level` int(11) unsigned NOT NULL,
  `effect_on` varchar(36) NOT NULL,
  `match_type` varchar(36) NOT NULL,
  `match_value` varchar(512) NOT NULL,
  `match_param_id` int(11) unsigned DEFAULT NULL,
  `enabled` tinyint(4) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


--
-- Table structure for table `policy_rule`
--

CREATE TABLE `policy_rule` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `policy_id` int(11) unsigned NOT NULL,
  `rule_id` int(11) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fkey_policy_rule_policy_id` (`policy_id`),
  KEY `fkey_policy_rule_rule_id` (`rule_id`),
  CONSTRAINT `fkey_policy_rule_policy_id` FOREIGN KEY (`policy_id`) REFERENCES `policy` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fkey_policy_rule_rule_id` FOREIGN KEY (`rule_id`) REFERENCES `rule` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `service_script`
--

CREATE TABLE `service_script` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `service` varchar(63) NOT NULL,
  `content_type` varchar(36) DEFAULT NULL,
  `content_field` varchar(63) DEFAULT NULL,
  `endpoint_field` varchar(63) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='serivce script extraction ';


--
-- Table structure for table `target`
--

CREATE TABLE `target` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(36) NOT NULL,
  `args_scope` varchar(512) DEFAULT NULL,
  `entity_scope` varchar(512) DEFAULT NULL,
  `enabled` tinyint(4) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


--
-- Table structure for table `subject_target`
--

CREATE TABLE `subject_target` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) unsigned NOT NULL,
  `target_id` int(11) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fkey_subject_target_subject_id` (`subject_id`),
  KEY `fkey_subject_target_target_id` (`target_id`),
  CONSTRAINT `fkey_subject_target_subject_id` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fkey_subject_target_target_id` FOREIGN KEY (`target_id`) REFERENCES `target` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

