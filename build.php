<?php
include_once(dirname(__FILE__) . '/lib/StringTools.class.php');

$BUILDDIR = '/home/buildrpm';

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

while (($spec_file = StringTools::consolePrompt('> Select a spec version to load (enter for a list):')) == '') {
	$spec_conf_files = scandir($app_dir . '/specs');
	foreach ($spec_conf_files as $spec_conf_file) {
		if (strpos($spec_conf_file, '.') === 0) { continue; }
		echo StringTools::consoleColor(' * ' . $spec_conf_file, StringTools::CONSOLE_COLOR_GREEN) . "\n";	
	}
}

$VERSION = str_replace('.spec', '', $spec_file);


$intro = 'This script will build the RPM for the ' . StringTools::consoleColor($settings['name'], StringTools::CONSOLE_COLOR_YELLOW) . ' project';
echo $intro . "\n";

$svn_url_array['cli.rad'] = array(
	'url' => 'http://svn.radinteractive.net/repos/rad/cli.rad/trunk',
	'dest_folder' => '/var/www/sites/cli.rad/'
);
$svn_url_array['dao.rad'] = array(
	'url' => 'http://svn.radinteractive.net/repos/rad/dao.rad/trunk',
	'dest_folder' => '/var/www/sites/cli.rad/webapp/modules'
);
$svn_url_array['common'] = array(
	'url' => 'http://svn.radinteractive.net/repos/common/common/trunk/mojavi',
	'dest_folder' => '/var/www/sites/cli.rad/webapp/lib/mojavi'
);

foreach ($svn_url_array as $key => $svn_array) {
	echo "Working on " . $key . "\n";
	$source_folder = $BUILDDIR . '/SOURCES/' . $BASENAME . '-' . $VERSION . $svn_array['dest_folder'];
	echo " - Exporting to: " . $source_folder . "\n";
	if (!file_exists($source_folder)) {
		$cmd = 'mkdir -p ' . $source_folder;
		passthru($cmd);
	}
	echo " - Exporting url: " . $svn_array['url'] . "\n";
	$cmd = 'svn export --force ' . $svn_array['url'] . ' ' . $source_folder;
	passthru($cmd);
}

echo 'Removing RPM folder' . "\n";
$cmd = 'rm -Rf ' . $BUILDDIR . '/SOURCES/' . $BASENAME . '-' . $VERSION . 'rpm';
shell_exec($cmd);

if (file_exists(dirname(__FILE__) . '/rpm.spec')) {
	$spec = file_get_contents($app_dir . '/specs/' . $spec_file);
	$spec = str_replace('[[VERSION]]', $VERSION, $spec);
	$spec = str_replace('[[RELEASE]]', $RELEASE, $spec);
	file_put_contents($BUILDDIR . '/SPECS/' . $BASENAME . '-' . $spec_file, $spec);
}

echo ' - Tar/Gzipping' . "\n";
chdir($BUILDDIR . '/SOURCES/');
$cmd = 'tar -cf ' . $BASENAME . '-' . $VERSION . '-.tar ' . $BASENAME . '-' . $VERSION;
passthru($cmd);
$cmd = 'gzip ' . $BASENAME . '-' . $VERSION . '.tar';
passthru($cmd);

$cmd = 'rpmbuild -ba ' . $BUILDDIR . '/SPECS/' . $BASENAME . '-' . $spec_file;
passthru($cmd);

echo 'RPM built in ' . $BUILDDIR . '/RPMS/noarch/' . "\n";
passthru('ll -h ' . $BUILDDIR . '/RPMS/noarch/');
?>