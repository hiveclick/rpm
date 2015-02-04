%define name        track.rad
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Provides a redirect tracking site for the Rad Feeder
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: php httpd php-gd php-mysql mysql-server php-pdo php-process php-cli postfix dovecot mydns mydns-mysql pdns pdns-backend-mysql poweradmin spamassassin

%description
Provides a redirect tracking site for the Rad Feeder

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

%config(noreplace) /home/rad/track/webapp/config/*

%attr(775, rad, apache) /home/rad/track
%attr(777, rad, apache) /home/rad/track/webapp/meta/exports
%attr(777, rad, apache) /home/rad/track/webapp/meta/exports/openers
%attr(777, rad, apache) /home/rad/track/webapp/meta/exports/clickers
%attr(777, rad, postfix) /home/rad/track/webapp/meta/exports/fbl
%attr(644, root, root) /etc/cron.d/track.rad
%attr(777, rad, apache) /var/log/rad

%pre
if [ "$1" = "1" ]; then
  if [ `grep -c ^rad /etc/passwd` = "0" ]; then
    /usr/sbin/useradd -c 'RAD User' -d /home/rad -g apache -m -s /bin/false rad 2>&1
    /bin/chmod 770 /home/rad
    /bin/chmod g+s /home/rad
  fi
  if [ `grep -c ^spamd /etc/passwd` = "0" ]; then
  	/usr/sbin/groupadd spamd
    /usr/sbin/useradd -c 'Spam Assassin user' -d /var/log/spamassassin -g spamd -s /bin/false spamd 2>&1
    sudo chown spamd:spamd /var/log/spamassassin
  fi
elif [ "$1" = "2" ]; then
  if [ `grep -c ^spamd /etc/passwd` = "0" ]; then
  	/usr/sbin/groupadd spamd
    /usr/sbin/useradd -c 'Spam Assassin user' -d /var/log/spamassassin -g spamd -s /bin/false spamd 2>&1
    sudo chown spamd:spamd /var/log/spamassassin
  fi
fi

%post
if [ "$1" = "1" ]; then
  # Perform tasks to prepare for the initial installation
  # echo "Installing rad user environment..."
  
  # copy over the install.ini only the first time
  cp /home/rad/track/init/install_sample.ini /home/rad/track/init/install.ini
  
  echo ""
  echo "    Installing RAD for first time use..."
  php /home/rad/track/init/install.sh silent
  
  /bin/sed -i 's/;date.timezone.*/date.timezone=US\/Pacific/' /etc/php.ini
  /bin/sed -i 's/post_max_size =.*/post_max_size = 128M/' /etc/php.ini
  /bin/sed -i 's/upload_max_filesize =.*/upload_max_filesize = 128M/' /etc/php.ini
  if [ `grep -c ^max_input_vars /etc/php.ini` = "0" ]; then
    /bin/sed -i 's/max_input_time =.*/max_input_time = 60\nmax_input_vars = 2048/' /etc/php.ini
  fi
  
  # Enable the various services on boot
  /sbin/chkconfig pdns on
  #/sbin/chkconfig mydns on
  #/sbin/chkconfig mydns_negative on
  /sbin/chkconfig mysqld on
  /sbin/chkconfig postfix on
  /sbin/chkconfig dovecot on
  /sbin/chkconfig spamassassin on
  /sbin/chkconfig httpd on
  
  # Start the pdns service
  /sbin/service mysqld restart
  /sbin/service spamassassin restart
  /sbin/service dovecot restart
  /sbin/service httpd restart
  /sbin/service postfix restart
  /sbin/service pdns restart
  #/sbin/service mydns restart
  #/sbin/service mydns_negative restart
  
  /bin/cp -f /home/rad/track/init/config/virtualhost /etc/httpd/conf.d/a.track.rad.conf
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/rad/track/webapp/cache/*
elif [ "$1" = "2" ]; then
  echo "    Applying updates to RAD..."
  php /home/rad/track/init/upgrade.sh silent
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/rad/track/webapp/cache/*
fi


%postun
#if [ "$1" = "0" ]; then
#elif [ "$1" = "1" ]; then
#fi