%define name        cli.rad
%define release		1
%define version 	1.0.1

Summary: Provides shared libraries for sending emails using the Rad feeder
Name: cli.rad
Version: ${version}
Release: 1%{?dist}
Group: Applications/Internet
License: commercial
Source: %{name}-${version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch

%description
Provides shared libraries for sending emails using the Rad feeder

%prep
%setup -q

%build

%install
cp -rvf \$RPM_BUILD_DIR/%{name}-${version} \$RPM_BUILD_ROOT

%clean
if( [ \$RPM_BUILD_ROOT != '/' ] ); then rm -rf \$RPM_BUILD_ROOT; fi;

%files
/.

%post
echo "CLI Feeder has been installed in $DESTLOC";
