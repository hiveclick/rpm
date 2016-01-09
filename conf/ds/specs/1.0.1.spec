%define name        admin.ds
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Provides an administration site for the DS Site
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: httpd php php-gd php-imap dos2unix php-pecl-ssh2 vsftpd php-pecl-apc php-pdo php-process php-pecl-mongodb php-devel

%description
Provides an administration site for the RPM site

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

#%config(noreplace) /home/ds/admin/webapp/config/*

%attr(775, ds, apache) /home/ds
%attr(775, ds, apache) /var/log/ds

%pre
if [ "$1" = "1" ]; then
  if [ `grep -c ^ds /etc/passwd` = "0" ]; then
    /usr/sbin/useradd -c 'DS User' -d /home/ds -g apache -m -s /usr/sbin/nologin -p '$1$Ph7VKadV$wANrVQ8fqOLXJHpxd7YBp.' ds 2>&1
    /bin/chmod 770 /home/ds
    /bin/chmod g+s /home/ds
  fi
fi

%post
if [ "$1" = "1" ]; then
  # Perform tasks to prepare for the initial installation
  # echo "Installing ds user environment..."
  
  # copy over the install.ini only the first time
  cp /home/ds/init/install_sample.ini /home/ds/init/install.ini
  
  echo ""
  echo "    Installing DS for first time use..."
  php /home/ds/init/install.sh silent
  
  echo ""
  echo "    Thank you for installing the admin.ds package.  You need to setup a"
  echo "    virtual host and add your API server url to the install.ini file.  A"
  echo "    sample virtual host configuration is located in:"
  echo ""
  echo "      /home/ds/init/config/virtualhost"
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/ds/admin/webapp/cache/*
elif [ "$1" = "2" ]; then
  echo "    Applying updates to DS..."
  php /home/ds/init/upgrade.sh silent
  
  # Remove the cache files so new forms and models load correctly
  /bin/rm -Rf /home/ds/webapp/cache/*
fi


%postun
#if [ "$1" = "0" ]; then
#elif [ "$1" = "2" ]; then
#fi