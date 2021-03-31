SET NAMES utf8 ;
/* rule */
INSERT INTO `rule` (name,description,`level`,effect_on,match_type,match_value,match_param_id,enabled,created_by,created_time,updated_by,updated_time) VALUES
	 ('qcloud销毁主机','调用qcloud API进行主机销毁','critical','param','filter','{serviceName eq ''qcloud/vm(resource)/terminate''}',NULL,1,'admin','2020-11-01 00:00:00.0',NULL,NULL);
INSERT INTO `rule` (name,description,`level`,effect_on,match_type,match_value,match_param_id,enabled,created_by,created_time,updated_by,updated_time) VALUES
	 ('saltstack删除数据库','调用saltstack API进行数据库删除','critical','param','filter','{serviceName eq ''saltstack/mysql-database(db_deploy)/delete''}',NULL,1,'admin','2020-11-01 00:00:00.0',NULL,NULL);


/* service_script */
INSERT INTO `service_script` (service,content_type,content_field,endpoint_field,endpoint_include,created_by,created_time,updated_by,updated_time) VALUES
	 ('saltstack/apply-deployment(app_deploy)/new','shell','','endpoint','startScript','admin','2020-11-01 00:00:00.0','admin','2021-02-01 00:00:00.0'),
	 ('saltstack/apply-deployment(app_deploy)/update','shell','','endpoint','startScript|stopScript','admin','2020-11-01 00:00:00.0','admin','2021-02-01 00:00:00.0'),
	 ('saltstack/host-file(app_deploy)/copy','','','endpoint',NULL,'admin','2020-11-01 00:00:00.0',NULL,NULL),
	 ('saltstack/mysql-script(db_deploy)/run-deploy-script','sql','','endpoint','sql_files','admin','2020-11-01 00:00:00.0','admin','2021-02-01 00:00:00.0'),
	 ('saltstack/mysql-script(db_deploy)/run-rollback-script','sql','','endpoint','sql_files','admin','2020-11-01 00:00:00.0','admin','2021-02-01 00:00:00.0'),
	 ('saltstack/mysql-script(db_deploy)/run-upgrade-script','sql','','endpoint','sql_files','admin','2020-11-01 00:00:00.0','admin','2021-02-01 00:00:00.0'),
	 ('saltstack/host-script(host)/run-custom-script','shell','scriptContent','',NULL,'admin','2020-11-01 00:00:00.0',NULL,NULL),
	 ('saltstack/host-script(host)/run-init-script','shell','scriptContent','',NULL,'admin','2020-11-01 00:00:00.0',NULL,NULL);