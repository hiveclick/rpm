%define name        bounce.rad
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Provides bounce parsing and postfix syncing for Rad
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: php postfix

%description
Provides bounce parsing and postfix syncing for Rad

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

%defattr(775, rad, postfix, 775)

%config(noreplace) /home/rad/bounce/webapp/config/*
%config(noreplace) /etc/cron.d/bounce.rad

%attr(775, rad, apache) /home/rad/bounce
%attr(644, root, root) /etc/cron.d/bounce.rad

%pre
if [ "$1" = "1" ]; then
  if [ `grep -c ^rad /etc/passwd` = "0" ]; then
    /usr/sbin/useradd -c 'RAD User' -d /home/rad -g postfix -m -s /bin/false rad 2>&1
    /bin/chmod 770 /home/rad
    /bin/chmod g+s /home/rad
  fi
fi

%post
if [ "$1" = "1" ]; then
  # Perform tasks to prepare for the initial installation
  # echo "Installing rad user environment..."
  
  # copy over the install.ini only the first time
  cp /home/rad/bounce/init/install_sample.ini /home/rad/bounce/init/install.ini
  
  echo ""
  echo "    Installing RAD for first time use..."
  php /home/rad/bounce/init/install.sh silent
  
  echo ""
  echo "    Thank you for installing the bounce.rad package.  You may need to"
  echo "    configure Postfix to accept mail from the internet.  All your "
  echo "    domains will be synced to Postfix automatically at night."
  echo ""
#elif [ "$1" = "2" ]; then
fi


%postun
#if [ "$1" = "0" ]; then
#elif [ "$1" = "1" ]; then
#fi