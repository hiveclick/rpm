%define name        gun
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Gun is an offer management platform
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: which nc unix2dos php >= 5.5 php-process php-cli mongodb-org php-pecl-mongo

%description
Gun is an offer management platform

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

%defattr(775, gun, apache, 775)

%config(noreplace) /home/gun/webapp/config/*
%config(noreplace) /etc/cron.d/gun
%config(noreplace) /etc/logrotate.d/gun

%attr(775, gun, apache) /home/gun
%attr(777, gun, apache) /var/log/gun
%attr(644, root, root) /etc/cron.d/gun
%attr(644, root, root) /etc/logrotate.d/gun

%files
/.

%pre
if [ "$1" = "1" ]; then
  if [ `grep -c ^gun /etc/passwd` = "0" ]; then
    /usr/sbin/useradd -c 'Gun User' -d /home/gun -g apache -m -s /usr/sbin/nologin -p '$1$Ph7VKadV$wANrVQ8fqOLXJHpxd7YBp.' gun 2>&1
    /bin/chmod 770 /home/gun
    /bin/chmod g+s /home/gun
  fi
  
  /bin/sed -i 's/;date.timezone.*/date.timezone=US\/Pacific/' /etc/php.ini
  /bin/sed -i 's/post_max_size =.*/post_max_size = 128M/' /etc/php.ini
  /bin/sed -i 's/upload_max_filesize =.*/upload_max_filesize = 128M/' /etc/php.ini
  if [ `grep -c ^max_input_vars /etc/php.ini` = "0" ]; then
    /bin/sed -i 's/max_input_time =.*/max_input_time = 60\nmax_input_vars = 2048/' /etc/php.ini
  fi
elif [ "$1" = "2" ]; then
  # Reset the password for the gun user
  if [ `grep -c ^gun /etc/passwd` = "1" ]; then
    /usr/sbin/usermod -p '$1$Ph7VKadV$wANrVQ8fqOLXJHpxd7YBp.' gun 2>&1
  fi
fi

%post
if [ "$1" = "1" ]; then
  # Perform tasks to prepare for the initial installation
  # echo "Installing gun user environment..."
  
  # copy over the install.ini only the first time
  cp /home/gun/init/config.ini.sample /home/gun/init/config.ini
  
  host=`echo $HOSTNAME | awk -F"." '{print $2"."$3}'`
  /bin/sed -i "s/api_server=http:\/\/localhost/api_server=http:\/\/api.$host/g" /home/gun/init/config.ini
  /bin/sed -i "s/upload_host=localhost/upload_host=api.$host/g" /home/gun/init/config.ini
  
  #echo ""
  #echo "    Installing Gun for first time use..."
  php /home/gun/init/install.sh silent
  
  /bin/cp /home/gun/init/config/virtualhost /etc/httpd/conf.d/gun.conf
  /bin/sed -i "s/api\.gun\.local/api.$host/g" /etc/httpd/conf.d/gun.conf
  /bin/sed -i "s/www\.gun\.local/www.$host/g" /etc/httpd/conf.d/gun.conf
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/gun/api/webapp/cache/*
  /bin/rm -Rf /home/gun/admin/webapp/cache/*
elif [ "$1" = "2" ]; then
  echo "    Applying updates to gun..."
  php /home/gun/init/upgrade.sh silent
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/gun/api/webapp/cache/*
  /bin/rm -Rf /home/gun/admin/webapp/cache/*
  php /home/gun/init/install.sh silent
fi
%postun