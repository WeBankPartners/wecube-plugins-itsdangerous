SET NAMES utf8 ;
/* rule */
INSERT INTO `rule` (name,description,`level`,effect_on,match_type,match_value,match_param_id,enabled,created_by,created_time,updated_by,updated_time) VALUES
	 ('qcloud销毁主机','调用qcloud API进行主机销毁','critical','param','filter','{serviceName eq ''qcloud/vm(resource)/terminate''}',NULL,1,'admin','2020-11-01 00:00:00.0',NULL,NULL);
INSERT INTO `rule` (name,description,`level`,effect_on,match_type,match_value,match_param_id,enabled,created_by,created_time,updated_by,updated_time) VALUES
	 ('saltstack删除数据库','调用saltstack API进行数据库删除','critical','param','filter','{serviceName eq ''saltstack/mysql-database(db_deploy)/delete''}',NULL,1,'admin','2020-11-01 00:00:00.0',NULL,NULL);


/* service_script */
INSERT INTO `service_script` (service,content_type,content_field,endpoint_field,created_by,created_time,updated_by,updated_time) VALUES
	 ('saltstack/apply-deployment(app_deploy)/new','','','endpoint','admin','2020-11-01 00:00:00.0',NULL,NULL);
INSERT INTO `service_script` (service,content_type,content_field,endpoint_field,created_by,created_time,updated_by,updated_time) VALUES
	 ('saltstack/apply-deployment(app_deploy)/update','','','endpoint','admin','2020-11-01 00:00:00.0',NULL,NULL);
INSERT INTO `service_script` (service,content_type,content_field,endpoint_field,created_by,created_time,updated_by,updated_time) VALUES
	 ('saltstack/host-file(app_deploy)/copy','','','endpoint','admin','2020-11-01 00:00:00.0',NULL,NULL);
INSERT INTO `service_script` (service,content_type,content_field,endpoint_field,created_by,created_time,updated_by,updated_time) VALUES
	 ('saltstack/mysql-script(db_deploy)/run-deploy-script','','','endpoint','admin','2020-11-01 00:00:00.0',NULL,NULL);
INSERT INTO `service_script` (service,content_type,content_field,endpoint_field,created_by,created_time,updated_by,updated_time) VALUES
	 ('saltstack/mysql-script(db_deploy)/run-rollback-script','','','endpoint','admin','2020-11-01 00:00:00.0',NULL,NULL);
INSERT INTO `service_script` (service,content_type,content_field,endpoint_field,created_by,created_time,updated_by,updated_time) VALUES
	 ('saltstack/mysql-script(db_deploy)/run-upgrade-script','','','endpoint','admin','2020-11-01 00:00:00.0',NULL,NULL);
INSERT INTO `service_script` (service,content_type,content_field,endpoint_field,created_by,created_time,updated_by,updated_time) VALUES
	 ('saltstack/host-script(host)/run-custom-script','shell','scriptContent','','admin','2020-11-01 00:00:00.0',NULL,NULL);
INSERT INTO `service_script` (service,content_type,content_field,endpoint_field,created_by,created_time,updated_by,updated_time) VALUES
	 ('saltstack/host-script(host)/run-init-script','shell','scriptContent','','admin','2020-11-01 00:00:00.0',NULL,NULL);