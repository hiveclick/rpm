%define name        api.rad
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Provides an api interface to the Rad Feeder
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: httpd php php-gd php-mysql mysql-server

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

%post
if [ "$1" = "1" ]; then
  # Perform tasks to prepare for the initial installation
  echo "Installing rad user environment..."
  if [ "$(grep "rad" /etc/passwd | wc -l)" -eq 0 ]; then
    useradd -g apache -M -r -s /bin/false rad
  fi
  
  # Create the log folder for rad
  if [ ! -d "/var/log/rad" ]; then
	  mkdir /var/log/rad
	  chown rad:apache /var/log/rad
	  chmod 775 /var/log/rad
  fi
  
  echo "Installing RAD for first time use..."
  php /home/rad/api/init/install.sh
  
  # Copy the virtual host to apache so stuff works
  cp -f /home/rad/api/init/config/virtualhost /etc/httpd/conf.d/api.rad.vhost.conf
  
  # Copy the logrotate.d so that we can rotate our logs
  cp -f /home/rad/api/init/config/logrotate /etc/logrotate.d/api.rad
  
  # Copy the crontab so that we can start our processes
  cp -f /home/rad/api/init/config/crontab /etc/cron.d/rad
  
elif [ "$1" = "2" ]; then
  # Perform whatever maintenance must occur before the upgrade begins
  echo "Upgrading rad user environment..."
  
  # Create the log folder for rad
  if [ ! -d "/var/log/rad" ]; then
	  mkdir /var/log/rad
	  chown rad:apache /var/log/rad
	  chmod 775 /var/log/rad
  fi
  
  # Copy the virtual host to apache so stuff works
  rm -f /etc/httpd/conf.d/rad.vhost.conf
  cp -f /home/rad/api/init/config/virtualhost /etc/httpd/conf.d/api.rad.vhost.conf
  
  # Copy the logrotate.d so that we can rotate our logs
  rm -f /etc/logrotate.d/rad
  cp -f /home/rad/api/init/config/logrotate /etc/logrotate.d/api.rad
  
  # Copy the crontab so that we can start our processes
  rm -f /etc/cron.d/rad
  cp -f /home/rad/api/init/config/crontab /etc/cron.d/api.rad
fi


%postun
if [ "$1" = "0" ]; then
  # Perform tasks to prepare for the final uninstallation
  echo "Removing rad user environment..."
  rm -f /etc/cron.d/api.rad
  rm -f /etc/logrotate.d/api.rad
  rm -Rf /var/log/rad
  if [ "$(grep "rad" /etc/passwd | wc -l)" -gt 0 ]; then
    userdel -r rad
  fi
elif [ "$1" = "2" ]; then
  # Perform whatever maintenance must occur before the upgrade begins
  echo "Upgrading rad user environment..."
fi