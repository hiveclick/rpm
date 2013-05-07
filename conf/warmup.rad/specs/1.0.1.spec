%define name        warmup.rad
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Provides shared libraries for warming ips using the Rad platform
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: php PowerMTA nc unix2dos php-gd

%description
Provides shared libraries for warming ips using the Rad platform

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

%config(noreplace) /home/rad/warmup/webapp/config/*
%config(noreplace) /etc/cron.d/warmup.rad
%config(noreplace) /etc/logrotate.d/warmup.rad

%attr(775, apache, pmta) /home/rad/warmup
%attr(775, apache, pmta) /var/log/rad
%attr(644, root, root) /etc/cron.d/warmup.rad
%attr(644, root, root) /etc/logrotate.d/warmup.rad

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
  cp /home/rad/warmup/init/install_sample.ini /home/rad/warmup/init/install.ini
  
  # Link common warmup commands to the cli folder
  ln -sf /home/rad/warmup/webapp/meta/crons/pmta.sh /home/rad/warmup/cli/pmta.sh
  
  echo ""
  echo "    Installing RAD for first time use..."
  php /home/rad/warmup/init/install.sh silent
  
  echo ""
  echo "    Thank you for installing the cli.rad package.  You need to setup"
  echo "    PowerMTA and add your API server url to the install.ini file.  A"
  echo "    script to install PowerMTA is located in:"
  echo ""
  echo "      /home/rad/warmup/init/install_pmta.sh"
  echo ""
  echo "    You can also setup your web interface by copying the virtualhost"
  echo "    file into your Apache directory.  The virtualhost file is located"
  echo "    in:"
  echo ""
  echo "      /home/rad/warmup/init/config/virtualhost"
#elif [ "$1" = "2" ]; then
fi


%postun
#if [ "$1" = "0" ]; then
#elif [ "$1" = "2" ]; then
#fi