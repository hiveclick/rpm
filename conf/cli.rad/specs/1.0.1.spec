%define name        cli.rad
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Provides shared libraries for sending emails using the Rad feeder
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: php php-gd PowerMTA

%description
Provides shared libraries for sending emails using the Rad feeder

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
  useradd -g pmta -M -s /bin/false rad
  
  # Create the log folder for rad
  if [ ! -d "$DIRECTORY" ]; then
	  mkdir /var/log/rad
	  chown rad:pmta /var/log/rad
	  chmod 775 /var/log/rad
  fi
  
  echo "Installing RAD for first time use..."
  php /home/rad/cli/init/install.sh
  
  # Link common cli commands to the cli folder
  ln -s /home/rad/cli/webapp/meta/crons/feeder_daemon.sh /home/rad/cli/cli/feeder_daemon
  ln -s /home/rad/cli/webapp/meta/crons/feeder_top_tier_domain_daemon.sh /home/rad/cli/cli/ttd_daemon
  ln -s /home/rad/cli/webapp/meta/crons/server_status.sh /home/rad/cli/cli/server_status
  ln -s /home/rad/cli/webapp/meta/crons/pmta.sh /home/rad/cli/cli/pmta
  
  # Reset permissions on the meta folder
  chmod 777 /home/rad/cli/webapp/meta -Rf
  
  # Copy the logrotate.d so that we can rotate our logs
  cp -f /home/rad/cli/init/config/logrotate /etc/logrotate.d/cli.rad
  
  # Copy the crontab so that we can start our processes
  cp -f /home/rad/cli/init/config/crontab /etc/cron.d/rad
elif [ "$1" = "2" ]; then
  # Perform whatever maintenance must occur before the upgrade begins
  echo "Upgrading rad user environment..."
  rm -f /home/rad/cli/cli/feeder_daemon
  ln -s /home/rad/cli/webapp/meta/crons/feeder_daemon.sh /home/rad/cli/cli/feeder_daemon
  rm -f /home/rad/cli/cli/ttd_daemon
  ln -s /home/rad/cli/webapp/meta/crons/feeder_top_tier_domain_daemon.sh /home/rad/cli/cli/ttd_daemon
  rm -f /home/rad/cli/cli/server_status
  ln -s /home/rad/cli/webapp/meta/crons/server_status.sh /home/rad/cli/cli/server_status
  rm -f /home/rad/cli/cli/pmta
  ln -s /home/rad/cli/webapp/meta/crons/pmta.sh /home/rad/cli/cli/pmta
  
  # Create the log folder for rad
  if [ ! -d "$DIRECTORY" ]; then
	  mkdir -p /var/log/rad
	  chown rad:pmta /var/log/rad
	  chmod 775 /var/log/rad
  fi
  
  # Reset permissions on the meta folder
  chmod 777 /home/rad/cli/webapp/meta -Rf
  
  # Copy the logrotate.d so that we can rotate our logs
  rm -f /etc/logrotate.d/rad
  cp -f /home/rad/cli/init/config/logrotate /etc/logrotate.d/cli.rad
  
  # Copy the crontab so that we can start our processes
  rm -f /etc/cron.d/rad
  cp -f /home/rad/cli/init/config/crontab /etc/cron.d/cli.rad
fi


%postun
if [ "$1" = "0" ]; then
  # Perform tasks to prepare for the final uninstallation
  echo "Removing rad user environment..."
  rm -f /etc/cron.d/cli.rad
  rm -f /etc/logrotate.d/cli.rad
  rm -Rf /var/log/rad
  userdel -r rad
elif [ "$1" = "2" ]; then
  # Perform whatever maintenance must occur before the upgrade begins
  echo "Upgrading rad user environment..."
fi