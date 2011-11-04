<?php
include_once(dirname(__FILE__) . '/lib/StringTools.class.php');

$BUILDDIR = dirname(__FILE__) . '/build';

while (($conf_dir = StringTools::consolePrompt('> Select a configuration to load (enter for a list):')) == '') {
	$conf_folders = scandir(dirname(__FILE__) . '/conf/');
	foreach ($conf_folders as $conf_folder) {
		if (strpos($conf_folder, '.') === 0) { continue; }
		echo StringTools::consoleColor(' * ' . $conf_folder, StringTools::CONSOLE_COLOR_GREEN) . "\n";	
	}
}

$app_dir = dirname(__FILE__) . '/conf/' . $conf_dir;
if (file_exists($app_dir . '/settings.ini')) {
	$settings = parse_ini_file($app_dir . '/settings.ini', true);
	$BASENAME = $settings['name'];
} else {
	echo StringTools::consoleColor('We cannot find a settings.ini file in the conf/' . $conf_dir . ' folder', StringTools::CONSOLE_COLOR_RED) . "\n";
	exit;
}

while (($VERSION = StringTools::consolePrompt('> Select a spec version to load (enter for a list):')) == '') {
	$spec_conf_files = scandir($app_dir . '/specs');
	foreach ($spec_conf_files as $spec_conf_file) {
		if (strpos($spec_conf_file, '.') === 0) { continue; }
		echo StringTools::consoleColor(' * ' . str_replace('.spec', '', $spec_conf_file), StringTools::CONSOLE_COLOR_GREEN) . "\n";	
	}
}

$spec_file = $VERSION . '.spec';


$intro = 'This script will build the RPM for the ' . StringTools::consoleColor($settings['name'], StringTools::CONSOLE_COLOR_YELLOW) . ' project';
echo $intro . "\n";

$cmd = 'svn info ' . $settings['revision_url'] . ' | grep "Revision: " | awk \'{print $2}\'';
$revision = intval(trim(shell_exec($cmd)));

foreach ($settings['subversion'] as $key => $svn_array) {
	echo "Working on " . $key . "\n";
	$source_folder = $BUILDDIR . '/SOURCES/' . $BASENAME . '-' . $VERSION . $svn_array[1];
	echo " - Exporting to: " . $source_folder . "\n";
	if (!file_exists($source_folder)) {
		$cmd = 'mkdir -p ' . $source_folder;
		passthru($cmd);
	}
	echo " - Exporting url: " . $svn_array[0] . "\n";
	$cmd = 'svn export --force ' . $svn_array[0] . ' ' . $source_folder;
	passthru($cmd);
}

foreach ($settings['support_files'] as $key => $files) {
	echo "Working on " . $key . "\n";
	if (file_exists($BUILDDIR . '/SOURCES/' . $BASENAME . '-' . $VERSION . $settings['root_folder'] . $files[0])) {
		echo " - Exporting to: " . $BUILDDIR . '/SOURCES/' . $BASENAME . '-' . $VERSION . $files[1] . "\n";
		$source_folder = dirname($BUILDDIR . '/SOURCES/' . $BASENAME . '-' . $VERSION . $files[1]);
		if (!file_exists($source_folder)) {
			$cmd = 'mkdir -p ' . $source_folder;
			passthru($cmd);
		}
		$cmd = 'cp ' . $BUILDDIR . '/SOURCES/' . $BASENAME . '-' . $VERSION . $settings['root_folder'] . $files[0] . ' ' . $BUILDDIR . '/SOURCES/' . $BASENAME . '-' . $VERSION . $files[1];
		passthru($cmd);
	}
}

if (file_exists(dirname(__FILE__) . '/conf/' . $conf_dir . '/specs/' . $spec_file)) {
	$spec = file_get_contents(dirname(__FILE__) . '/conf/' . $conf_dir . '/specs/' . $spec_file);
	$spec = str_replace('[[VERSION]]', $VERSION, $spec);
	$spec = str_replace('[[DIST]]', $revision, $spec);
	$spec = str_replace('[[BUILDDIR]]', $BUILDDIR, $spec);
	file_put_contents($BUILDDIR . '/SPECS/' . $BASENAME . '-' . $spec_file, $spec);
}

echo ' - Tar/Gzipping' . "\n";

$cmd = 'tar -cPf ' . $BASENAME . '-' . $VERSION . '.tar ' . ' -C ' . $BUILDDIR . '/SOURCES/ ' . $BASENAME . '-' . $VERSION;
echo $cmd . "\n";
passthru($cmd);

$cmd = 'gzip ' . $BASENAME . '-' . $VERSION . '.tar';
echo $cmd . "\n";
passthru($cmd);

$cmd = 'cp ' . $BASENAME . '-' . $VERSION . '.tar.gz' . ' ' . '/usr/src/redhat/SOURCES';
passthru($cmd);

$cmd = 'rpmbuild -ba ' . $BUILDDIR . '/SPECS/' . $BASENAME . '-' . $spec_file;
echo $cmd . "\n";
passthru($cmd);

$cmd = 'cp -Rf /usr/src/redhat/RPMS/noarch/*.rpm ' . $BUILDDIR . '/RPMS/';
passthru($cmd);

while (($upload_rpm = StringTools::consolePrompt('> Do you want to upload the RPM to the YUM repository? (Y/n):', 'Y')) == '') { }
if (strtoupper(trim($upload_rpm)) == 'Y') {
	$cmd = 'scp ' . $BUILDDIR . '/RPMS/' . $BASENAME . '-' . $VERSION . '-1' . $revision . '.noarch.rpm root@core1.krypt.com:/var/www/sites/yum/CentOS/5/local/x86_64/RPMS/';
	passthru($cmd);
	$cmd = 'scp ' . $BUILDDIR . '/RPMS/' . $BASENAME . '-' . $VERSION . '-1' . $revision . '.noarch.rpm root@core1.krypt.com:/var/www/sites/yum/CentOS/5/local/noarch/RPMS/';
	passthru($cmd);
	echo "\n\n" . 'Run the following command to recompile your YUM repository:' . "\n" . 'createrepo /var/www/sites/yum/CentOS/5/local/x86_64/' . "\n" . 'createrepo /var/www/sites/yum/CentOS/5/local/noarch/' . "\n";
} else {
	echo 'RPM built in ' . $BUILDDIR . '/RPMS/' . "\n";
	passthru('ls -lh ' . $BUILDDIR . '/RPMS/');
}
?>