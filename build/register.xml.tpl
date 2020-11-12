<?xml version="1.0" encoding="UTF-8"?>
<package name="itsdangerous" version="{{PLUGIN_VERSION}}">
    <!-- 1.依赖分析 - 描述运行本插件包需要的其他插件包 -->
    <packageDependencies>
        <packageDependency name="platform" version="v2.6.1" />
    </packageDependencies>

    <!-- 2.菜单注入 - 描述运行本插件包需要注入的菜单 -->
    <menus>
        <menu code='ADMIN_ITS_DANGEROUS_CONFIG' cat='ADMIN' displayName="Its Dangerous Config" localDisplayName="高危规则配置">/dangerousIndex</menu>
    </menus>

    <!-- 3.数据模型 - 描述本插件包的数据模型,并且描述和Framework数据模型的关系 -->
    <dataModel></dataModel>

    <!-- 4.系统参数 - 描述运行本插件包需要的系统参数 -->
    <systemParameters></systemParameters>

    <!-- 5.权限设定 -->
    <authorities>
        <authority systemRoleName="SUPER_ADMIN" >
            <menu code="ADMIN_ITS_DANGEROUS_CONFIG" />
        </authority >
    </authorities>

    <!-- 6.运行资源 - 描述部署运行本插件包需要的基础资源(如主机、虚拟机、容器、数据库等) -->
    <resourceDependencies>
        <docker imageName="{{IMAGENAME}}" containerName="{{CONTAINERNAME}}" 
        portBindings="{{ALLOCATE_PORT}}:9000" 
        volumeBindings="/etc/localtime:/etc/localtime,{{BASE_MOUNT_PATH}}/itsdangerous/logs:/var/log/itsdangerous,{{BASE_MOUNT_PATH}}/certs:/certs" 
        envVariables="ITSDANGEROUS_DB_USERNAME={{DB_USER}},ITSDANGEROUS_DB_PASSWORD={{DB_PWD}},
        ITSDANGEROUS_DB_HOSTIP={{DB_HOST}},ITSDANGEROUS_DB_HOSTPORT={{DB_PORT}},ITSDANGEROUS_DB_SCHEMA={{DB_SCHEMA}},
        GATEWAY_URL={{GATEWAY_URL}},JWT_SIGNING_KEY={{JWT_SIGNING_KEY}},
        WECUBE_S3_ACCESS_KEY={{S3_ACCESS_KEY}},WECUBE_S3_SECRET_KEY={{S3_SECRET_KEY}}" />
        <mysql schema="itsdangerous" initFileName="init.sql" upgradeFileName="upgrade.sql" />
    </resourceDependencies>

    <!-- 7.插件列表 - 描述插件包中单个插件的输入和输出 -->
    <plugins></plugins>
</package>
