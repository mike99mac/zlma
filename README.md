# z/VM and Linux Modern Administration 
z/VM and Linux Modern Administration (**zlma**, pronounced "zelma") enables Linux servers running under the z/VM hypervisor on IBM Mainframes to be managed in a more modern fashion. The priority of how servers are managed is:

1. Browser-based
1. Linux command line
1. 3270 ("green screen")

It consists of four main components:
- A relational database 
  - Containing pertinent up-to-date data about Linux servers on z
- Web browser interfaces
  - ``finder`` - view all z/VM and Linux data with search capabilities
  - ``consolez`` - view z/VM console data 
- Linux line commands
  - ``zlma`` - manage DB of zLinux data 
  - ``vif`` - manage many aspects of z/VM
- A RESTful API 
  - So other apps can get to the data

# Overview
Following is a block diagram of zlma:

![](zlma-block-diagram.png) 

**zlma block diagram**

## Set up SSH access
Key-based authentication, or *Passwordless* SSH access is needed for one user from the zlma server to all systems that will be managed.  ``zlma`` commands must be run by that user and they must have ``sudo`` access.  

Details on how to accomplish this are outside the scope of this document, howerver, there is a script, ``sshall``, which tests SSH connectivity: https://github.com/mike99mac/zlma/blob/main/usr/local/sbin/sshall

Once SSH access is set up, the solution can be installed. 

# Installation
These steps set up a virtual environment under ``/srv/venv``. The python files reference this directory. 

This code has been installed on Debian and RHEL bases Linuxes.  When there are differences, separate steps are given for each.

To install zlma, perform the following steps.

## Update your system
To uUpdate your system, perform the following:

  - For Debian-based:
    ```
    sudo apt update 
    ```

    ```
    sudo apt upgrade -y
    ```

  - For RHEL-based:
    ```
    sudo dnf update 
    ```

## Install this repository
To install this ``zlma`` repository, some basic packages are first needed.

- Allow members of a certain group to be able to run **``sudo``** commands without a password, by adding **``NOPASSWD:``** to the line near the bottom of the file.

    ```
    sudo visudo
    ```

    - For Debian-based, it is the ``sudo`` group:
      ```
      ...
      %sudo   ALL=(ALL:ALL) NOPASSWD: ALL
      ...
      ```

    - For RHEL-based, it is the ``wheel`` group:
      ```
      ...
      %wheel  ALL=(ALL:ALL) NOPASSWD: ALL
      ...
      ```

- Install git, httpd and vim:

  - For Debian-based:

    ```
    sudo apt install -y git apache2 vim
    ```

  - For RHEL-based:

    ```
    sudo dnf install -y git httpd vim
    ```

- Clone this repo to your home directory:

```
cd;
git clone https://github.com/mike99mac/zlma
```
- Login as a non-root user with sudo privileges. Add the group which will be running apache to that user.  
  In this exmple the user is ``youruser`` and the group is ``apache``, which is common for Red Hat-based distros. For Debian, the group ``www-data`` is common.

```
sudo usermod -aG <apache|www-data> <youruser>
```

- Use the ``su -`` command to start a new shell which will reflect the group added 
su - youruser
id
uid=1000(youruser) gid=1000(youruser) groups=1000(youruser),48(apache)
```


## Upgrade Python

This step is optional.  

Python must be at level 3.10 or greater because zlma code uses ``match/case`` statements which are not supported in Python 3.9 or earlier. AlmaLinux 9.4 (the distro often used to write this document) ships with a base Python version of 3.9 which will not run this code.

To install Python 3.11 on a RHEL based distro, perform the following steps.

- Install Python 3.11

```
sudo dnf install python3.11 python3.11-devel
```

- Show the new version:

```
python3.11 -V
Python 3.11.7
```

If you need to use Python 3.11, it will be specified later.


## Choose manual install or install script
Choose either to install manually or use the install script (recommended).

### Install automatically
The script ``instzlma`` is provided in the ``zlma`` repo to save you time. 


- Change to the new zlma directory:

```
cd $HOME/zlma;
```

    - To run it if your Linux has a base Python version of 3.10 or greater, perform the following steps:

    ```
    ./instzlma 
    ```

    -To run it if your system has an upgraded python, include the upgraded version as an argument to ``instzlma``:

    ```
    ./instzlma python3.11
    ```

The output will be written to your home directory in a file of the form ``<yr-mon-day-hr-min-sec>-instzlma.out``.
### Install manually
If you want to use the install script to save time, skip this section and [go to Install automatically](#Install-automatically).

To install zlma and co-req packages, perform the following steps.

- Install co-requisite packages.

  - For Debian-based:
    ```
    sudo apache apt install cifs-utils curl gcc git libmariadb3 libmariadb-dev make mariadb-server mlocate net-tools pandoc python3 python3-dev python3-pip 
    ```

  - For RHEL-based:
    ```
    sudo dnf install bzip2-devel cifs-utils curl gcc git httpd libffi-devel make mariadb-server mlocate net-tools openssl-devel python3 python3-devel python3-pip vim wget zlib-devel
    ```

- Set Apache to start at boot time: 

  - For Debian-based:
    ```
    sudo systemctl enable apache2
    ```

  - For RHEL-based:

    ```
    sudo systemctl enable httpd
    ```

- Create a directory for zlma to log to:

```
sudo mkdir /var/log/zlma
```

- Change the group of that directory to the group that Apache runs as.
 
  - For Debian based:
    ```
    sudo chgrp www-data /var/log/zlma
    ```

  - For RHEL based:
    ```
    sudo chgrp apache /var/log/zlma
    ```

- Set the group write bit of the new directory:

```
sudo chmod g+w /var/log/zlma
```

- Set mariadb to start at boot time:

```
sudo systemctl enable mariadb
```

- Start mariadb.

```
sudo systemctl start mariadb
```


### Set mariadb root password
The install script does not set the mariadb root password, so this step must be performed manually.

- Set the mariadb root password. This must be the same user and password as in ``/etc/mariadb.conf``. Enter the MariaDB command-line tool:

```
sudo mariadb
```

- From there, change the root password, then leave the session: 

```
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
exit
```

## Create a virtual environment
Now that the co-requisites are satisfied, the virtual environment can be created with the following steps:

- Change to the ``/srv/`` directory:

```
cd /srv
```

- Create a virtual environment in one of two ways:
  - where the base Python version is 3.10 or greater:

    ```
    sudo python3 -m venv venv
    ```

  - Where Python 3.11 was added:

    ```
    sudo python3.11 -m venv venv
    ```

- Recursively change the group of the new virtual environment.

  - For Debian-based:
    ```
    sudo chgrp -R www-data venv
    ```

  - For RHEL-based:
    ```
    sudo chgrp -R apache venv
    ```

- Recursively add group write permissions to the new virtual environment:

```
sudo chmod -R g+w venv
```

- Activate the environment which the current user will now be able to write to with group privileges:

```
. venv/bin/activate
```

You should see the text ``(venv)`` prefixed on the command prompt.

- Upgrade pip:

  - On systems where the base Python version is 3.10 or greater:

    ```
    /srv/venv/bin/python3 -m pip install --upgrade pip
    ```

  - On systems where Python 3.11 was added:

    ```
    /srv/venv/bin/python3.11 -m pip install --upgrade pip
    ```

- Install Mariadb, the Python connector and the Lex-Yacc library:

```
python3 -m pip install mariadb mysql-connector-python ply
```

- Issue the following command and answer the many security questions:
```
mysql_secure_installation
```

For reference, 
```
# cat /etc/apache2/sites-available/zlma.conf
```
{
  "db_user":        "root",
  "db_pw":          "pi",
  "db_host":        "127.0.0.1",
  "db_name":        "zlma",
  "home_dir":       "/home/youruser",
  "log_level":      "debug",
  "user_directory": "vmsecure"
}
```
#
# zlma configuration file
#
For reference, following is an Apache configuration file for a **Debian-based Linux**:

```
User pi
Group pi
<VirtualHost *:80>
  ServerAdmin mmacisaac@example.com 
  DocumentRoot /srv/www/zlma
  ServerName model1500
  LogLevel error
  LoadModule cgi_module /usr/lib/apache2/modules/mod_cgi.so

  <Directory "/srv/www/html">
    Options Indexes FollowSymLinks
    AllowOverride all
    Require all granted
  </Directory>

  <Directory /srv/www/zlma>
    Options +ExecCGI
    DirectoryIndex restapi.py
    Require all granted
  </Directory>
  AddHandler cgi-script .py

  ErrorLog ${APACHE_LOG_DIR}/error.log
  CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

- Following is an Apache configuration file for a **RHEL-based Linux**: 

```
# cat /etc/httpd/conf/httpd.conf
```
#
# Apache configuration file for zlma
#
Include conf.modules.d/*.conf
User apache
Group apache
ServerName your.server.fqdn
ServerRoot /etc/httpd
Listen *:80
ServerAdmin admin@example.com
DocumentRoot /srv/www/zlma
LogLevel error

<Directory "/srv/www/html">
  Options Indexes FollowSymLinks
  AllowOverride all
  Require all granted
</Directory>

# Read-Only queries do not require credentials
AddHandler cgi-script .py
Alias /zlma /srv/www/zlma
<Directory /srv/www/zlma>
  Options +ExecCGI
  Require all granted
</Directory>

# Read-Write operations require credentials
ScriptAlias /zlmarw/ /srv/www/zlmarw/
<Directory /srv/www/zlmarw/>
  AllowOverride None
  Options +ExecCGI -Includes
  AuthType Basic
  AuthName "zlma - Enter password"
  AuthType Basic
  AuthName "Restricted Access"
  AuthUserFile /srv/www/zlmarw/.htpasswd
  Require valid-user
  # Replace above if using LDAP
  # AuthBasicProvider ldap
  # AuthLDAPURL ldap://<your.orgs.ldap.server:389/ou=people,ou=linux_systems,dc=example,dc=com?uid
  # Require ldap-filter objectClass=posixAccount
</Directory>

ErrorLog /var/log/httpd/error.log
CustomLog /var/log/httpd/access.log combined
```

- Enable the site for Debian-based Linuxes:

```
sudo a2ensite zlma.conf
```

- Following is the systemd ``service`` file. 

```
cat /etc/systemd/system/apache2.service
```

```
[Unit]
Description=The Apache HTTP Server
After=network.target remote-fs.target nss-lookup.target
Documentation=https://httpd.apache.org/docs/2.4/

[Service]
Type=forking
Environment=APACHE_STARTED_BY_SYSTEMD=true
ExecStartPre=/usr/local/sbin/mklogdir
ExecStart=/usr/sbin/apachectl start
ExecStop=/usr/sbin/apachectl graceful-stop
ExecReload=/usr/sbin/apachectl graceful
KillMode=mixed
PrivateTmp=true
Restart=on-abort

[Install]
WantedBy=multi-user.target
```

- Set Apache to start at boot time and start it in the current environment. 

  - For Debian-based:

    ```
    sudo systemctl enable apache2
    ```

    ```
    sudo systemctl start apache2
    ```

  - For RHEL-based:

    ```
    sudo systemctl enable httpd
    ```

    ```
    sudo systemctl start httpd
    ```

## Create a configuration file
The zlma configuration file allows you to set local values such as the database credentials, the home directory and the logging level.

There is a sample configuration file named ``zlma.conf`` in the repo.  The code expects it to be in ``/etc/``.

- Copy it to ``/etc/``:

```
sudo cp ~/zlma/zlma.conf /etc
```

- Modify the values if desired. Set the root password to the value used earlier in mariadb.

```
sudo vi /etc/zlma.conf
{
  "DBuser": "root",
  "DBpw": "pi",
  "DBhost": "127.0.0.1",
  "DBname": "cmdb",
  "homeDir": "/home/pi",
  "logLevel": "debug"
}
```
- The first four variables are the database user, password, host name or IP address, and the database name which will store the table ``servers``.
- ``homeDir`` is the directory where the ``serverinfo`` script will be copied to and run from.
- ``logLevel``, in order of severity, are ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR`` and ``CRITICAL``.


# Using zlma
The following sections describe the line command, the Web interface and the RESTful API.

## The zlma line command
The ``zlma`` line command must include one *subcommand*: 

- ``add       `` Add a server to be managed - if it already exists, it will be updated.  
- ``describe  `` Show the metadata of the ``servers`` table.
- ``init      `` Create the ``servers`` table. 
- ``query     `` Show the specified rows of the ``servers`` table.
- ``remove    `` Remove a managed server.
- ``update    `` Update all rows in table.

Following is the help output for ``zlma``:

```
zlma -h
usage: zlma [-h] [-v] [-C] [-c COLUMN] [-p PATTERN] [-s SERVER] subcommand

zlma - A simple Configuration Management Database

positional arguments:
  subcommand            Can be 'add', 'describe', 'init', 'query', 'remove' or 'update'

options:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -C, --copyscript      copy script 'serverinfo' to target server before add
  -c COLUMN, --column COLUMN
                        column name to search
  -p PATTERN, --pattern PATTERN
                        pattern to search for
  -s SERVER, --server SERVER
                        server to add or remove
```

- Use the ``init`` subcommand to create the ``servers`` table:

## Creating a database
To create and populate a new database, perform the following steps:

- Create a database with the ``init`` subcommand.  This should create a database and a table in zlma.

``` 
$ zlma init
```

- Check that the database was created. Use the ``desc`` subcommand to list the attributes of the ``servers`` table: 

```
Field,Type,Null,Key,Default,Extra
---------------------------------
host_name,varchar(255),NO,PRI,None,
ip_addr,varchar(20),YES,,None,
cpus,int(11),YES,,None,
mem_gb,int(11),YES,,None,
arch,varchar(50),YES,,None,
arch_com,varchar(50),YES,,None,
os,varchar(100),YES,,None,
os_ver,varchar(50),YES,,None,
kern_ver,varchar(100),YES,,None,
kern_rel,varchar(50),YES,,None,
rootfs,int(11),YES,,None,
last_ping,varchar(50),YES,,None,
created,varchar(50),YES,,None,
app,varchar(50),YES,,None,
grp,varchar(50),YES,,None,
owner,varchar(50),YES,,None,
```

- Use the ``add`` subcommand to insert rows into the database.  

The zlma server must be able to **``ssh``** to all servers using key-based authentication.  Following is an example of adding four severs to be managed:
 
```
zlma add --server model800
Added or updated server model800

zlma add --server model1000
Added or updated server model1000

zlma add --server model1500
Added or updated server model1500

zlma add --server model2000
Added or updated server model12000
```

- Use the ``query`` subcommand to show all rows in the table:

```
zlma query 
model1000,192.168.1.229,4,4,aarch64,arm,Linux,AlmaLinux 9.4,#1 SMP Mon Jun 24 08:28:31 EDT 2024,6.6.31-20240529.v8.2.el9,4,24-08-21 06:58:42,2024-06-25,bkupgit,boomboxes,Mike Mac
model1500,192.168.1.147,4,4,aarch64,arm,Linux,Ubuntu 22.04,#63-Ubuntu SMP Wed Jul 17 11:18:43 UTC 2024,5.15.0-1060-raspi,51,24-08-21 06:58:43,2023-08-07,zlma,boomboxes,Mike Mac
model2000,192.168.1.103,4,8,aarch64,arm,Linux,Debian GNU/Linux 12,#1 SMP Debian 1:6.6.31-1+rpt1 (2024-05-29),6.6.31+rpt-rpi-2712,14,24-08-21 06:58:43,2024-03-15,Minimy,boomboxes,Mike                 Mac
model800,192.168.1.35,4,4,aarch64,arm,Linux,Debian GNU/Linux 12,#1 SMP Debian 1:6.6.31-1+rpt1 (2024-05-29),6.6.31+rpt-rpi-v8,11,24-08-21 06:58:44,2024-07-03,Server speak,boomboxes,Mi                ke Mac
```

- Use the ``update`` subcommand to update all rows in the ``servers`` table.  There must be the ability to use key-based authentication to ``ssh`` to all managed servers. 

```
zlma update 
__main__    : INFO     replace_row(): replaced row for server model1000
__main__    : INFO     replace_row(): replaced row for server model1500
__main__    : INFO     replace_row(): replaced row for server model2000
__main__    : INFO     replace_row(): replaced row for server model800
__main__    : INFO     update_cmdb() successfully updated table 'servers'
```
 
## Web interface
Following is a screen shot of the browser interface:

![](finderScreenShot.png)
**Finder browser interface**

Hopefully all is intuitive.  There is one search field that will search on any column. Click the ``Submit`` button and a search will be performed, returning all matching servers.

There is an ``Update all servers`` button. This will go out to all managed servers and update the values in real time. It will update the ``Last ping`` column. 

On the right side of each row, there is a pencil icon. Click that to go into edit mode for the three metadata columns: ``app``, ``group`` and ``owner``.  Modify the data and click the check mark to save, or the X to discard changes.  This is shown in the following figure:

![](FinderEditMode.png)
**Finder in edit mode**


## RESTful API
Following is an example of using the RESTful API to search for servers that have 4 CPUs and 4GB of memory.  Three of the four servers do.

```
curl "http://model1500/restapi.py?cpus=4&mem_gb=4"
<html><head>
</head><body>
<h1>This is the zlma RESTful API!</h1>
<pre>
model1000,192.168.12.233,4,4,aarch64,Linux,Debian GNU/Linux 12 (bookworm),6.6.28+rpt-rpi-v8 #1 SMP PREEMPT Debian 1:6.6.28-1+rpt1 (2024-04-22),29,2024-05-06 14:01:22
model1500,192.168.12.239,4,4,aarch64,Linux,Ubuntu 22.04.4 LTS,5.15.0-1053-raspi #56-Ubuntu SMP PREEMPT Mon Apr 15 18:50:10 UTC 2024,24,2024-05-06 14:02:01
model800,192.168.12.176,4,4,aarch64,Linux,Ubuntu 22.04.4 LTS,5.15.0-1053-raspi #56-Ubuntu SMP PREEMPT Mon Apr 15 18:50:10 UTC 2024,23,2024-05-06 14:01:04
</pre>
</body></html>
```

# vif 
The Virtual Image Facility (VIF) is a product that IBM offered in 2000, but then quickly withdrew.  Perhaps the main reason was that there was no ability to log on to 3270 sessions to user IDs such as ``OPERATOR`` or ``MAINT``.  However, the syntax of VIF both abstracted the function of z/VM as a hypervisor and allows commands to be issued from the Linux command line thus alleviating the need for *green screen* access to z/VM.

## vif commands
``vif`` has the following main commands:

```
         help: give help
   hypervisor: manage z/VM
        image: manage instances of Linux
    partition: manage disk partitions
        query: display many types of z/VM information
```

## vif hypervisor commands

The ``vif hypervisor`` command allows management and maintaintence of z/VM. It has the following subcommands:

```
      collect: gather problem determination info - could this also send hardware errors?
         echo: verify connectivity with vif - not needed with localhost, but perhaps cross LPAR
       errors: report on hardware errors - could this also send problem determination info?
       export: create a backup of configuration info
       import: restore a backup of configuration info
      restart: SHUTDOWN REIPL z/VM
      service: install the latest VIF service (git pull?)
     shutdown: SHUTDOWN z/VM
       verify: performs consistency checks of vif
       volume: add paging or image disk space 
```

## vif image commands
The ``vif image`` commands allow instances of Linux to be managed and modified.  It has the following subcommands:

```
       create: define a new Linux image
               Syntax: vif image create <image>
       delete: delete an existing Linux image
               Syntax: vif image delete <image>
      network: manage network connections for a Linux image
               Syntax: vif image network <image> add|delete <device>
          set: change memory size or number of CPUs of a Linux image
               Syntax: vif image set <image> (storage <size>)|cpus <num>)
        start: boot a Linux image
               Syntax: vif image start <image>
         stop: shutdown a Linux image
               Syntax: vif image stop <image>
      stopall: shutdown all Linux images on LPAR
               Syntax: vif image stopall
```

## vif partition: manage disk partitions
  Subcommands:
```
         copy: copy source partition to newly added target partition
               Syntax: vif partition copy <image1> <device1> [to] <image2> <device2>
       create: add a new partition
               Syntax: vif partition create <image> <device> <size>
       delete: delete an existing partition
               Syntax: vif partition delete <image1> <device1>
        share: give read-only access to the partition of another Linux image
               Syntax: vif partition share <image1> <device1> [with] <image2> <device2>
```

## vif query    
The ``vif query`` command displays many types of z/VM information. It has the following subcommands:

```
       active: report which Linux images are running
          all: invoke all other query subcommands
configuration: display current vif settings
       errors: report on hardware errors
        image: display configuration of a Linux image
               Syntax: vif query <image>
        level: report the vif level (version)
      network: display network configuration
       paging: report on amount of page space and how much is being used
   partitions: display Linux image DASD utilization
  performance: display current CPU, paging and I/O utilization
       shared: display Linux images that share partitions
      volumes: display image and paging DASD volumes
```
# consolez 
consolez is an open-source package that allows browser access to z/VM console data and to issue CP commands. It helps alleviate the need for *green screen* access to z/VM.

# Colophon
Zelma is a feminine given name that originated in the late 19th century in the United States. It's believed to be a variant of the German name Selma, which is derived from the Old Norse word "selmr," meaning "protection" or "shelter."
