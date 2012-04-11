%define name        rad
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Provides an administration site for the Rad Feeder
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
Provides an administration site for the Rad Feeder

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

%config
/home/rad/admin/init/install.ini

%post
if [ "$1" = "1" ]; then
  # Perform tasks to prepare for the initial installation
  echo "Installing rad user environment..."
  if [ "$(grep "rad" /etc/passwd | wc -l)" -eq 0 ]; then
  	useradd -g apache -M -r -s /bin/false rad
  fi
  
  # Create the log folder for rad
  if [ ! -d "/var/log/rad" ]; then
	  mkdir /var/log/rad
	  chown rad:apache /var/log/rad
	  chmod 775 /var/log/rad
  fi
  
  echo "Installing RAD for first time use..."
  php /home/rad/admin/init/install.sh silent
  
  # Copy the virtual host to apache so stuff works
  cp -f /home/rad/admin/init/config/virtualhost /etc/httpd/conf.d/rad.vhost.conf
  
  # Copy the logrotate.d so that we can rotate our logs
  cp -f /home/rad/admin/init/config/logrotate /etc/logrotate.d/rad

elif [ "$1" = "2" ]; then
  # Perform whatever maintenance must occur before the upgrade begins
  echo "Upgrading rad user environment..."
  
  # Create the log folder for rad
  if [ ! -d "/var/log/rad" ]; then
	  mkdir /var/log/rad
	  chown rad:apache /var/log/rad
	  chmod 775 /var/log/rad
  fi
  
  if [ -d "/home/rad/admin" ]; then
	  chown rad:apache /home/rad/admin
	  chmod 775 /home/rad/admin
  fi
  
  # Copy the virtual host to apache so stuff works
  rm -f /etc/httpd/conf.d/rad.vhost.conf
  cp -f /home/rad/admin/init/config/virtualhost /etc/httpd/conf.d/rad.vhost.conf
  
  # Copy the logrotate.d so that we can rotate our logs
  rm -f /etc/logrotate.d/rad
  cp -f /home/rad/admin/init/config/logrotate /etc/logrotate.d/rad

fi


%postun
if [ "$1" = "0" ]; then
  # Perform tasks to prepare for the final uninstallation
  echo "Removing rad user environment..."
  rm -f /etc/logrotate.d/rad
  rm -Rf /var/log/rad
elif [ "$1" = "2" ]; then
  # Perform whatever maintenance must occur before the upgrade begins
  echo "Upgrading rad user environment..."
fi