%define name        cli.rad
%define version 	[[VERSION]]
%define dist 	    [[DIST]]

Summary: Provides shared libraries for sending emails using the Rad feeder
Name: %{name}
Version: %{version}
Release: 1%{?dist}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64
Requires: php php-gd PowerMTA shared.rad

%description
Provides shared libraries for sending emails using the Rad feeder

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

%post
php /home/rad/cli/init/install.sh

%postun
rm -f /etc/cron.d/rad
rm -f /etc/logrotate.d/rad