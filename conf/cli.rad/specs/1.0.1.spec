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

%config(noreplace) /home/rad/cli/init/install.ini
%config(noreplace) /home/rad/cli/webapp/config/*
%config(noreplace) /etc/cron.d/cli.rad
%config(noreplace) /etc/logrotate.d/cli.rad

%defattr(775, rad, pmta, 775)

%pre
if [ "$1" = "1" ]; then
  if [ `grep -c ^rad /etc/passwd` = "0" ]; then
    /usr/sbin/useradd -c 'RAD User' -d /home/rad -g pmta -M -r -s /bin/false rad
  fi
fi

%post
if [ "$1" = "1" ]; then
  # Perform tasks to prepare for the initial installation
  # echo "Installing rad user environment..."
    
  # copy over the install.ini only the first time
  cp /home/rad/cli/init/install_sample.ini /home/rad/cli/init/install.ini
  
  # Link common cli commands to the cli folder
  ln -s /home/rad/cli/webapp/meta/crons/feeder_daemon.sh /home/rad/cli/cli/auto_feeder.sh
  ln -s /home/rad/cli/webapp/meta/crons/feeder_top_tier_domain_daemon.sh /home/rad/cli/cli/auto_prefeeder.sh
  ln -s /home/rad/cli/webapp/meta/crons/server_status.sh /home/rad/cli/cli/server_status.sh
  ln -s /home/rad/cli/webapp/meta/crons/pmta.sh /home/rad/cli/cli/pmta.sh
  
  echo "Installing RAD for first time use..."
  php /home/rad/cli/init/install.sh silent
  
  echo "Thank you for installing the cli.rad package.  You need to setup"
  echo "PowerMTA and add your API server url to the install.ini file.  A"
  echo "script to install PowerMTA is located in:"
  echo ""
  echo "/home/rad/cli/init/install_pmta.sh"
#elif [ "$1" = "2" ]; then
  # Perform whatever maintenance must occur before the upgrade begins
  # echo "Upgrading rad user environment..."
fi


%postun
#if [ "$1" = "0" ]; then
  # Perform tasks to prepare for the final uninstallation
  # echo "Removing rad user environment..."
#elif [ "$1" = "2" ]; then
  # Perform whatever maintenance must occur before the upgrade begins
  # echo "Removing rad user environment for upgrade..."
#fi