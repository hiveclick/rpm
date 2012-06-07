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

%defattr(775, rad, apache, 775)

%config(noreplace) /home/rad/api/webapp/config/*
%config(noreplace) /etc/cron.d/api.rad
%config(noreplace) /etc/logrotate.d/api.rad

%attr(775, rad, apache) /home/rad/api
%attr(775, rad, apache) /var/log/rad
%attr(644, root, root) /etc/cron.d/api.rad
%attr(644, root, root) /etc/logrotate.d/api.rad

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
  cp /home/rad/api/init/install_sample.ini /home/rad/api/init/install.ini
  
  echo ""
  echo "    Installing RAD for first time use..."
  php /home/rad/api/init/install.sh silent
  
  echo ""
  echo "    Thank you for installing the api.rad package.  You need to setup a"
  echo "    virtual host.  A sample virtual host configuration is located in:"
  echo ""
  echo "      /home/rad/api/init/config/virtualhost" 
#elif [ "$1" = "2" ]; then
fi


%postun
#if [ "$1" = "0" ]; then
#elif [ "$1" = "1" ]; then
#fi