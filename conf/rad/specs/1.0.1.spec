%define name        rad
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Provides an administration site for the Rad Feeder
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: php php-gd

%description
Provides an administration site for the Rad Feeder

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
  useradd -g apache -M -s /bin/false rad
  
  # Create the log folder for rad
  if [ ! -d "$DIRECTORY" ]; then
	  mkdir /var/log/rad
	  chown rad:apache /var/log/rad
	  chmod 775 /var/log/rad
  fi
  
  echo "Installing RAD for first time use..."
  php /var/www/sites/rad/admin/init/install.sh
  
  # Copy the logrotate.d so that we can rotate our logs
  cp -f /var/www/sites/rad/admin/init/config/logrotate /etc/logrotate.d/rad

  # Copy the crontab so that we can start our processes
  cp -f /var/www/sites/rad/admin/init/config/crontab /etc/cron.d/rad
elif [ "$1" = "2" ]; then
  # Perform whatever maintenance must occur before the upgrade begins
  echo "Upgrading rad user environment..."
  
  # Create the log folder for rad
  if [ ! -d "$DIRECTORY" ]; then
	  mkdir /var/log/rad
	  chown rad:apache /var/log/rad
	  chmod 775 /var/log/rad
  fi
  
  # Copy the logrotate.d so that we can rotate our logs
  rm -f /etc/logrotate.d/rad
  cp -f /var/www/sites/rad/admin/init/config/logrotate /etc/logrotate.d/rad
  
  # Copy the crontab so that we can start our processes
  rm -f /etc/cron.d/rad
  cp -f /var/www/sites/rad/admin/init/config/crontab /etc/cron.d/rad
fi


%postun
if [ "$1" = "0" ]; then
  # Perform tasks to prepare for the final uninstallation
  echo "Removing rad user environment..."
  rm -f /etc/cron.d/rad
  rm -f /etc/logrotate.d/rad
  rm -Rf /var/log/rad
  userdel -r rad
elif [ "$1" = "2" ]; then
  # Perform whatever maintenance must occur before the upgrade begins
  echo "Upgrading rad user environment..."
fi