# Itsdangerous插件
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![](https://img.shields.io/badge/language-python-orang.svg)



## 简介

Itsdangerous插件可以对shell & sql 脚本进行命令检测，根据既定的规则发现高危命令并提示用户。



## 概念说明

调用参数：一个命令或者一次检测中的参数

规则：数据的检测明细动作，比如对脚本检测 或 输入参数json字段进行检测，使用正则 或 调用参数 进行匹配

策略：规则的集合

目标对象：定义规则/策略将作用于的对象范围，对象可以使用 输入参数json特定字段值，或wecube模型定位表达式 来表述

角色：对象的集合

试盒：将策略和角色关联，以对调用的行为进行高危检测

插件参数：定义插件最佳实践服务所对应的脚本提取字段，支持内容字段，以及物料插件地址/S3地址压缩包自动提取

高危检测：针对要执行的插件参数及模型实例，进行目标对象范围界定，若符合则使用其规则进行脚本内容的检测。



## 痛点解决

命令检测通常围绕正则表达式进行，这个方法非常通用但并不有效，比如：

在bash中，rm命令是常见需要注意的命令，由于每个人的使用习惯不一致，rm的写法各式各样

```bash
rm -rf /tmp/*
rm -r -f /tmp/* && rm -f -r /tmp/* && rm -rf '/tmp/*' && rm '-rf' '/tmp/*' 
rm --force -r /tmp/*
rm --force -R /tmp/*
rm \
-rf \
/tmp/*
```

以上仅是一些常见的写法，如果使用正则解析，会存在命令参数组合，引号问题，再加上多行命令等情况，正则会变得异常复杂

同样的在sql语句中，除了常见的大小写，还存在着多行，注释混插，\`表名\`等多种表达方式

```mysql
SELECT * FROM `box`;DROP/*???*/ TABLE IF EXISTS `box`;
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

```



Itsdangerous插件中针对以上的场景进行了优化：

为bash增加了一个**shell命令解析器** + **命令行模拟器** 来进行数据分析，简化了高危规则的表达

shell命令解析器： input - rm '-rf' '/tmp/*'      =>      命令行模拟器： command = rm，force=True， recursive=True， path=/tmp/\*

为sql增加了一个**sql格式化工具**，自动进行sql语句的切分&格式化，正则表达式只需要写^drop\s+table\s+.*$即可

sql语句的切分&格式化输出： 
    SELECT * FROM \`box\`   
    DROP TABLE IF EXISTS \`box\`
    ...

> 当然在Itsdangerous插件中，也支持对不经任何处理的原数据进行按行(text)/多行(fulltext)方式进行正则匹配，以满足更多的通用自定义检测场景。
>
> 主要支持2类检测器
>
> script检测器
> |
> |-----------------------------|----------------|-------------------------------------|
> |                                    |                    |                                              |
> cli(for shell script)       sql                 text(for line match)              fulltext(for multi-line)
>
> 
>
> param检测器
> |
> |
> | 
> filter(for any json data)

当在wecube中执行插件时，用户可以根据自己已有的插件最佳实践配置脚本字段或脚本地址字段，itsdangerous插件会提取脚本内容进行解压/检测。

比如：saltstack/host-script(host)/run-custom-script插件实践中，用户会提供scriptContent字段，字段值为shell脚本



## 反馈

如果您遇到问题，请给我们提[Issue](https://github.com/WeBankPartners/wecube-plugins-itsdangerous/issues/new/choose)，我们会第一时间反馈。