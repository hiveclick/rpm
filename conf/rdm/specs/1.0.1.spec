%define name        rdm
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: RDM is a data management system build in conjunction with RAD
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: which nc unix2dos php >= 5.5 php-gd php-process php-cli mongodb-org php-pecl-mongo GeoIP GeoIP-update GeoIP-devel php-pecl-geoip

%description
RDM is a data management system build in conjunction with RAD

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

%defattr(775, rdm, apache, 775)

%config(noreplace) /home/rdm/webapp/config/*
%config(noreplace) /etc/cron.d/rdm
%config(noreplace) /etc/logrotate.d/rdm

%attr(775, rdm, apache) /home/rdm
%attr(777, rdm, apache) /var/log/rdm
%attr(644, root, root) /etc/cron.d/rdm
%attr(644, root, root) /etc/logrotate.d/rdm

%files
/.

%pre
if [ "$1" = "1" ]; then
  if [ `grep -c ^rdm /etc/passwd` = "0" ]; then
    /usr/sbin/useradd -c 'RDM User' -d /home/rdm -g apache -m -s /usr/sbin/nologin -p '$1$Ph7VKadV$wANrVQ8fqOLXJHpxd7YBp.' rdm 2>&1
    /bin/chmod 770 /home/rdm
    /bin/chmod g+s /home/rdm
  fi
elif [ "$1" = "2" ]; then
  # Reset the password for the rdm user
  if [ `grep -c ^rdm /etc/passwd` = "1" ]; then
    /usr/sbin/usermod -p '$1$Ph7VKadV$wANrVQ8fqOLXJHpxd7YBp.' rdm 2>&1
  fi
fi

%post
if [ "$1" = "1" ]; then
  /bin/sed -i 's/;date.timezone.*/date.timezone=US\/Pacific/' /etc/php.ini
  /bin/sed -i 's/post_max_size =.*/post_max_size = 128M/' /etc/php.ini
  /bin/sed -i 's/upload_max_filesize =.*/upload_max_filesize = 128M/' /etc/php.ini
  if [ `grep -c ^max_input_vars /etc/php.ini` = "0" ]; then
    /bin/sed -i 's/max_input_time =.*/max_input_time = 60\nmax_input_vars = 2048/' /etc/php.ini
  fi
  ln -s /usr/share/GeoIP/GeoLiteCity.dat /usr/share/GeoIP/GeoIPCity.dat

  # Perform tasks to prepare for the initial installation
  # echo "Installing RDM user environment..."
  
  # copy over the install.ini only the first time
  cp /home/rdm/init/config.ini.sample /home/rdm/init/config.ini
  
  host=`echo $HOSTNAME | awk -F"." '{print $2"."$3}'`
  /bin/sed -i "s/api_server=http:\/\/localhost/api_server=http:\/\/api.$host/g" /home/rdm/init/config.ini
  /bin/sed -i "s/upload_host=localhost/upload_host=api.$host/g" /home/rdm/init/config.ini
  
  #echo ""
  #echo "    Installing RDM for first time use..."
  php /home/rdm/init/install.sh silent
  
  /bin/cp /home/rdm/init/config/virtualhost /etc/httpd/conf.d/rdm.conf
  /bin/sed -i "s/api\.rdm\.local/api.$host/g" /etc/httpd/conf.d/rdm.conf
  /bin/sed -i "s/www\.rdm\.local/www.$host/g" /etc/httpd/conf.d/rdm.conf
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/rdm/api/webapp/cache/*
  /bin/rm -Rf /home/rdm/admin/webapp/cache/*
elif [ "$1" = "2" ]; then
  echo "    Applying updates to RDM..."
  php /home/rdm/init/upgrade.sh silent
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/rdm/api/webapp/cache/*
  /bin/rm -Rf /home/rdm/admin/webapp/cache/*
  php /home/rdm/init/install.sh silent
fi
%postun