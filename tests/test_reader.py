# coding=utf-8
import pytest

from wecube_plugins_itsdangerous.common import reader


def test_reader_bash():
    t = r'''top # haha
cat > mytest.sh << EOF
$a123 ';' $me

# this is comment
rm -rf /tmp/kkk/*;
EOF
ls|grep abc && date||tree;ps -ef|grep grep
ps \
-ef
rm "-r" '-'f /tmp/abc
echo '   -e 456' #-ef
echo 你好
echo $var
echo '$var'
echo "$var"
echo \1\2 #-ef
'''
    expected = [
        (1, ['top']),
        (2, ['cat', '>', 'mytest.sh', '<<', 'EOF']),
        (3, ['$a123', ';', '$me']),
        (6, ['rm', '-rf', '/tmp/kkk/*']),
        (7, ['EOF']),
        (8, ['ls']),
        (8, ['grep', 'abc']),
        (8, ['date']),
        (8, ['tree']),
        (8, ['ps', '-ef']),
        (8, ['grep', 'grep']),
        (9, ['ps', '\n-ef']),
        (11, ['rm', '-r', '-f', '/tmp/abc']),
        (12, ['echo', '   -e 456']),
        (13, ['echo', '你好']),
        (14, ['echo', '$var']),
        (15, ['echo', '$var']),
        (16, ['echo', '$var']),
        (17, ['echo', '12']),
        ]
    s = reader.ShellReader(t)
    counter = 0
    for x in s.iter():
        assert x == expected[counter]
        counter += 1


def test_reader_sql():
    t = r'''-- MySQL dump 10.16  Distrib 10.1.44-MariaDB, for debian-linux-gnu (x86_64)

/*!40101 SET NAMES utf8 */;

select * from `box`/* cccccccc */;/* cccccccc */select * from `target`;

update table_name set name='test' WhErE id='1';
update table_name set name='test';

--
-- Table structure for table `box`
--

DROP TABLE IF EXISTS `box`;       
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

-- Dump completed on 2020-07-14 15:47:51
'''
    expected = [
        (2, ['']),
        (3, ['']),
        (3, [';']),
        (5, ['select * from `box`']),
        (5, [';']),
        (5, ['select * from `target`;']),
        (7, ["update table_name set name='test' WhErE id='1';"]),
        (8, ["update table_name set name='test';"]),
        (13, ['']),
        (14, ['DROP TABLE IF EXISTS `box`;']),
        (15, ['']),
        (15, [';']),
        (16, ['']),
        (16, [';']),
        (28, ["CREATE TABLE `box` (`id` int(11) unsigned NOT NULL AUTO_INCREMENT, `name` varchar(36) NOT NULL, `description` varchar(63) DEFAULT '', `policy_id` int(11) unsigned NOT NULL, `subject_id` int(11) unsigned NOT NULL, PRIMARY KEY (`id`), KEY `fkey_box_policy_id` (`policy_id`), KEY `fkey_box_subject_id` (`subject_id`), CONSTRAINT `fkey_box_policy_id` FOREIGN KEY (`policy_id`) REFERENCES `policy` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION, CONSTRAINT `fkey_box_subject_id` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION) ENGINE=InnoDB DEFAULT CHARSET=utf8;"]),
        (29, ['']),
        (29, [';']),
        (31, ['']),
        ]
    s = reader.SqlReader(t)
    counter = 0
    for x in s.iter():
        assert x == expected[counter]
        counter += 1


def test_reader_line():
    t = r'''top # haha
cat > mytest.sh << EOF
$a123 ';' $me

# this is comment
ls|grep abc && date||tree;ps -ef|grep grep
ps \
-ef
'''
    expected = [
        (1, ['top # haha']),
        (2, ['cat > mytest.sh << EOF']),
        (3, ["$a123 ';' $me"]),
        (4, ['']),
        (5, ['# this is comment']),
        (6, ['ls|grep abc && date||tree;ps -ef|grep grep']),
        (7, ['ps \\']),
        (8, ['-ef']),
        ]
    s = reader.LineReader(t)
    counter = 0
    for x in s.iter():
        assert x == expected[counter]
        counter += 1


def test_reader_fulltext():
    t = r'''top # haha
cat > mytest.sh << EOF
$a123 ';' $me

# this is comment
ls|grep abc && date||tree;ps -ef|grep grep
ps \
-ef
'''
    expected = [
        (1, ["top # haha\ncat > mytest.sh << EOF\n$a123 ';' $me\n\n# this is comment\nls|grep abc && date||tree;ps -ef|grep grep\nps \\\n-ef\n"])
        ]
    s = reader.FullTextReader(t)
    counter = 0
    for x in s.iter():
        assert x == expected[counter]
        counter += 1
