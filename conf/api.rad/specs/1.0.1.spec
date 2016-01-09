%define _binaries_in_noarch_packages_terminate_build   0
%define name        api.rad
%define version 	[[VERSION]]
%define revision	[[REVISION]]
%define debug_package %{nil}

Summary: Provides an api interface to the Rad Feeder
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: httpd php php-gd php-mysql mysql-server php-imap dos2unix php-pecl-ssh2 vsftpd php-pdo php-process jwhois

%description
Provides an api interface to the Rad Feeder

%prep
%setup -q

%build

%install
# as sanity protection, make sure the Buildroot is empty
rm -rf $RPM_BUILD_ROOT
# install software into the Buildroot
cp -rvf $RPM_BUILD_DIR/%{name}-%{version} $RPM_BUILD_ROOT

%clean
if( [ $RPM_BUILD_ROOT != '/' ] ); then rm -rf $RPM_BUILD_ROOT; fi;

%files
/.

%defattr(775, rad, apache, 775)

%config(noreplace) /home/rad/api/webapp/config/*
%config(noreplace) /etc/cron.d/api.rad
%config(noreplace) /etc/logrotate.d/api.rad

%attr(775, rad, apache) /home/rad/api
%attr(777, rad, apache) /home/rad/api/webapp/meta/uploads
%attr(777, rad, apache) /home/rad/api/webapp/meta/imports
%attr(777, rad, apache) /home/rad/api/webapp/meta/exports
%attr(4755, rad, apache) /home/rad/api/webapp/meta/crons/
%attr(777, rad, apache) /var/log/rad
%attr(777, rad, apache) /var/log/rad/lists
%attr(777, rad, apache) /var/log/rad/imports
%attr(644, root, root) /etc/cron.d/api.rad
%attr(644, root, root) /etc/logrotate.d/api.rad

%pre
if [ "$1" = "1" ]; then
  if [ `grep -c ^rad /etc/passwd` = "0" ]; then
    /usr/sbin/useradd -c 'RAD User' -d /home/rad -g apache -m -s /usr/sbin/nologin -p '$1$Ph7VKadV$wANrVQ8fqOLXJHpxd7YBp.' rad 2>&1
    /bin/chmod 770 /home/rad
    /bin/chmod g+s /home/rad
  fi
  
  # Make changes to the vsftpd configuration
  /bin/sed -i 's/^anonymous_enable/#anonymous_enable/' /etc/vsftpd/vsftpd.conf
  /bin/sed -i 's/^connect_from_port_20/#connect_from_port_20/' /etc/vsftpd/vsftpd.conf 
  /bin/sed -i 's/^chroot_local_user/#chroot_local_user/' /etc/vsftpd/vsftpd.conf 
  /bin/sed -i 's/^userlist_file/#userlist_file/' /etc/vsftpd/vsftpd.conf 
  /bin/sed -i 's/^userlist_enable/#userlist_enable/' /etc/vsftpd/vsftpd.conf 
  /bin/sed -i 's/^userlist_deny/#userlist_deny/' /etc/vsftpd/vsftpd.conf 

  # Enable the local ftp user list
  echo "chroot_local_user=YES" >> /etc/vsftpd/vsftpd.conf 
  echo "userlist_file=/etc/vsftpd/vsftpd.userlist" >> /etc/vsftpd/vsftpd.conf
  echo "userlist_enable=YES" >> /etc/vsftpd/vsftpd.conf
  echo "userlist_deny=NO" >> /etc/vsftpd/vsftpd.conf
  
  # Add the rad user to the local ftp userlist
  if [ -f /etc/vsftpd/vsftpd.userlist ]; then
    if [ `grep -c ^rad /etc/vsftpd/vsftpd.userlist` = "0" ]; then
  	  echo "rad" >> /etc/vsftpd/vsftpd.userlist
    fi
  else
    echo "rad" > /etc/vsftpd/vsftpd.userlist
  fi
  
  if [ `grep -c ^/usr/sbin/nologin /etc/shells` = "0" ]; then
  	  echo "/usr/sbin/nologin" >> /etc/shells
  fi
  
  /bin/sed -i 's/;date.timezone.*/date.timezone=US\/Pacific/' /etc/php.ini
  /bin/sed -i 's/post_max_size =.*/post_max_size = 128M/' /etc/php.ini
  /bin/sed -i 's/upload_max_filesize =.*/upload_max_filesize = 128M/' /etc/php.ini
  /bin/sed -i 's/session.gc_maxlifetime =.*/session.gc_maxlifetime = 604800/' /etc/php.ini
  if [ `grep -c ^max_input_vars /etc/php.ini` = "0" ]; then
    /bin/sed -i 's/max_input_time =.*/max_input_time = 60\nmax_input_vars = 2048/' /etc/php.ini
  fi
    
elif [ "$1" = "2" ]; then
  # Reset the password for the rad user
  if [ `grep -c ^rad /etc/passwd` = "1" ]; then
    /usr/sbin/usermod -p '$1$Ph7VKadV$wANrVQ8fqOLXJHpxd7YBp.' rad 2>&1
  fi
  
  # Make changes to the vsftpd configuration
  /bin/sed -i 's/^anonymous_enable/#anonymous_enable/' /etc/vsftpd/vsftpd.conf
  /bin/sed -i 's/^connect_from_port_20/#connect_from_port_20/' /etc/vsftpd/vsftpd.conf 
  /bin/sed -i 's/^chroot_local_user/#chroot_local_user/' /etc/vsftpd/vsftpd.conf 
  /bin/sed -i 's/^userlist_file/#userlist_file/' /etc/vsftpd/vsftpd.conf 
  /bin/sed -i 's/^userlist_enable/#userlist_enable/' /etc/vsftpd/vsftpd.conf 
  /bin/sed -i 's/^userlist_deny/#userlist_deny/' /etc/vsftpd/vsftpd.conf 
  
  # Enable the local ftp user list
  echo "chroot_local_user=YES" >> /etc/vsftpd/vsftpd.conf 
  echo "userlist_file=/etc/vsftpd/vsftpd.userlist" >> /etc/vsftpd/vsftpd.conf
  echo "userlist_enable=YES" >> /etc/vsftpd/vsftpd.conf
  echo "userlist_deny=NO" >> /etc/vsftpd/vsftpd.conf
  
  # Add the rad user to the local ftp userlist
  if [ -f /etc/vsftpd/vsftpd.userlist ]; then
    if [ `grep -c ^rad /etc/vsftpd/vsftpd.userlist` = "0" ]; then
  	  echo "rad" >> /etc/vsftpd/vsftpd.userlist
    fi
  else
    echo "rad" > /etc/vsftpd/vsftpd.userlist
  fi
  
  if [ `grep -c ^/usr/sbin/nologin /etc/shells` = "0" ]; then
  	  echo "/usr/sbin/nologin" >> /etc/shells
  fi
fi

%post
if [ "$1" = "1" ]; then
  # Perform tasks to prepare for the initial installation
  # echo "Installing rad user environment..."
  
  # Install the default mysql configuration
  cp /home/rad/api/init/config/my.cnf /etc/my.cnf
  
  # copy over the install.ini only the first time
  cp /home/rad/api/init/install_sample.ini /home/rad/api/init/install.ini
  
  host=`echo $HOSTNAME | awk -F"." '{print $2"."$3}'`
  /bin/sed -i "s/api_server=http:\/\/localhost/api_server=http:\/\/api.$host/g" /home/rad/api/init/install.ini
  /bin/sed -i "s/upload_host=api.rad.local/upload_host=api.$host/g" /home/rad/api/init/install.ini
  
  if [ -f /root/.my.cnf ]; then
    mysql_password=`/bin/grep "password" ~/.my.cnf | /usr/bin/head -n1 | /bin/sed 's/password=//' | /bin/sed 's/"//g'`
    /bin/sed -i "s/db_pass=\"\"/db_pass=\"$mysql_password\"/g" /home/rad/api/init/install.ini
    /bin/sed -i "s/db_pass_readonly=\"\"/db_pass_readonly=\"$mysql_password\"/g" /home/rad/api/init/install.ini
  fi
  
  echo ""
  echo "    Installing RAD for first time use..."
  php /home/rad/api/init/install.sh silent
  
  /bin/cp /home/rad/api/init/config/virtualhost /etc/httpd/conf.d/api.rad.conf
  /bin/sed -i "s/api\.localhost/api.$host/g" /etc/httpd/conf.d/api.rad.conf
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/rad/api/webapp/cache/*
  
  # Start the vsftpd service
  /sbin/chkconfig vsftpd on
  /sbin/service vsftpd restart
elif [ "$1" = "2" ]; then
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/rad/api/webapp/cache/*
fi


%postun
#if [ "$1" = "0" ]; then
#elif [ "$1" = "1" ]; then
#fi
