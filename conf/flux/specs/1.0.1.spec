%define name        flux
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Flux is an offer management platform
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
Flux is an offer management platform

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

%defattr(775, flux, apache, 775)

%config(noreplace) /home/flux/webapp/config/*
%config(noreplace) /etc/cron.d/flux
%config(noreplace) /etc/logrotate.d/flux

%attr(775, flux, apache) /home/flux
%attr(777, flux, apache) /var/log/flux
%attr(644, root, root) /etc/cron.d/flux
%attr(644, root, root) /etc/logrotate.d/flux

%files
/.

%pre
if [ "$1" = "1" ]; then
  if [ `grep -c ^flux /etc/passwd` = "0" ]; then
    /usr/sbin/useradd -c 'Flux User' -d /home/flux -g apache -m -s /usr/sbin/nologin -p '$1$Ph7VKadV$wANrVQ8fqOLXJHpxd7YBp.' flux 2>&1
    /bin/chmod 770 /home/flux
    /bin/chmod g+s /home/flux
  fi
  
  /bin/sed -i 's/;date.timezone.*/date.timezone=US\/Pacific/' /etc/php.ini
  /bin/sed -i 's/post_max_size =.*/post_max_size = 128M/' /etc/php.ini
  /bin/sed -i 's/upload_max_filesize =.*/upload_max_filesize = 128M/' /etc/php.ini
  if [ `grep -c ^max_input_vars /etc/php.ini` = "0" ]; then
    /bin/sed -i 's/max_input_time =.*/max_input_time = 60\nmax_input_vars = 2048/' /etc/php.ini
  fi
elif [ "$1" = "2" ]; then
  # Reset the password for the flux user
  if [ `grep -c ^flux /etc/passwd` = "1" ]; then
    /usr/sbin/usermod -p '$1$Ph7VKadV$wANrVQ8fqOLXJHpxd7YBp.' flux 2>&1
  fi
fi

%post
if [ "$1" = "1" ]; then
  # Perform tasks to prepare for the initial installation
  # echo "Installing flux user environment..."
  
  # copy over the install.ini only the first time
  cp /home/flux/init/config.ini.sample /home/flux/init/config.ini
  
  host=`echo $HOSTNAME | awk -F"." '{print $2"."$3}'`
  /bin/sed -i "s/api_server=http:\/\/localhost/api_server=http:\/\/api.$host/g" /home/flux/init/config.ini
  /bin/sed -i "s/upload_host=localhost/upload_host=api.$host/g" /home/flux/init/config.ini
  
  #echo ""
  #echo "    Installing Flux for first time use..."
  php /home/flux/init/install.sh silent
  
  /bin/cp /home/flux/init/config/virtualhost /etc/httpd/conf.d/flux.conf
  /bin/sed -i "s/api\.flux\.local/api.$host/g" /etc/httpd/conf.d/flux.conf
  /bin/sed -i "s/www\.flux\.local/www.$host/g" /etc/httpd/conf.d/flux.conf
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/flux/api/webapp/cache/*
  /bin/rm -Rf /home/flux/admin/webapp/cache/*
elif [ "$1" = "2" ]; then
  echo "    Applying updates to flux..."
  php /home/flux/init/upgrade.sh silent
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/flux/api/webapp/cache/*
  /bin/rm -Rf /home/flux/admin/webapp/cache/*
  php /home/flux/init/install.sh silent
fi
%postun