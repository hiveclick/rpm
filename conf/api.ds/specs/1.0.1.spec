%define name        api.ds
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Provides an api interface to the DS site
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: httpd php php-gd php-mysql mysql-server php-imap dos2unix php-pecl-ssh2 vsftpd php-pecl-apc php-pdo php-process

%description
Provides an api interface to the DS site

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

%defattr(775, ds, apache, 775)

%config(noreplace) /home/ds/api/webapp/config/*
%config(noreplace) /etc/cron.d/api.ds
%config(noreplace) /etc/logrotate.d/api.ds

%attr(775, ds, apache) /home/ds/api
%attr(4755, ds, apache) /home/ds/api/webapp/meta/crons/
%attr(775, ds, apache) /var/log/ds
%attr(644, root, root) /etc/cron.d/api.ds
%attr(644, root, root) /etc/logrotate.d/api.ds

%pre
if [ "$1" = "1" ]; then
  if [ `grep -c ^ds /etc/passwd` = "0" ]; then
    /usr/sbin/useradd -c 'DS User' -d /home/ds -g apache -m -s /usr/sbin/nologin -p '$1$Ph7VKadV$wANrVQ8fqOLXJHpxd7YBp.' ds 2>&1
    /bin/chmod 770 /home/ds
    /bin/chmod g+s /home/ds
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
  
  # Add the ds user to the local ftp userlist
  if [ -f /etc/vsftpd/vsftpd.userlist ]; then
    if [ `grep -c ^ds /etc/vsftpd/vsftpd.userlist` = "0" ]; then
  	  echo "ds" >> /etc/vsftpd/vsftpd.userlist
    fi
  else
    echo "ds" > /etc/vsftpd/vsftpd.userlist
  fi
  
  if [ `grep -c ^/usr/sbin/nologin /etc/shells` = "0" ]; then
  	  echo "/usr/sbin/nologin" >> /etc/shells
  fi
elif [ "$1" = "2" ]; then
  # Reset the password for the ds user
  if [ `grep -c ^ds /etc/passwd` = "1" ]; then
    /usr/sbin/usermod -p '$1$Ph7VKadV$wANrVQ8fqOLXJHpxd7YBp.' ds 2>&1
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
  
  # Add the ds user to the local ftp userlist
  if [ -f /etc/vsftpd/vsftpd.userlist ]; then
    if [ `grep -c ^ds /etc/vsftpd/vsftpd.userlist` = "0" ]; then
  	  echo "ds" >> /etc/vsftpd/vsftpd.userlist
    fi
  else
    echo "ds" > /etc/vsftpd/vsftpd.userlist
  fi
  
  if [ `grep -c ^/usr/sbin/nologin /etc/shells` = "0" ]; then
  	  echo "/usr/sbin/nologin" >> /etc/shells
  fi
fi

%post
if [ "$1" = "1" ]; then
  # Perform tasks to prepare for the initial installation
  # echo "Installing ds user environment..."
  
  # copy over the install.ini only the first time
  cp /home/ds/api/init/install_sample.ini /home/ds/api/init/install.ini
  
  echo ""
  echo "    Installing DS for first time use..."
  php /home/ds/api/init/install.sh silent
  
  echo ""
  echo "    Thank you for installing the api.ds package.  You need to setup a"
  echo "    virtual host.  A sample virtual host configuration is located in:"
  echo ""
  echo "      /home/ds/api/init/config/virtualhost" 
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/ds/api/webapp/cache/*
elif [ "$1" = "2" ]; then
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/ds/api/webapp/cache/*
fi


%postun
#if [ "$1" = "0" ]; then
#elif [ "$1" = "1" ]; then
#fi