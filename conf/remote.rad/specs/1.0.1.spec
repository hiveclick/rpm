%define name        remote.rad
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Provides remote server setup scripts for GRE tunnels
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: php which nc unix2dos dos2unix php-pecl-ssh2

%description
Provides remote server setup scripts for GRE tunnels

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

%config(noreplace) /home/rad/admin/webapp/config/*
%config(noreplace) /etc/cron.d/rad
%config(noreplace) /etc/logrotate.d/rad

%attr(775, rad, apache) /home/rad/admin
%attr(775, rad, apache) /var/log/rad
%attr(644, root, root) /etc/cron.d/rad
%attr(644, root, root) /etc/logrotate.d/rad

%pre
if [ "$1" = "1" ]; then
  if [ `grep -c ^rad /etc/passwd` = "0" ]; then
    /usr/sbin/useradd -c 'RAD User' -d /home/rad -g apache -m -s /usr/sbin/nologin -p '$1$Ph7VKadV$wANrVQ8fqOLXJHpxd7YBp.' rad 2>&1
    /bin/chmod 770 /home/rad
    /bin/chmod g+s /home/rad
  fi
fi

%post
if [ "$1" = "1" ]; then
  # Perform tasks to prepare for the initial installation
  # echo "Installing rad user environment..."
  
  # copy over the install.ini only the first time
  cp /home/rad/admin/init/install_sample.ini /home/rad/admin/init/install.ini
  
  echo ""
  echo "    Installing RAD for first time use..."
  php /home/rad/admin/init/install.sh silent
  
  echo ""
  echo "    Thank you for installing the unsub.rad package.  You need to setup a"
  echo "    virtual host and add your API server url to the install.ini file.  A"
  echo "    sample virtual host configuration is located in:"
  echo ""
  echo "      /home/rad/admin/init/config/virtualhost"
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/rad/admin/webapp/cache/*
elif [ "$1" = "2" ]; then
  echo "    Applying updates to RAD..."
  php /home/rad/admin/init/upgrade.sh silent
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/rad/admin/webapp/cache/*
fi


%postun
#if [ "$1" = "0" ]; then
#elif [ "$1" = "2" ]; then
#fi