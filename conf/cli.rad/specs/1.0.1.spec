%define name        cli.rad
%define version 	[[VERSION]]
%define revision	[[REVISION]]
%define debug_package %{nil}

Summary: Provides shared libraries for sending emails using the Rad feeder
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: php PowerMTA nc unix2dos php-gd php-process php-cli spamassassin

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
  
  # Make changes to the sudoers configuration
  if [ -f /etc/sudoers ]; then
    /bin/sed -i 's/^Defaults *requiretty/#Defaults    requiretty/' /etc/sudoers
    if [ `grep -c "^apache  ALL=NOPASSWD: PMTA" /etc/sudoers` = "0" ]; then
      echo "## Pmta" >> /etc/sudoers
      echo "Cmnd_Alias PMTA = /usr/sbin/pmta, /etc/init.d/pmta, /sbin/ifconfig, /sbin/ip, /sbin/arping, /home/rad/cli/webapp/meta/crons/pmta.sh, /home/rad/cli/webapp/meta/crons/test_ips.sh, /home/rad/cli/webapp/meta/crons/move_eth_file.sh" >> /etc/sudoers
      echo "apache  ALL=NOPASSWD: PMTA" >> /etc/sudoers
    else
      /bin/sed -i 's/^Cmnd_Alias PMTA.*/Cmnd_Alias PMTA = \/usr\/sbin\/pmta, \/etc\/init.d\/pmta, \/sbin\/ifconfig, \/sbin\/ip, \/sbin\/arping, \/home\/rad\/cli\/webapp\/meta\/crons\/pmta.sh, \/home\/rad\/cli\/webapp\/meta\/crons\/test_ips.sh, \/home\/rad\/cli\/webapp\/meta\/crons\/move_eth_file.sh/' /etc/sudoers
    fi
  fi	  
elif [ "$1" = "2" ]; then
  # Make changes to the sudoers configuration
  if [ -f /etc/sudoers ]; then
    /bin/sed -i 's/^Defaults *requiretty/#Defaults    requiretty/' /etc/sudoers
    if [ `grep -c "^apache  ALL=NOPASSWD: PMTA" /etc/sudoers` = "0" ]; then
      echo "## Pmta" >> /etc/sudoers
      echo "Cmnd_Alias PMTA = /usr/sbin/pmta, /etc/init.d/pmta, /sbin/ifconfig, /sbin/ip, /sbin/arping, /home/rad/cli/webapp/meta/crons/pmta.sh, /home/rad/cli/webapp/meta/crons/test_ips.sh, /home/rad/cli/webapp/meta/crons/move_eth_file.sh" >> /etc/sudoers
      echo "apache  ALL=NOPASSWD: PMTA" >> /etc/sudoers
    else
      /bin/sed -i 's/^Cmnd_Alias PMTA.*/Cmnd_Alias PMTA = \/usr\/sbin\/pmta, \/etc\/init.d\/pmta, \/sbin\/ifconfig, \/sbin\/ip, \/sbin\/arping, \/home\/rad\/cli\/webapp\/meta\/crons\/pmta.sh, \/home\/rad\/cli\/webapp\/meta\/crons\/test_ips.sh, \/home\/rad\/cli\/webapp\/meta\/crons\/move_eth_file.sh/' /etc/sudoers
    fi
  fi
  
  # Verify the folders exist
  if [ ! -d /home/rad/cli/webapp/meta/drop/bad ]; then
  	mkdir -p /home/rad/cli/webapp/meta/drop/bad
  	chown apache:pmta /home/rad/cli/webapp/meta/drop/bad
  	chmod 775 /home/rad/cli/webapp/meta/drop/bad
  fi
  if [ ! -d /home/rad/cli/webapp/meta/drop/pending ]; then
  	mkdir -p /home/rad/cli/webapp/meta/drop/pending
  	chown apache:pmta /home/rad/cli/webapp/meta/drop/pending
  	chmod 775 /home/rad/cli/webapp/meta/drop/pending
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
  host=`echo $HOSTNAME`
  
  /bin/cp /home/rad/cli/init/config/virtualhost /etc/httpd/conf.d/cli.rad.conf
  /bin/sed -i "s/cli\.localhost/$host/g" /etc/httpd/conf.d/cli.rad.conf

elif [ "$1" = "2" ]; then
  # Verify the folders exist
  if [ ! -d /home/rad/cli/webapp/meta/drop/bad ]; then
  	mkdir -p /home/rad/cli/webapp/meta/drop/bad
  	chown apache:pmta /home/rad/cli/webapp/meta/drop/bad
  	chmod 775 /home/rad/cli/webapp/meta/drop/bad
  fi
  if [ ! -d /home/rad/cli/webapp/meta/drop/pending ]; then
  	mkdir -p /home/rad/cli/webapp/meta/drop/pending
  	chown apache:pmta /home/rad/cli/webapp/meta/drop/pending
  	chmod 775 /home/rad/cli/webapp/meta/drop/pending
  fi
fi


%postun
#if [ "$1" = "0" ]; then
#elif [ "$1" = "2" ]; then
#fi
