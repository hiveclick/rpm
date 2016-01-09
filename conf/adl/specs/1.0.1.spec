%define _binaries_in_noarch_packages_terminate_build   0
%define name        adl
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Provides a bridge API between Infusionsoft and ADLWare
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: httpd php dos2unix

%description
Provides a bridge API between Infusionsoft and ADLWare

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

%defattr(775, adl, apache, 775)

%config(noreplace) /home/adl/api/webapp/config/*

%attr(775, adl, apache) /home/adl/api
%attr(777, adl, apache) /var/log/adl

%pre
if [ "$1" = "1" ]; then
  if [ `grep -c ^adl /etc/passwd` = "0" ]; then
    /usr/sbin/useradd -c 'ADL User' -d /home/adl -g apache -m -s /usr/sbin/nologin -p '$1$Ph7VKadV$wANrVQ8fqOLXJHpxd7YBp.' adl 2>&1
    /bin/chmod 770 /home/adl
    /bin/chmod g+s /home/adl
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
  # Reset the password for the adl user
  if [ `grep -c ^adl /etc/passwd` = "1" ]; then
    /usr/sbin/usermod -p '$1$Ph7VKadV$wANrVQ8fqOLXJHpxd7YBp.' adl 2>&1
  fi
  
  if [ `grep -c ^/usr/sbin/nologin /etc/shells` = "0" ]; then
  	  echo "/usr/sbin/nologin" >> /etc/shells
  fi
fi

%post
if [ "$1" = "1" ]; then
  # Perform tasks to prepare for the initial installation
  # echo "Installing adl user environment..."
  
  # copy over the install.ini only the first time
  cp /home/adl/api/init/install_sample.ini /home/adl/api/init/install.ini
  
  host=`echo $HOSTNAME | awk -F"." '{print $2"."$3}'`
  /bin/sed -i "s/api_server=http:\/\/localhost/api_server=http:\/\/api.$host/g" /home/adl/api/init/install.ini
  /bin/sed -i "s/upload_host=api.adl.local/upload_host=api.$host/g" /home/adl/api/init/install.ini
  
  echo ""
  echo "    Installing ADL for first time use..."
  php /home/adl/api/init/install.sh silent
  
  /bin/cp /home/adl/api/init/config/virtualhost /etc/httpd/conf.d/adl.conf
  /bin/sed -i "s/api\.localhost/api.$host/g" /etc/httpd/conf.d/adl.conf
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/adl/api/webapp/cache/*
  
elif [ "$1" = "2" ]; then
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/adl/api/webapp/cache/*
fi


%postun
#if [ "$1" = "0" ]; then
#elif [ "$1" = "1" ]; then
#fi