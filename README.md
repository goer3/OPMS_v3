# OPMS_v3（该项目是自己以前学 Python 时候写的，现在学 Go 了，已经停止维护）


### 说明

由于之前的 OPMS (姑且称作 v2 版本，因为 v1 版本太简单了就没分享出来)通用性其实不大，在换了新公司之后开始着手 OPMS v3 的开发

其实功能大致相同，这一次主要的更改还是进一步优化了页面的兼容性，优化了页面的显示效果，看起来舒服一些，删除了以前一些乱七八糟无用的东西

从过去从事运维工作的经验中总结了一些运维的需求，将其做成 WEB 版本，使运维工作平台化，尽量摆脱运维文档，记录 Excel，word 文档化

由于目前还处于开发阶段，很多功能还没做，目前先暂且就不上传了

先给一些效果图，有兴趣的可以看下，说不定我哪天就更新了！

### 效果图

【0】主页：

![enter description here](https://github.com/PythonTra1nee/OPMS_v3/blob/master/display/index.jpg?raw=true)

【1】用户管理：

![enter description here](https://github.com/PythonTra1nee/OPMS_v3/blob/master/display/userinfo.jpg?raw=true)


【2】主机管理：

![enter description here](https://github.com/PythonTra1nee/OPMS_v3/blob/master/display/host.jpg?raw=true)

![enter description here](https://github.com/PythonTra1nee/OPMS_v3/blob/master/display/hostinfo.jpg?raw=true)

![enter description here](https://github.com/PythonTra1nee/OPMS_v3/blob/master/display/dbinfo.jpg?raw=true)

![enter description here](https://github.com/PythonTra1nee/OPMS_v3/blob/master/display/webssh.jpg?raw=true)


【3】故障和消息：

![enter description here](https://github.com/PythonTra1nee/OPMS_v3/blob/master/display/guzhang.jpg?raw=true)

![enter description here](https://github.com/PythonTra1nee/OPMS_v3/blob/master/display/message.jpg?raw=true)


### 部署方法


#### 环境安装

系统 CentOS 6 或者 7


#### 下载 Python

```bash
https://www.python.org/ftp/python/3.6.2/Python-3.6.2.tar.xz
```


#### 放到服务器上面编译安装

```bash
yum -y install zlib-devel bzip2-devel wget openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make
cd /usr/local/src
xz -d Python-3.6.2.tar.xz
tar -xf Python-3.6.2.tar
cd Python-3.6.2
./configure --prefix=/usr/local/python-36 --enable-shared CFLAGS=-fPIC
make && make install
```


#### 添加环境变量

```bash
echo 'export PATH=$PATH:/usr/local/python-36/bin' >> /etc/profile
source /etc/profile
```


#### 替换旧版本

```bash
mv /usr/bin/python /tmp
ln -s /usr/local/python-36/bin/python3.6 /usr/bin/python
```


#### 修改 yum

```bash
vim /usr/bin/yum
```


#### 把第一行用的 Python 换成本机 /usr/bin 下面 python2.* （CentOS 6 和 7 带的 Python 版本不同）

#### 修改库文件

```bash
cp /usr/local/python-36/lib/libpython3.6m.so.1.0 /usr/lib64/
```


#### 查看当前版本

```bash
python -V
```

#### 服务配置

#### 新建目录，上传 opms 到该目录下
```bash
mkdir -p /opt/opms_website
```

#### 修改 /opt/opms_website/opms/opms/settings.py 中的个人配置

* 数据库配置

* 系统发送邮件邮箱配置，需要一个开启 SMTP 的邮箱地址

* 系统地址配置：

    * SERVER_URL：系统运行之后的访问地址
    * WEBSSH_IP：远程终端的服务地址，这里其实是本机的 IP地址
    * WEBSSH_PORT：不需要修改，如果真的要改，需要修改 extra_apps/webssh/main.py 中的端口，改为一致

 
* 高德地图和城市：

    * GAODE_API_KEY：需要去高德地址开发者中心创建一个 KEY，很容易，这里用于首页的天气功能
    * CITY_ID：默认的城市 ID，在内网访问的时候提供城市天气支持


* 开发者邮箱 DEVELPER_EMAIL_ADDRESS，默认为我得，首页反馈功能发送的消息最终发送给谁


#### 安装依赖

```bash
cd /opt/opms_website/opms
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```


#### 同步数据库

```bash
python manage.py makemigrations
python manage.py migrate
```


#### 创建超级用户，根据提示创建

```bash
python manage.py createsuperuser
```


#### 安装环境

```bash
pip3 install uwsgi
```


#### 创建文件，添加配置：/etc/uwsgi.ini

```bash
[uwsgi]
//运行端口号
socket = 127.0.0.1:9090
//主进程
master = true
//多站模式
vhost = true
//多站模式时不设置入口模块和文件
no-stie = true
//子进程数
workers = 2
reload-mercy = 10
//退出、重启时清理文件 
vacuum = true
max-requests = 1000   
limit-as = 512
buffer-sizi = 30000
//pid文件，用于下面的脚本启动、停止该进程
pidfile = /var/run/uwsgi.pid
daemonize = /var/log/uwsgi.log
```


#### 创建启动脚本:/etc/init.d/uwsgi

```bash
#!/bin/bash

NAME='uwsgi'
DAEMON='uwsgi'
CONFIGFILE="/etc/$NAME.ini"
PIDFILE="/var/run/$NAME.pid"
SCRIPTNAME="/etc/init.d/$NAME"
   
do_start() {
$DAEMON $CONFIGFILE || echo -n "uwsgi  running" 
}

do_stop() {
    $DAEMON --stop $PIDFILE || echo -n "uwsgi not running"
    rm -f $PIDFILE
    echo "$DAEMON STOPED."
}

do_reload() {
    $DAEMON --reload $PIDFILE || echo -n "uwsgi can't reload"
}

do_status() {
    ps aux|grep $DAEMON
}

case "$1" in
status)
    echo -en "Status $NAME: \n"
    do_status
;;
start)
    echo -en "Starting $NAME: \n"
    do_start
;;
stop)
    echo -en "Stopping $NAME: \n"
    do_stop
;; 
reload|graceful)
    echo -en "Reloading $NAME: \n"
    do_reload
;;
*)
    echo "Usage: $SCRIPTNAME {start|stop|reload}" >&2
    exit 3
;;
esac
exit 0
```


#### 创建 nginx 虚拟主机

```bash
server {
    # 设置网站运行端口
    listen       10000;
    server_name  localhost;
   
    location / {
        include  uwsgi_params;
        # 必须和uwsgi中的设置一致
        uwsgi_pass  127.0.0.1:9090;
        # 入口文件，即wsgi.py相对于项目根目录的位置，“.”相当于一   层目录
        uwsgi_param UWSGI_SCRIPT opms.wsgi;
        # 项目根目录
        uwsgi_param UWSGI_CHDIR /opt/opms_website/opms;
        index  index.html index.htm;
        client_max_body_size 35m;
    }
    # 静态文件目录
    location /static/ {
        alias  /opt/opms_website/opms/static/;
        index  index.html index.htm;
    }
}
```


#### 启动服务

```bash
/etc/init.d/uwsgi start
```


#### 启动 nginx


#### 启动 main.py

```bash
python /opt/opms_website/opms/extra_apps/webssh/main.py & >/dev/null
```

#### 用之前创建的用户登录后台
```bash
http://xxxx:10000/admin
```

#### 初始化

* 找到公司表，添加公司
* 然后部门表添加部门
* 然后职位表，添加职位
* 最后找到用户表，完善当前用户的一些用户信息

#### 初始化平台
找到平台表，添加你们公司用到的一些平台，如 zabbix，jenkins 等，logo 路径为 opms/media/platform-management/logo 下面
添加时候，如 zabbix logo 只需要写 platform-management/logo/zabbix.png 即可


#### 服务正常使用
http://xxxx:10000








