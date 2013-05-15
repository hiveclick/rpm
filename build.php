<?php
try {
	set_include_path(dirname(__FILE__) . '/lib' . PATH_SEPARATOR . get_include_path());
	require_once(dirname(__FILE__) . '/lib/Zend/Loader/Autoloader.php');
	$autoloader = Zend_Loader_Autoloader::getInstance();
	$autoloader->registerNamespace('Rad_');
	
	$BUILDDIR = dirname(__FILE__) . '/build';
	
	// Load the configuration file
	if (!file_exists(dirname(__FILE__) . '/conf/rad.ini')) {
		throw new Exception('We cannot find the conf/rad.ini configuration file.  Please create one before configuring a tunnel.');
	} else {
		$ini_settings = parse_ini_file(dirname(__FILE__) . '/conf/rad.ini', true);
		if (isset($ini_settings['api_server'])) {
			$api_url = $ini_settings['api_server'];
		} else {
			throw new Exception('The api server is not set in your conf/rad.ini file.');
		}
	}
	
	// Select which component we want to use
	while (($conf_dir = Rad_StringTools::consolePrompt('> Select a configuration to load (enter for a list):')) == '') {
		$conf_folders = scandir(dirname(__FILE__) . '/conf/');
		foreach ($conf_folders as $conf_folder) {
			if (strpos($conf_folder, '.') === 0) { continue; }
			echo Rad_StringTools::consoleColor(' * ' . $conf_folder, Rad_StringTools::CONSOLE_COLOR_GREEN) . "\n";	
		}
	}
	
	// Look for a configuration file (settings.ini) 
	$app_dir = dirname(__FILE__) . '/conf/' . $conf_dir;
	if (file_exists($app_dir . '/settings.ini')) {
		$settings = parse_ini_file($app_dir . '/settings.ini', true);
		$BASENAME = $settings['name'];
	} else {
		throw new Exception('We cannot find a settings.ini file in the conf/' . $conf_dir . ' folder');
	}
	
	// Load a spec version (mostly this will be 1.0.1)
	while (($VERSION = Rad_StringTools::consolePrompt('> Select a spec version to load (enter for a list):', '1.0.1')) == '') {
		$spec_conf_files = scandir($app_dir . '/specs');
		foreach ($spec_conf_files as $spec_conf_file) {
			if (strpos($spec_conf_file, '.') === 0) { continue; }
			echo Rad_StringTools::consoleColor(' * ' . str_replace('.spec', '', $spec_conf_file), Rad_StringTools::CONSOLE_COLOR_GREEN) . "\n";	
		}
	}
	
	while (($upload_rpm = Rad_StringTools::consolePrompt('> Do you want to upload the RPM to the YUM repository? (Y/n):', 'Y')) == '') { }
	
	$spec_file = $VERSION . '.spec';
	
	// Output the introduction
	$intro = array();
	$intro[] = 'This script will build the RPM for the ' . Rad_StringTools::consoleColor($settings['name'], Rad_StringTools::CONSOLE_COLOR_YELLOW) . ' project';
	$intro[] = '  Api Url: ' . $api_url;
	echo implode("\n", $intro) . "\n";
	
	
	
	// We need to procure a new version number from the database
	
	
	//$cmd = 'svn info ' . $settings['revision_url'] . ' | grep "Revision: " | awk \'{print $2}\'';
	//$revision = intval(trim(shell_exec($cmd)));
	//
	//// Grab our log contents so we can post the release notes to the version server
	//if (file_exists(dirname(__FILE__) . '/conf/' . $conf_dir . '/.svn_version')) {
	//	$old_revision = trim(file_get_contents(dirname(__FILE__) . '/conf/' . $conf_dir . '/.svn_version'));
	//	echo "1 - Getting Revision History for " . $old_revision . " to " . $revision . "\n";
	//	$cmd = 'svn log ' . $settings['revision_url'] . ' -r ' . $old_revision . ':' . $revision . ' --xml';
	//	$log_contents = shell_exec($cmd);
	//} else {
	//	$cmd = 'svn info ' . $settings['revision_url'] . ' | grep "Last Changed Rev: " | awk \'{print $4}\'';
	//	$last_changed_revision = intval(trim(shell_exec($cmd)));
	//	echo "2 - Getting Revision History for " . $last_changed_revision . " to " . $revision . "\n";
	//	$cmd = 'svn log ' . $settings['revision_url'] . ' -r ' . $last_changed_revision . ':' . $revision . ' --xml';
	//	$log_contents = shell_exec($cmd);
	//}
	
	//$log_buffer = array();
	//if (trim($log_contents) != '') {
	//	$xml = simplexml_load_string($log_contents);
	//	if (count($xml->logentry) > 0) {
	//		foreach ($xml->logentry as $log_entry) {
	//			$log_buffer[] = $log_entry['revision'] . ": " . $log_entry->msg;
	//		}
	//	} else {
	//		$cmd = 'svn info ' . $settings['revision_url'] . ' | grep "Last Changed Rev: " | awk \'{print $4}\'';
	//		$last_changed_revision = intval(trim(shell_exec($cmd)));
	//		echo "3 - Getting Revision History for " . $last_changed_revision . " to " . $revision . "\n";
	//		$cmd = 'svn log ' . $settings['revision_url'] . ' -r ' . $last_changed_revision . ':' . $revision . ' --xml';
	//		$log_contents = shell_exec($cmd);
	//		if (trim($log_contents) != '') {
	//			$xml = simplexml_load_string($log_contents);
	//			if (count($xml->logentry) > 0) {
	//				foreach ($xml->logentry as $log_entry) {
	//					$log_buffer[] = $log_entry['revision'] . ": " . $log_entry->msg;
	//				}
	//			} else {
	//				$log_buffer[] = $revision . ": Incremental Update";
	//			}
	//		} else {
	//			$log_buffer[] = $revision . ": Incremental Update";
	//		}
	//	}
	//}
	
	$base_dir = $BUILDDIR . '/SOURCES/' . $BASENAME . '-' . $VERSION;
	
	//// Extract the subversion files
	//foreach ($settings['subversion'] as $key => $svn_array) {
	//	echo "Working on " . $key . "\n";
	//	$source_folder = $base_dir . $svn_array[1];
	//	echo " - Exporting to: " . $source_folder . "\n";
	//	if (file_exists($source_folder)) {
	//		$cmd = 'rm -Rf ' . $source_folder;
	//		passthru($cmd);
	//	}
	//	if (!file_exists($source_folder)) {
	//		$cmd = 'mkdir -p ' . $source_folder;
	//		passthru($cmd);
	//	}
	//	echo " - Exporting url: " . $svn_array[0] . "\n";
	//	$cmd = 'svn export --force ' . $svn_array[0] . ' ' . $source_folder;
	//	passthru($cmd);
	//}
	
	// Extract the git files
	
	if (!isset($settings['git'])) { throw new Exception('No GIT repository is defined in settings.ini'); }
	
	foreach ($settings['git'] as $key => $git_array) {
		echo "Working on " . $key . "\n";
		$source_folder = $base_dir . $git_array[1];
		echo " - Exporting to: " . $source_folder . "/\n";
		if (file_exists($source_folder)) {
			$cmd = 'rm -Rf ' . $source_folder;
			passthru($cmd);
		}
		if (!file_exists($source_folder)) {
			$cmd = 'mkdir -p ' . $source_folder;
			passthru($cmd);
		}
		echo " - Exporting url: " . $git_array[0] . "\n";
		
		$cmd = 'git clone --depth=1 --recurse-submodules ' . $git_array[0] . ' ' . $source_folder . '/';
		echo $cmd . "\n";
		passthru($cmd);
		$cmd = 'cd ' . $source_folder . '/';
		passthru($cmd);

//		$cmd = 'git submodule update --init --recursive ' . $source_folder . '/';
//		echo $cmd . "\n";
//		passthru($cmd);
		
		$release_notes = '';
		// Grab our log contents so we can post the release notes to the version server
		$cmd = 'git --no-pager --git-dir ' . $source_folder . '/.git log --pretty=oneline';
		echo $cmd . "\n";
		$release_notes = shell_exec($cmd);
		
		// Remove the git files
		$find_cmd = 'find ' . $source_folder . ' -type d -name ".git*"';
		$git_folders = shell_exec($find_cmd);
		foreach (explode("\n", $git_folders) as $git_folder) {
			if (trim($git_folder) != '') {
				$cmd = "rm -Rf " . $git_folder;
				echo $cmd . "\n";
				shell_exec($cmd);	
			}
		}
		
		// Remove the git files
		$find_cmd = 'find ' . $source_folder . ' -type f -name ".git*"';
		$git_files = shell_exec($find_cmd);
		foreach (explode("\n", $git_files) as $git_file) {
			if (trim($git_file) != '') {
				$cmd = "rm -f " . $git_file;
				echo $cmd . "\n";
				shell_exec($cmd);
			}	
		}
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
	
	echo $release_notes . "\n";
	Rad_StringTools::consoleWrite('Saving Component Version', $api_url, Rad_StringTools::CONSOLE_COLOR_RED, true);
	$response_obj = Rad_Api::sendAjax('/Component/ComponentVersion', array('rpm_name' => $BASENAME, 'version' => ($VERSION), 'release_notes' => $release_notes, 'rpm_build_date' => date('Y-m-d')), 'POST', array(), $api_url);

	if (isset($response_obj['record'])) {
		$full_version = $response_obj['record']['version'];
		$revision = $response_obj['record']['revision'];
		Rad_StringTools::consoleWrite('Saving Component Version', $full_version, Rad_StringTools::CONSOLE_COLOR_GREEN, true);
	} else {
		throw new Exception('Cannot find revision for component: ' . $BASENAME);	
	}
	
	// Extract the support folders
	foreach ($settings['support_folders'] as $key => $folder_name) {
		echo "Working on " . $key .  " => " . $folder_name[0] . "\n";
		$source_folder = $base_dir . '/' . $folder_name[0];
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
	
	if (isset($settings['version_file']) && trim($settings['version_file']) != '') {
		file_put_contents($base_dir . $settings['root_folder'] . '/' . $settings['version_file'], $VERSION . '-' . $revision);
	}
	
	if (file_exists(dirname(__FILE__) . '/conf/' . $conf_dir . '/specs/' . $spec_file)) {
		$spec = file_get_contents(dirname(__FILE__) . '/conf/' . $conf_dir . '/specs/' . $spec_file);
		$spec = str_replace('[[VERSION]]', $VERSION, $spec);
		$spec = str_replace('[[REVISION]]', $revision, $spec);
		$spec = str_replace('[[BUILDDIR]]', $BUILDDIR, $spec);
		file_put_contents($BUILDDIR . '/SPECS/' . $BASENAME . '-' . $spec_file, $spec);
	}
	
	
	
	echo ' - Tar/Gzipping' . "\n";
	// Tar up the checked out files
	$cmd = 'tar -cPf ' . $BASENAME . '-' . $VERSION . '.tar ' . ' -C ' . dirname($base_dir) . ' ' . basename($base_dir);
	echo $cmd . "\n";
	passthru($cmd);
	// Gzip the tar
	$cmd = 'gzip -f ' . $BASENAME . '-' . $VERSION . '.tar';
	echo $cmd . "\n";
	passthru($cmd);
	
	// We move the tar.gz to /usr/src/redhat/SOURCES because that's the default folder for building RPMs
	$cmd = 'cp ' . $BASENAME . '-' . $VERSION . '.tar.gz' . ' ' . '/usr/src/redhat/SOURCES';
	passthru($cmd);
	
	// Build the rpm
	$cmd = 'rpmbuild -ba --quiet ' . $BUILDDIR . '/SPECS/' . $BASENAME . '-' . $spec_file;
	echo $cmd . "\n";
	passthru($cmd);
	
	$cmd = 'cp -Rf /usr/src/redhat/RPMS/noarch/' . $BASENAME . '-' . $VERSION . '-' . $revision . '.noarch.rpm ' . $BUILDDIR . '/RPMS/';
	passthru($cmd);
	
	// Now update the component in doublesplash
//	$release_notes = implode("\n", $log_buffer);
//	echo $release_notes . "\n";
//	$release_notes = '';
//	Rad_StringTools::consoleWrite('Saving Component Version', 'Saving', Rad_StringTools::CONSOLE_COLOR_RED);
//	$response_obj = Rad_Api::sendAjax('/Component/ComponentVersion', array('rpm_name' => $BASENAME, 'version' => ($VERSION . '-' . $revision), 'release_notes' => $release_notes), 'POST', array(), $api_url);
//	Rad_StringTools::consoleWrite('Saving Component Version', 'Saved', Rad_StringTools::CONSOLE_COLOR_GREEN, true);
	
	// Save this current revision into the build folder, so we can get the log next time
	file_put_contents(dirname(__FILE__) . '/conf/' . $conf_dir . '/.svn_version', $revision);
	
	// Now remove the extra files created by building the RPM
	/*
	$cmd = 'rm -Rf /usr/src/redhat/RPMS/noarch/*.rpm';
	passthru($cmd);
	$cmd = 'rm -Rf /usr/src/redhat/RPMS/x86_64/*.rpm';
	passthru($cmd);
	$cmd = 'rm -Rf /usr/src/redhat/BUILD/*';
	passthru($cmd);
	$cmd = 'rm -Rf /usr/src/redhat/SOURCES/*';
	passthru($cmd);
	$cmd = 'rm -Rf /usr/src/redhat/SRPMS/*';
	passthru($cmd);
	$cmd = 'rm -Rf /usr/src/redhat/SPECS/*';
	passthru($cmd);
	*/
	
	if (strtoupper(trim($upload_rpm)) == 'Y') {
		echo "Removing older revisions (5)..." . "\n";
		$cmd = 'ssh root@yum.radinteractive.net rm -f /var/www/sites/yum/CentOS/5/local/*/RPMS/' . $BASENAME . '*';
		passthru($cmd);
		
		echo "Uploading new revisions (5)..." . "\n";
		$cmd = 'scp ' . $BUILDDIR . '/RPMS/' . $BASENAME . '-' . $VERSION . '-' . $revision . '.noarch.rpm root@yum.radinteractive.net:/var/www/sites/yum/CentOS/5/local/noarch/RPMS/ 2>&1';
		passthru($cmd);
		
		echo "Rebuilding Repositories (5)..." . "\n";	
		$cmd = 'ssh root@yum.radinteractive.net createrepo --update /var/www/sites/yum/CentOS/5/local/noarch/';
		passthru($cmd);
		
		echo "Removing older revisions (6)..." . "\n";
		$cmd = 'ssh root@yum.radinteractive.net rm -f /var/www/sites/yum/CentOS/6/local/*/RPMS/' . $BASENAME . '*';
		passthru($cmd);
		
		echo "Uploading new revisions (6)..." . "\n";
		$cmd = 'scp ' . $BUILDDIR . '/RPMS/' . $BASENAME . '-' . $VERSION . '-' . $revision . '.noarch.rpm root@yum.radinteractive.net:/var/www/sites/yum/CentOS/6/local/noarch/RPMS/ 2>&1';
		passthru($cmd);
		
		echo "Rebuilding Repositories (6)..." . "\n";	
		$cmd = 'ssh root@yum.radinteractive.net createrepo --update /var/www/sites/yum/CentOS/6/local/noarch/';
		passthru($cmd);
		
		echo 'Done building ' . $BASENAME . ' rpm at revision ' . $VERSION . '-' . $revision . "\n";
	} else {
		echo 'RPM built in ' . $BUILDDIR . '/RPMS/' . "\n";
		passthru('ls -lh ' . $BUILDDIR . '/RPMS/');
	}
} catch (Exception $e) {
	echo Rad_StringTools::consoleColor($e->getMessage(), Rad_StringTools::CONSOLE_COLOR_RED) . "\n";
	exit;	
}
?>