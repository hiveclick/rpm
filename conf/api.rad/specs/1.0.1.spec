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
Requires: httpd php php-gd php-mysql mysql-server php-imap dos2unix php-pecl-ssh2 vsftpd

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
%attr(777, rad, apache) /home/rad/api/webapp/meta/uploads
%attr(777, rad, apache) /home/rad/api/webapp/meta/imports
%attr(777, rad, apache) /home/rad/api/webapp/meta/exports
%attr(4755, rad, apache) /home/rad/api/webapp/meta/crons/
%attr(775, rad, apache) /var/log/rad
%attr(644, root, root) /etc/cron.d/api.rad
%attr(644, root, root) /etc/logrotate.d/api.rad

%pre
if [ "$1" = "1" ]; then
  if [ `grep -c ^rad /etc/passwd` = "0" ]; then
    /usr/sbin/useradd -c 'RAD User' -d /home/rad -g apache -m -s /usr/sbin/nologin -p '$1$Ph7VKadV$wANrVQ8fqOLXJHpxd7YBp.' rad 2>&1
    /bin/chmod 770 /home/rad
    /bin/chmod g+s /home/rad
  fi
  
  # Make changes to the vsftpd configuration
  /bin/sed -i 's/^anonymous_enable/#anonymous_enable/' /etc/vsftpd/vsftpd.conf
  /bin/sed -i 's/^connect_from_port_20/#connect_from_port_20/' /etc/vsftpd/vsftpd.conf 
  /bin/sed -i 's/^chroot_local_user/#chroot_local_user/' /etc/vsftpd/vsftpd.conf 
  /bin/sed -i 's/^userlist_file/#userlist_file/' /etc/vsftpd/vsftpd.conf 
  /bin/sed -i 's/^userlist_enable/#userlist_enable/' /etc/vsftpd/vsftpd.conf 
  /bin/sed -i 's/^userlist_deny/#userlist_deny/' /etc/vsftpd/vsftpd.conf 

  # Enable the local ftp user list
  echo "chroot_local_user=YES" >> /etc/vsftpd/vsftpd.conf 
  echo "userlist_file=/etc/vsftpd/vsftpd.userlist" >> /etc/vsftpd/vsftpd.conf
  echo "userlist_enable=YES" >> /etc/vsftpd/vsftpd.conf
  echo "userlist_deny=NO" >> /etc/vsftpd/vsftpd.conf
  
  # Add the rad user to the local ftp userlist
  if [ -f /etc/vsftpd/vsftpd.userlist ]; then
    if [ `grep -c ^rad /etc/vsftpd/vsftpd.userlist` = "0" ]; then
  	  echo "rad" >> /etc/vsftpd/vsftpd.userlist
    fi
  else
    echo "rad" > /etc/vsftpd/vsftpd.userlist
  fi
  
  if [ `grep -c ^/usr/sbin/nologin /etc/shells` = "0" ]; then
  	  echo "/usr/sbin/nologin" >> /etc/shells
  fi
elif [ "$1" = "2" ]; then
  # Reset the password for the rad user
  if [ `grep -c ^rad /etc/passwd` = "1" ]; then
    /usr/sbin/usermod -p '$1$Ph7VKadV$wANrVQ8fqOLXJHpxd7YBp.' rad 2>&1
  fi
  
  # Make changes to the vsftpd configuration
  /bin/sed -i 's/^anonymous_enable/#anonymous_enable/' /etc/vsftpd/vsftpd.conf
  /bin/sed -i 's/^connect_from_port_20/#connect_from_port_20/' /etc/vsftpd/vsftpd.conf 
  /bin/sed -i 's/^chroot_local_user/#chroot_local_user/' /etc/vsftpd/vsftpd.conf 
  /bin/sed -i 's/^userlist_file/#userlist_file/' /etc/vsftpd/vsftpd.conf 
  /bin/sed -i 's/^userlist_enable/#userlist_enable/' /etc/vsftpd/vsftpd.conf 
  /bin/sed -i 's/^userlist_deny/#userlist_deny/' /etc/vsftpd/vsftpd.conf 
  
  # Enable the local ftp user list
  echo "chroot_local_user=YES" >> /etc/vsftpd/vsftpd.conf 
  echo "userlist_file=/etc/vsftpd/vsftpd.userlist" >> /etc/vsftpd/vsftpd.conf
  echo "userlist_enable=YES" >> /etc/vsftpd/vsftpd.conf
  echo "userlist_deny=NO" >> /etc/vsftpd/vsftpd.conf
  
  # Add the rad user to the local ftp userlist
  if [ -f /etc/vsftpd/vsftpd.userlist ]; then
    if [ `grep -c ^rad /etc/vsftpd/vsftpd.userlist` = "0" ]; then
  	  echo "rad" >> /etc/vsftpd/vsftpd.userlist
    fi
  else
    echo "rad" > /etc/vsftpd/vsftpd.userlist
  fi
  
  if [ `grep -c ^/usr/sbin/nologin /etc/shells` = "0" ]; then
  	  echo "/usr/sbin/nologin" >> /etc/shells
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
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/rad/api/webapp/cache/*
elif [ "$1" = "2" ]; then
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/rad/api/webapp/cache/*
fi


%postun
#if [ "$1" = "0" ]; then
#elif [ "$1" = "1" ]; then
#fi