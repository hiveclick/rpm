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
Requires: php PowerMTA

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

%defattr(775, apache, pmta, 775)

%config(noreplace) /home/rad/cli/webapp/config/*
%config(noreplace) /etc/cron.d/cli.rad
%config(noreplace) /etc/logrotate.d/cli.rad

%attr(775, apache, pmta) /home/rad/cli
%attr(775, apache, pmta) /var/log/rad
%attr(644, root, root) /etc/cron.d/cli.rad
%attr(644, root, root) /etc/logrotate.d/cli.rad

%pre
if [ "$1" = "1" ]; then
  if [ `grep -c ^rad /etc/passwd` = "0" ]; then
    /usr/sbin/useradd -c 'RAD User' -d /home/rad -g pmta -m -s /bin/false rad 2>&1
    /bin/chmod 770 /home/rad
    /bin/chmod g+s /home/rad
  fi
fi

%post
if [ "$1" = "1" ]; then
  # Perform tasks to prepare for the initial installation
  # echo "Installing rad user environment..."
    
  # copy over the install.ini only the first time
  cp /home/rad/cli/init/install_sample.ini /home/rad/cli/init/install.ini
  
  # Link common cli commands to the cli folder
  ln -sf /home/rad/cli/webapp/meta/crons/feeder_daemon.sh /home/rad/cli/cli/auto_feeder.sh
  ln -sf /home/rad/cli/webapp/meta/crons/prefeeder_daemon.sh /home/rad/cli/cli/auto_prefeeder.sh
  ln -sf /home/rad/cli/webapp/meta/crons/server_status.sh /home/rad/cli/cli/server_status.sh
  ln -sf /home/rad/cli/webapp/meta/crons/pmta.sh /home/rad/cli/cli/pmta.sh
  
  echo ""
  echo "    Installing RAD for first time use..."
  php /home/rad/cli/init/install.sh silent
  
  echo ""
  echo "    Thank you for installing the cli.rad package.  You need to setup"
  echo "    PowerMTA and add your API server url to the install.ini file.  A"
  echo "    script to install PowerMTA is located in:"
  echo ""
  echo "      /home/rad/cli/init/install_pmta.sh"
  echo ""
  echo "    You can also setup your web interface by copying the virtualhost"
  echo "    file into your Apache directory.  The virtualhost file is located"
  echo "    in:"
  echo ""
  echo "      /home/rad/cli/init/config/virtualhost"
#elif [ "$1" = "2" ]; then
fi


%postun
#if [ "$1" = "0" ]; then
#elif [ "$1" = "2" ]; then
#fi