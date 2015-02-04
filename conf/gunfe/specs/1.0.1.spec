%define name        gunfe
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: GunFE is an offer management platform used on the FrontEnd
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: which nc unix2dos php >= 5.5 php-process php-cli php-pecl-mongo

%description
GunFE is an offer management platform used on the FrontEnd

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

%config(noreplace) /home/gunfe/webapp/config/*
%config(noreplace) /etc/cron.d/gunfe
%config(noreplace) /etc/logrotate.d/gunfe

%attr(775, gun, apache) /home/gunfe
%attr(777, gun, apache) /var/log/gun
%attr(644, root, root) /etc/cron.d/gunfe
%attr(644, root, root) /etc/logrotate.d/gunfe

%files
/.

%pre
if [ "$1" = "1" ]; then
  if [ `grep -c ^gun /etc/passwd` = "0" ]; then
    /usr/sbin/useradd -c 'Gun User' -d /home/gunfe -g apache -m -s /usr/sbin/nologin -p '$1$Ph7VKadV$wANrVQ8fqOLXJHpxd7YBp.' gun 2>&1
    /bin/chown gun:apache /home/gunfe -Rf
    /bin/chmod 770 /home/gunfe -Rf
    /bin/chmod g+s /home/gunfe -Rf
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
  cp /home/gunfe/init/config.ini.sample /home/gunfe/init/config.ini
  
  host=`echo $HOSTNAME | awk -F"." '{print $2"."$3}'`
  /bin/sed -i "s/api_server=.*/api_server=http:\/\/api.$host/g" /home/gunfe/init/config.ini
  /bin/sed -i "s/upload_host=.*/upload_host=api.$host/g" /home/gunfe/init/config.ini
  
  #echo ""
  #echo "    Installing Gun for first time use..."
  php /home/gunfe/init/install.sh silent
  
  /bin/cp /home/gunfe/init/config/virtualhost /etc/httpd/conf.d/gunfe.conf
  /bin/sed -i "s/frontend\.gun\.local/frontend.$host/g" /etc/httpd/conf.d/gunfe.conf
  /bin/sed -i "s/www\.debt\.local/debt.$host/g" /etc/httpd/conf.d/gunfe.conf
  /bin/sed -i "s/www\.rate\.local/rate.$host/g" /etc/httpd/conf.d/gunfe.conf
  
  /bin/sed -i "s/api\.gun\.local/api.$host/g" /home/gunfe/examples/debtMover/lib/config.ini
  /bin/sed -i "s/FE_LIB_DIR.*/FE_LIB_DIR = \"\/home\/gunfe\/frontend\/webapp\/lib\"/g" /home/gunfe/examples/debtMover/lib/config.ini
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/gunfe/frontend/webapp/cache/*
  
elif [ "$1" = "2" ]; then
  echo "    Applying updates to gun..."
  # php /home/gunfe/init/upgrade.sh silent
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/gunfe/frontend/webapp/cache/*
fi
%postun                                                                                                                   