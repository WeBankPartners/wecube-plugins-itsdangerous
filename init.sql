SET FOREIGN_KEY_CHECKS = 0;

--
-- Table structure for table `box`
--

DROP TABLE IF EXISTS `box`;
CREATE TABLE `box` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(36) NOT NULL,
  `description` varchar(63) DEFAULT '',
  `policy_id` bigint(20) unsigned NOT NULL,
  `subject_id` bigint(20) unsigned NOT NULL,
  `enabled` tinyint(4) NOT NULL,
  `created_by` varchar(36) DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `updated_by` varchar(36) DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fkey_box_policy_id` (`policy_id`),
  KEY `fkey_box_subject_id` (`subject_id`),
  CONSTRAINT `fkey_box_policy_id` FOREIGN KEY (`policy_id`) REFERENCES `policy` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fkey_box_subject_id` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `box`
--

LOCK TABLES `box` WRITE;
INSERT INTO `box` VALUES (1,'通用试盒','一些基本的shell&sql危险命令规则集合，针对所有对象',1,1,1,'admin','2020-11-01 00:00:00',NULL,NULL);
UNLOCK TABLES;

--
-- Table structure for table `match_param`
--

DROP TABLE IF EXISTS `match_param`;
CREATE TABLE `match_param` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(36) NOT NULL,
  `description` varchar(63) DEFAULT '',
  `params` varchar(512) NOT NULL,
  `type` varchar(36) NOT NULL,
  `created_by` varchar(36) DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `updated_by` varchar(36) DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `match_param`
--

LOCK TABLES `match_param` WRITE;
INSERT INTO `match_param` VALUES (1,'iregex','正则校验参数，针对大小写不敏感的场景','{\"flag\": \"I\"}','regex','admin','2020-11-01 00:00:00',NULL,NULL),(2,'rm','rm命令行参数定义','{\"name\":\"rm\", \"args\": [{\"name\": \"force\", \"shortcut\": \"-f,--force\", \"action\": \"store_true\"}, {\"name\": \"recursive\", \"shortcut\": \"-r,-R,--recursive\", \"action\": \"store_true\"}, {\"name\": \"help\", \"shortcut\": \"--help\", \"action\": \"store_true\"}, {\"name\": \"version\", \"shortcut\": \"--version\", \"action\": \"store_true\"}, {\"name\": \"path\", \"repeatable\": \"*\"}]}','cli','admin','2020-11-01 00:00:00',NULL,NULL),(3,'kill','kill命令行参数定义','{\"name\":\"kill\", \"args\": [{\"name\": \"name\", \"shortcut\": \"-s\"}, {\"name\": \"number\", \"shortcut\": \"-n\"}, {\"name\": \"help\", \"shortcut\": \"--help\", \"action\": \"store_true\"}, {\"name\": \"s_kill\", \"shortcut\": \"-9,-15\", \"action\": \"store_true\"}, {\"name\": \"pid\", \"repeatable\": \"*\"}]}','cli','admin','2020-11-01 00:00:00',NULL,NULL),(4,'reboot','reboot命令行参数定义','{\"name\":\"reboot\", \"args\": [{\"name\": \"help\", \"shortcut\": \"--help\", \"action\": \"store_true\"}]}','cli','admin','2020-11-01 00:00:00',NULL,NULL),(5,'netcat','necat命令行参数定义，reverse shell(nc)','{\"name\":\"nc\", \"args\": []}','cli','admin','2020-11-01 00:00:00',NULL,NULL),(6,'socat','socat命令行参数定义，reverse shell(socat)','{\"name\":\"socat\", \"args\": []}','cli','admin','2020-11-01 00:00:00',NULL,NULL),(7,'bash','bash交互式命令行参数定义','{\"name\":\"bash\", \"opt_strip_path\": true, \"args\": [{\"name\": \"interact\", \"shortcut\": \"-i\", \"action\": \"store_true\"},{\"name\": \"command\", \"repeatable\": \"*\"}]}','cli','admin','2020-11-01 00:00:00',NULL,NULL);
UNLOCK TABLES;

--
-- Table structure for table `policy`
--

DROP TABLE IF EXISTS `policy`;
CREATE TABLE `policy` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(36) NOT NULL,
  `description` varchar(63) DEFAULT '',
  `enabled` tinyint(4) NOT NULL,
  `created_by` varchar(36) DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `updated_by` varchar(36) DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `policy`
--

LOCK TABLES `policy` WRITE;
INSERT INTO `policy` VALUES (1,'基础策略','包含数据销毁性操作的规则',1,'admin','2020-11-01 00:00:00',NULL,NULL);
UNLOCK TABLES;

--
-- Table structure for table `policy_rule`
--

DROP TABLE IF EXISTS `policy_rule`;
CREATE TABLE `policy_rule` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `policy_id` bigint(20) unsigned NOT NULL,
  `rule_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fkey_policy_rule_policy_id` (`policy_id`),
  KEY `fkey_policy_rule_rule_id` (`rule_id`),
  CONSTRAINT `fkey_policy_rule_policy_id` FOREIGN KEY (`policy_id`) REFERENCES `policy` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fkey_policy_rule_rule_id` FOREIGN KEY (`rule_id`) REFERENCES `rule` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `policy_rule`
--

LOCK TABLES `policy_rule` WRITE;
INSERT INTO `policy_rule` VALUES (1,1,17),(2,1,16),(3,1,15),(4,1,11),(5,1,8),(6,1,7),(7,1,6),(9,1,4),(10,1,1);
UNLOCK TABLES;

--
-- Table structure for table `rule`
--

DROP TABLE IF EXISTS `rule`;
CREATE TABLE `rule` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(36) NOT NULL,
  `description` varchar(63) DEFAULT '',
  `level` varchar(36) NOT NULL,
  `effect_on` varchar(36) NOT NULL,
  `match_type` varchar(36) NOT NULL,
  `match_value` varchar(512) NOT NULL,
  `match_param_id` bigint(20) unsigned DEFAULT NULL,
  `enabled` tinyint(4) NOT NULL,
  `created_by` varchar(36) DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `updated_by` varchar(36) DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `rule`
--

LOCK TABLES `rule` WRITE;
INSERT INTO `rule` VALUES (1,'rm批量删除文件','删除目录下全量文件，可能会删除过多文件，建议明确删除目标','high','script','cli','[{\"name\": \"force\", \"operator\": \"set\"}, {\"name\": \"recursive\", \"operator\": \"set\"}, {\"name\": \"help\", \"operator\": \"notset\"}, {\"name\": \"version\", \"operator\": \"notset\"}, {\"name\": \"path\", \"operator\": \"ilike\", \"value\": \"*\"}]',2,1,'admin','2020-11-01 00:00:00',NULL,NULL),(2,'reboot系统重启','系统重启，可能会导致数据丢失，需要确认应用关闭后执行','medium','script','cli','[{\"name\": \"help\", \"operator\": \"notset\"}]',4,1,'admin','2020-11-01 00:00:00',NULL,NULL),(3,'sysctl修改系统参数','修改系统参数可能会造成全局影响','low','script','text','sysctl',NULL,1,'admin','2020-11-01 00:00:00',NULL,NULL),(4,'drop删除数据表','drop table，可能会造成数据丢失','critical','script','sql','^drop\\s+table\\s+.*$',1,1,'admin','2020-11-01 00:00:00',NULL,NULL),(6,'rm删除根分区','将删除根分区，导致操作系统不可用，非常危险。','critical','script','cli','[{\"name\": \"force\", \"operator\": \"set\"}, {\"name\": \"recursive\", \"operator\": \"set\"}, {\"name\": \"help\", \"operator\": \"notset\"}, {\"name\": \"version\", \"operator\": \"notset\"}, {\"name\": \"path\", \"operator\": \"eq\", \"value\": \"/\"}]',2,1,'admin','2020-11-01 00:00:00',NULL,NULL),(7,'truncate清空数据表','turncate table，可能会造成数据丢失','critical','script','sql','^truncate\\s+table\\s+.*$',1,1,'admin','2020-11-01 00:00:00',NULL,NULL),(8,'delete清空数据表','delete table语句没有带上正确的where条件语句，可能会误删数据','critical','script','sql','^delete\\s+from\\s+(?:(?!where).)*$',1,1,'admin','2020-11-01 00:00:00',NULL,NULL),(9,'sql更改外键限制','SET FOREIGN_KEY_CHECKS手动关闭外键校验，可能会导致数据不合法','low','script','sql','^SET\\s+FOREIGN_KEY_CHECKS=\\d;$',1,1,'admin','2020-11-01 00:00:00',NULL,NULL),(10,'sql更改表结构','ALTER TABLE，更改表结构可能会影响应用的运行','low','script','sql','^ALTER\\s+TABLE\\s+.*$',1,1,'admin','2020-11-01 00:00:00',NULL,NULL),(11,'update更新表全量数据','update table语句没有带上正确的where条件语句，可能会误删数据','high','script','sql','^update\\s+(?:(?!where).)*$',1,1,'admin','2020-11-01 00:00:00',NULL,NULL),(12,'强制kill(cli-s)','强制kill会导致应用非正常退出，一般建议使用kill即可','medium','script','cli','[{\"name\": \"name\", \"operator\": \"in\", \"value\": [\"KILL\", \"TERM\"]}, {\"name\": \"pid\", \"operator\": \"set\"}]',3,1,'admin','2020-11-01 00:00:00',NULL,NULL),(13,'强制kill(cli-n)','强制kill会导致应用非正常退出，一般建议使用kill即可','medium','script','cli','[{\"name\": \"number\", \"operator\": \"in\", \"value\": [\"9\", \"15\"]}, {\"name\": \"pid\", \"operator\": \"set\"}]',3,1,'admin','2020-11-01 00:00:00',NULL,NULL),(14,'强制kill(cli-9/15)','强制kill会导致应用非正常退出，一般建议使用kill即可','medium','script','cli','[{\"name\": \"s_kill\", \"operator\": \"set\"}, {\"name\": \"pid\", \"operator\": \"set\"}]',3,1,'admin','2020-11-01 00:00:00',NULL,NULL),(15,'反弹shell(nc)','nc常见于反弹shell，用于远程命令执行','high','script','cli','[{\"name\": \"N/A\", \"operator\": \"notset\"}]',5,1,'admin','2020-11-01 00:00:00',NULL,NULL),(16,'反弹shell(socat)','socat常见于反弹shell，用于远程命令执行','high','script','cli','[{\"name\": \"N/A\", \"operator\": \"notset\"}]',6,1,'admin','2020-11-01 00:00:00',NULL,NULL),(17,'反弹shell(bash)','bash -i 常见于反弹shell，用于远程命令执行','high','script','cli','[{\"name\": \"interact\", \"operator\": \"set\"}, {\"name\": \"command\", \"operator\": \"ilike\", \"value\": \"/dev/tcp/\"}]',7,1,'admin','2020-11-01 00:00:00',NULL,NULL);
UNLOCK TABLES;

--
-- Table structure for table `service_script`
--

DROP TABLE IF EXISTS `service_script`;
CREATE TABLE `service_script` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `service` varchar(63) NOT NULL,
  `content_type` varchar(36) DEFAULT NULL,
  `content_field` varchar(63) DEFAULT NULL,
  `endpoint_field` varchar(63) DEFAULT NULL,
  `created_by` varchar(36) DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `updated_by` varchar(36) DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='serivce script extraction ';

--
-- Dumping data for table `service_script`
--

LOCK TABLES `service_script` WRITE;
UNLOCK TABLES;

--
-- Table structure for table `subject`
--

DROP TABLE IF EXISTS `subject`;
CREATE TABLE `subject` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(36) NOT NULL,
  `description` varchar(63) DEFAULT '',
  `enabled` tinyint(4) NOT NULL,
  `created_by` varchar(36) DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `updated_by` varchar(36) DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `subject`
--

LOCK TABLES `subject` WRITE;
INSERT INTO `subject` VALUES (1,'全部对象','任意对象范围',1,'admin','2020-11-01 00:00:00',NULL,NULL);
UNLOCK TABLES;

--
-- Table structure for table `subject_target`
--

DROP TABLE IF EXISTS `subject_target`;
CREATE TABLE `subject_target` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `subject_id` bigint(20) unsigned NOT NULL,
  `target_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fkey_subject_target_subject_id` (`subject_id`),
  KEY `fkey_subject_target_target_id` (`target_id`),
  CONSTRAINT `fkey_subject_target_subject_id` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fkey_subject_target_target_id` FOREIGN KEY (`target_id`) REFERENCES `target` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `subject_target`
--

LOCK TABLES `subject_target` WRITE;
INSERT INTO `subject_target` VALUES (1,1,1);
UNLOCK TABLES;

--
-- Table structure for table `target`
--

DROP TABLE IF EXISTS `target`;
CREATE TABLE `target` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(36) NOT NULL,
  `args_scope` varchar(512) DEFAULT NULL,
  `entity_scope` varchar(512) DEFAULT NULL,
  `enabled` tinyint(4) NOT NULL,
  `created_by` varchar(36) DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `updated_by` varchar(36) DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `target`
--

LOCK TABLES `target` WRITE;
INSERT INTO `target` VALUES (1,'任意对象','','',1,'admin','2020-11-01 00:00:00',NULL,NULL);
UNLOCK TABLES;

SET FOREIGN_KEY_CHECKS = 1;
-- Dump completed on 2020-11-23 17:08:28

#@v0.1.0.1-begin@;
UPDATE `rule` SET match_value='{force set ''''}{recursive set ''''}{help notset ''''}{version notset ''''}{path like ''*''}'
  WHERE id=1;
UPDATE `rule` SET match_value='{help notset ''''}'
  WHERE id=2;
UPDATE `rule` SET match_value='{force set ''''}{recursive set ''''}{help notset ''''}{version notset ''''}{path eq ''/''}'
  WHERE id=6;
UPDATE `rule` SET match_value='{name in [''KILL'', ''TERM'']}{pid set ''''}'
  WHERE id=12;
UPDATE `rule` SET match_value='{number in [''9'', ''15'']}{pid set ''''}'
  WHERE id=13;
UPDATE `rule` SET match_value='{s_kill set ''''}{pid set ''''}'
  WHERE id=14;
UPDATE `rule` SET match_value=''
  WHERE id=15;
UPDATE `rule` SET match_value=''
  WHERE id=16;
UPDATE `rule` SET match_value='{interact set ''''}{command ilike ''/dev/tcp/''}'
  WHERE id=17;

ALTER TABLE `service_script` ADD endpoint_include varchar(255) NULL;
ALTER TABLE `service_script` CHANGE endpoint_include endpoint_include varchar(255) NULL AFTER endpoint_field;

#@v0.1.0.1-end@;