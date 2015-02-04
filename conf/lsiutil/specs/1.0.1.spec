%define name        lsiutil
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Installs the lsiutil script used to manage LSI RAID controllers on Dell C6100 servers
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: x86_64

%description
Installs the lsiutil script used to manage LSI RAID controllers on Dell C6100 servers

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

%postun