%define name        zendguard.rad
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Provides Zend Guard capability to RAD components
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64 i386
Requires: php

%description
Provides Zend Guard capability to RAD components

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


%pre

%post

%postun