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

while (($upload_rpm = StringTools::consolePrompt('> Do you want to upload the RPM to the YUM repository? (Y/n):', 'Y')) == '') { }

$spec_file = $VERSION . '.spec';

// Output the introduction
$intro = 'This script will build the RPM for the ' . StringTools::consoleColor($settings['name'], StringTools::CONSOLE_COLOR_YELLOW) . ' project';
echo $intro . "\n";

$cmd = 'svn info ' . $settings['revision_url'] . ' | grep "Revision: " | awk \'{print $2}\'';
$revision = intval(trim(shell_exec($cmd)));

$base_dir = $BUILDDIR . '/SOURCES/' . $BASENAME . '-' . $VERSION;

// Extract the subversion files
foreach ($settings['subversion'] as $key => $svn_array) {
	echo "Working on " . $key . "\n";
	$source_folder = $base_dir . $svn_array[1];
	echo " - Exporting to: " . $source_folder . "\n";
	if (file_exists($source_folder)) {
		$cmd = 'rm -Rf ' . $source_folder;
		passthru($cmd);
	}
	if (!file_exists($source_folder)) {
		$cmd = 'mkdir -p ' . $source_folder;
		passthru($cmd);
	}
	echo " - Exporting url: " . $svn_array[0] . "\n";
	$cmd = 'svn export --force ' . $svn_array[0] . ' ' . $source_folder;
	passthru($cmd);
}

// Extract the support files
foreach ($settings['support_files'] as $key => $files) {
	echo "Working on " . $key . "\n";
	if (file_exists($base_dir . $settings['root_folder'] . '/' . $files[0])) {
		echo " - Exporting to: " . $base_dir . $files[1] . "\n";
		$source_folder = dirname($base_dir . $files[1]);
		if (!file_exists($source_folder)) {
			$cmd = 'mkdir -p ' . $source_folder;
			passthru($cmd);
		}
		$cmd = 'cp ' . $base_dir . $settings['root_folder'] . '/' . $files[0] . ' ' . $base_dir . $files[1];
		passthru($cmd);
	} else {
		echo ' - Source file does not exist: ' . $base_dir . $settings['root_folder'] . $files[0] . "\n";
		die();
	}
}

// Extract the support folders
foreach ($settings['support_folders'] as $key => $folder_name) {
	echo "Working on " . $key .  " => " . $folder_name[0] . "\n";
	$source_folder = $base_dir . $folder_name[0];
	if (!file_exists($source_folder)) {
		$cmd = 'mkdir -p ' . $source_folder;
		passthru($cmd);
	}
}

// Remove the install.ini file
$install_source_file = $base_dir . $settings['root_folder'] . '/init/install.ini';
if (file_exists($install_source_file)) {
	$cmd = 'rm -f ' . $install_source_file;
	shell_exec($cmd);
}

if (isset($settings['use_zend_guard']) && ($settings['use_zend_guard'] == 1)) {
	// Use Zend Guard to encode this project
	$cmd = '/usr/local/Zend/ZendGuard-5_5_0/plugins/com.zend.guard.core.resources.linux.x86_5.5.0/resources/bin/zendenc53 --delete-source --short-tags on --expires 2012-07-01 --recursive --ignore-errors ' . $base_dir;
	shell_exec($cmd);
}

if (file_exists(dirname(__FILE__) . '/conf/' . $conf_dir . '/specs/' . $spec_file)) {
	$spec = file_get_contents(dirname(__FILE__) . '/conf/' . $conf_dir . '/specs/' . $spec_file);
	$spec = str_replace('[[VERSION]]', $VERSION, $spec);
	$spec = str_replace('[[REVISION]]', $revision, $spec);
	$spec = str_replace('[[BUILDDIR]]', $BUILDDIR, $spec);
	file_put_contents($BUILDDIR . '/SPECS/' . $BASENAME . '-' . $spec_file, $spec);
}



echo ' - Tar/Gzipping' . "\n";

$cmd = 'tar -cPf ' . $BASENAME . '-' . $VERSION . '.tar ' . ' -C ' . dirname($base_dir) . ' ' . basename($base_dir);
echo $cmd . "\n";
passthru($cmd);

$cmd = 'gzip -f ' . $BASENAME . '-' . $VERSION . '.tar';
echo $cmd . "\n";
passthru($cmd);

$cmd = 'cp ' . $BASENAME . '-' . $VERSION . '.tar.gz' . ' ' . '/usr/src/redhat/SOURCES';
passthru($cmd);

$cmd = 'rpmbuild -ba ' . $BUILDDIR . '/SPECS/' . $BASENAME . '-' . $spec_file;
echo $cmd . "\n";
passthru($cmd);

$cmd = 'cp -Rf /usr/src/redhat/RPMS/noarch/*.rpm ' . $BUILDDIR . '/RPMS/';
passthru($cmd);

if (strtoupper(trim($upload_rpm)) == 'Y') {
	echo "Removing older revisions..." . "\n";
	$cmd = 'ssh root@yum.radinteractive.net rm -f /var/www/sites/yum/CentOS/5/local/*/RPMS/' . $BASENAME . '*';
	passthru($cmd);
	
	echo "Uploading new revisions..." . "\n";
	$cmd = 'scp ' . $BUILDDIR . '/RPMS/' . $BASENAME . '-' . $VERSION . '-' . $revision . '.noarch.rpm root@yum.radinteractive.net:/var/www/sites/yum/CentOS/5/local/x86_64/RPMS/';
	passthru($cmd);
	$cmd = 'scp ' . $BUILDDIR . '/RPMS/' . $BASENAME . '-' . $VERSION . '-' . $revision . '.noarch.rpm root@yum.radinteractive.net:/var/www/sites/yum/CentOS/5/local/noarch/RPMS/';
	passthru($cmd);
	$cmd = 'scp ' . $BUILDDIR . '/RPMS/' . $BASENAME . '-' . $VERSION . '-' . $revision . '.noarch.rpm root@yum.radinteractive.net:/var/www/sites/yum/CentOS/5/local/i386/RPMS/';
	passthru($cmd);
	
	echo "Rebuilding Repositories..." . "\n";	
	$cmd = 'ssh root@yum.radinteractive.net createrepo /var/www/sites/yum/CentOS/5/local/x86_64/';
	passthru($cmd);
	$cmd = 'ssh root@yum.radinteractive.net createrepo /var/www/sites/yum/CentOS/5/local/noarch/';
	passthru($cmd);
	$cmd = 'ssh root@yum.radinteractive.net createrepo /var/www/sites/yum/CentOS/5/local/i386/';
	passthru($cmd);	
	
	echo 'Done building ' . $BASENAME . ' rpm' . "\n";
} else {
	echo 'RPM built in ' . $BUILDDIR . '/RPMS/' . "\n";
	passthru('ls -lh ' . $BUILDDIR . '/RPMS/');
}
?>