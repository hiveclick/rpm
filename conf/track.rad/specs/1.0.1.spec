%define name        track.rad
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Provides a redirect tracking site for the Rad Feeder
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: php httpd php-gd php-mysql mysql-server php-apc php-pdo

%description
Provides a redirect tracking site for the Rad Feeder

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

%config(noreplace) /home/rad/track/webapp/config/*

%attr(775, rad, apache) /home/rad/track
%attr(777, rad, apache) /home/rad/track/webapp/meta/exports
%attr(777, rad, apache) /home/rad/track/webapp/meta/exports/openers
%attr(777, rad, apache) /home/rad/track/webapp/meta/exports/clickers
%attr(644, root, root) /etc/cron.d/track.rad

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
  cp /home/rad/track/init/install_sample.ini /home/rad/track/init/install.ini
  
  echo ""
  echo "    Installing RAD for first time use..."
  php /home/rad/track/init/install.sh silent
  
  echo ""
  echo "    Thank you for installing the track.rad package.  You need to setup a"
  echo "    virtual host and add your API server url to the install.ini file.  A"
  echo "    sample virtual host configuration is located in:"
  echo ""
  echo "      /home/rad/track/init/config/virtualhost"
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/rad/track/webapp/cache/*
elif [ "$1" = "2" ]; then
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/rad/track/webapp/cache/*
fi


%postun
#if [ "$1" = "0" ]; then
#elif [ "$1" = "1" ]; then
#fi