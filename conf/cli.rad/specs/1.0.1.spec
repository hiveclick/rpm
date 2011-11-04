%define name        cli.rad
%define version 	[[VERSION]]
%define revision	[[REVISION]]

Summary: Provides shared libraries for sending emails using the Rad feeder
Name: %{name}
Version: %{version}
Release: %{revision}
Group: Applications/Internet
License: commercial
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-buildroot
BuildArch: noarch x86_64
Requires: php php-gd PowerMTA

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
if [ "$1" = "1" ]; then
  # Perform tasks to prepare for the initial installation
  echo "Installing rad user environment..."
  useradd -g pmta -M -s /bin/false rad
  echo "Installing RAD for first time use..."
  php /home/rad/cli/init/install.sh
elif [ "$1" = "2" ]; then
  # Perform whatever maintenance must occur before the upgrade begins
  echo "Upgrading rad user environment..."
fi


%postun
if [ "$1" = "0" ]; then
  # Perform tasks to prepare for the final uninstallation
  echo "Removing rad user environment..."
  rm -f /etc/cron.d/rad
  rm -f /etc/logrotate.d/rad
  userdel -r rad
elif [ "$1" = "2" ]; then
  # Perform whatever maintenance must occur before the upgrade begins
  echo "Upgrading rad user environment..."
fi