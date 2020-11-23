# coding=utf-8
import pytest

from tests import box_data
from wecube_plugins_itsdangerous.common import reader

text_fulltext = r'''top # haha
cat > mytest.sh << EOF
$a123 ';' $me

# this is comment
ls|grep abc && date||tree;ps -ef|grep grep
ps \
-ef
'''

text_mix = '''var1=date
echo ${var1}
var2=`date`
echo $var2
cat > test.log << EOF
delete from `table_name` where id='1';
EOF'''


def test_reader_bash():
    expected = [
        ((1, 1), ['top']),
        ((2, 2), ['cat', '>', 'mytest.sh', '<<', 'EOF']),
        ((3, 3), ['$a123', ';', '$me']),
        ((4, 4), ['var=`date`']),
        ((6, 6), ['rm', '-rf', '/tmp/kkk/*']),
        ((7, 7), ['EOF']),
        ((8, 8), ['ls']),
        ((8, 8), ['grep', 'abc']),
        ((8, 8), ['date']),
        ((8, 8), ['tree']),
        ((8, 8), ['ps', '-ef']),
        ((8, 8), ['grep', 'grep']),
        ((9, 10), ['ps', '-ef']),
        ((11, 11), ['rm', '-r', '-f', '/tmp/abc']),
        ((12, 12), ['echo', '   -e 456']),
        ((13, 13), ['echo', '你好']),
        ((14, 14), ['echo', '$var']),
        ((14, 14), ['rm', '-rf', '/']),
        ((15, 15), ['echo', '$var']),
        ((16, 16), ['echo', '$var']),
        ((17, 17), ['echo', '12']),
        ((18, 18), ['kill', '-9', '123']),
        ((19, 19), ['kill', '-n', '9', '123']),
        ((20, 20), ['kill', '-s', 'TERM', '123']),
        ((21, 21), ['reboot']),
        ((22, 22), ['sysctl', '-p']),
    ]
    s = reader.ShellReader(box_data.script_shell)
    counter = 0
    for x in s.iter():
        assert x == expected[counter]
        counter += 1


def test_reader_bash_multiline():
    expected = [
        ((1, 1), ['ls', '-al']),
        ((2, 4), ['rm', '-rf', '/']),
        ((5, 9), ['rm', '-rf', '/']),
        ((10, 10), ['rm', ' ']),
        ((11, 11), ['-rf', ' ']),
        ((12, 12), ['/']),
        ((13, 15), ['rm', '\\\n-rf " \\\n/']),
        ((16, 18), ['rm', '-r', '-f', '/']),
        ((18, 18), ['ls', '-al']),
        ((19, 20), ['echo', 'Done']),
    ]
    s = reader.ShellReader(box_data.script_shell_multiline)
    counter = 0
    for x in s.iter():
        assert x == expected[counter]
        counter += 1


def test_reader_sql():
    expected = [
        ((1, 1), ['']),
        ((3, 3), ['']),
        ((3, 3), [';']),
        ((5, 5), ['select * from `box`']),
        ((5, 5), [';']),
        ((5, 5), ['select * from `target`;']),
        ((7, 7), ["update table_name set name='test' WhErE id='1';"]),
        ((8, 8), ["update table_name set name='test';"]),
        ((10, 12), ['']),
        ((14, 14), ['DROP TABLE IF EXISTS `box`;']),
        ((15, 15), ['']),
        ((15, 15), [';']),
        ((16, 16), ['']),
        ((16, 16), [';']),
        ((17, 28), [
            "CREATE TABLE `box` (`id` int(11) unsigned NOT NULL AUTO_INCREMENT, `name` varchar(36) NOT NULL, `description` varchar(63) DEFAULT '', `policy_id` int(11) unsigned NOT NULL, `subject_id` int(11) unsigned NOT NULL, PRIMARY KEY (`id`), KEY `fkey_box_policy_id` (`policy_id`), KEY `fkey_box_subject_id` (`subject_id`), CONSTRAINT `fkey_box_policy_id` FOREIGN KEY (`policy_id`) REFERENCES `policy` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION, CONSTRAINT `fkey_box_subject_id` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        ]),
        ((29, 29), ['']),
        ((29, 29), [';']),
        ((31, 31), ['']),
    ]
    s = reader.SqlReader(box_data.script_sql)
    counter = 0
    for x in s.iter():
        assert x == expected[counter]
        counter += 1


def test_reader_line():
    expected = [
        ((1, 1), ['top # haha']),
        ((2, 2), ['cat > mytest.sh << EOF']),
        ((3, 3), ["$a123 ';' $me"]),
        ((4, 4), ['']),
        ((5, 5), ['# this is comment']),
        ((6, 6), ['ls|grep abc && date||tree;ps -ef|grep grep']),
        ((7, 7), ['ps \\']),
        ((8, 8), ['-ef']),
    ]
    s = reader.LineReader(text_fulltext)
    counter = 0
    for x in s.iter():
        assert x == expected[counter]
        counter += 1


def test_reader_fulltext():
    expected = [((1, 9), [
        "top # haha\ncat > mytest.sh << EOF\n$a123 ';' $me\n\n# this is comment\nls|grep abc && date||tree;ps -ef|grep grep\nps \\\n-ef\n"
    ])]
    s = reader.FullTextReader(text_fulltext)
    counter = 0
    for x in s.iter():
        assert x == expected[counter]
        counter += 1


def test_reader_guess():
    assert reader.guess(box_data.script_shell) == 'shell'
    assert reader.guess(box_data.script_sql) == 'sql'
    assert reader.guess(text_fulltext) == 'shell'
    assert reader.guess(text_mix) == 'shell'
    assert reader.guess('docker run -it 44fc0f0582d9') == 'shell'
    assert reader.guess('docker attach 44fc0f0582d9') is None
