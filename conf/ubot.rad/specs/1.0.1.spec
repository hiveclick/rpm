%define name        ubot.rad
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Provides simple pages for modifying parts of the site via uBot Studio
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: api.rad

%description
Provides simple pages for modifying parts of the site via uBot Studio

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

%config(noreplace) /home/rad/ubot/webapp/config/*
%config(noreplace) /etc/cron.d/ubot.rad
%config(noreplace) /etc/logrotate.d/ubot.rad

%attr(775, rad, apache) /home/rad/ubot
%attr(775, rad, apache) /var/log/rad
%attr(644, root, root) /etc/cron.d/ubot.rad
%attr(644, root, root) /etc/logrotate.d/ubot.rad

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
  cp /home/rad/ubot/init/install_sample.ini /home/rad/ubot/init/install.ini
  
  echo ""
  echo "    Installing RAD for first time use..."
  php /home/rad/ubot/init/install.sh silent
  
  echo ""
  echo "    Thank you for installing the ubot.rad package.  You need to setup a"
  echo "    virtual host and add your API server url to the install.ini file.  A"
  echo "    sample virtual host configuration is located in:"
  echo ""
  echo "      /home/rad/ubot/init/config/virtualhost"
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/rad/ubot/webapp/cache/*
elif [ "$1" = "2" ]; then
  echo "    Applying updates to RAD..."
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/rad/ubot/webapp/cache/*
fi


%postun
#if [ "$1" = "0" ]; then
#elif [ "$1" = "2" ]; then
#fi