%define name        dns.rad
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Provides a dns component for hosting reverse dns
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: php httpd php-mysql php-pdo php-process php-cli mydns mydns-mysql

%description
Provides a dns component for hosting reverse dns

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

%config(noreplace) /home/rad/dns/webapp/config/*

%attr(775, rad, apache) /home/rad/dns
%attr(777, rad, apache) /var/log/rad

%pre
if [ "$1" = "1" ]; then
  if [ `grep -c ^rad /etc/passwd` = "0" ]; then
    /usr/sbin/useradd -c 'RAD User' -d /home/rad -g apache -m -s /bin/false rad 2>&1
    /bin/chmod 770 /home/rad
    /bin/chmod g+s /home/rad
  fi
fi

%post
if [ "$1" = "1" ]; then
  # Perform tasks to prepare for the initial installation
  # echo "Installing rad user environment..."
  
  # copy over the install.ini only the first time
  cp /home/rad/dns/init/install_sample.ini /home/rad/dns/init/install.ini
  
  echo ""
  echo "    Installing RAD for first time use..."
  php /home/rad/dns/init/install.sh silent
  
  /bin/sed -i 's/;date.timezone.*/date.timezone=US\/Pacific/' /etc/php.ini
  /bin/sed -i 's/post_max_size =.*/post_max_size = 128M/' /etc/php.ini
  /bin/sed -i 's/upload_max_filesize =.*/upload_max_filesize = 128M/' /etc/php.ini
  /bin/sed -i 's/session.gc_maxlifetime =.*/session.gc_maxlifetime = 604800/' /etc/php.ini
  if [ `grep -c ^max_input_vars /etc/php.ini` = "0" ]; then
    /bin/sed -i 's/max_input_time =.*/max_input_time = 60\nmax_input_vars = 2048/' /etc/php.ini
  fi
  
  # Enable the various services on boot
  /sbin/chkconfig mydns on
  /sbin/chkconfig mysqld on
  /sbin/chkconfig httpd on
  
  # Start the mydns service
  /sbin/service mydns restart
  
  /bin/cp -f /home/rad/dns/init/config/virtualhost /etc/httpd/conf.d/dns.rad.conf
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/rad/dns/webapp/cache/*
elif [ "$1" = "2" ]; then
  echo "    Applying updates to RAD..."
  # php /home/rad/dns/init/upgrade.sh silent
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/rad/dns/webapp/cache/*
fi


%postun
#if [ "$1" = "0" ]; then
#elif [ "$1" = "1" ]; then
#fi