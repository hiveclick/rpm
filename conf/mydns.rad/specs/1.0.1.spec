%define name        mydns.rad
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Provides a MyDNS console for use in the RAD environment
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: remi-release mysql-server php php-mysql httpd mydns mydns-mysql

%description
Provides a MyDNS console for use in the RAD environment

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
%config(noreplace) /home/rad/mydns/webapp/config/*
%config(noreplace) /etc/cron.d/mydns.rad

%attr(775, rad, apache) /home/rad/mydns
%attr(644, root, root) /etc/cron.d/mydns.rad

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
  cp /home/rad/mydns/init/install_sample.ini /home/rad/mydns/init/install.ini
  
  echo ""
  echo "    Installing RAD for first time use..."
  
  chkconfig mydns on
  chkconfig mysqld on
  chkconfig httpd on
  
  echo ""
  echo "    Thank you for installing the mydns.rad package.  You need to setup a"
  echo "    virtual host.  A sample virtual host configuration is located in:"
  echo ""
  echo "      /home/rad/mydns/init/config/virtualhost"
  echo ""
  echo "    You also need to configure MyDNS on this server.  You can do this by"
  echo "    following the steps here:"
  echo ""
  echo "      /home/rad/mydns/INSTALL.txt"
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/rad/mydns/webapp/cache/*
elif [ "$1" = "2" ]; then
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/rad/mydns/webapp/cache/*
fi


%postun
#if [ "$1" = "0" ]; then
#elif [ "$1" = "2" ]; then
#fi