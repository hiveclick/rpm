<?php
/**
 * Sends a request via curl and returns the response
 * @author Mark Hobson
 */
require_once(dirname(__FILE__) . '/../Core/Common.php');

abstract class Rad_Api_Abstract extends Rad_Core_Common {
	
	const DEBUG = false;
	
	/**
	 * Sends a request via curl
	 * @param string $host
	 * @param string $func
	 * @param string $params
	 * @param string $method
	 * @param string $headers
	 */
	function curl($host, $func, $params, $method = 'GET', $headers = array()) {
		$host .= $func;

		if ($method == 'GET') {
			$host .= '?' . http_build_query($params);
		} else if ($method == 'PUT' || $method == 'DELETE') {
			foreach ($params as $key => $value) {
				$host .= '/' . $key . '/' . $value;
			}
		}
		if (self::DEBUG) {
			echo __METHOD__ . ' :: ' . $host . "\n";
			echo __METHOD__ . ' :: ' . var_export($params, true) . "\n";
			echo __METHOD__ . ' :: ' . var_export($headers, true) . "\n";
		}
		
		$ch = curl_init($host);
		if ($method == 'POST') {
			curl_setopt($ch, CURLOPT_POST, true);
			curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($params));
		} else if ($method == 'PUT') {
			curl_setopt($ch, CURLOPT_PUT, true);
		}
		curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
		curl_setopt($ch, CURLOPT_HEADER, false);
		if ($method == 'DELETE') {
			curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'DELETE');
		}
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
		curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
		curl_setopt($ch, CURLOPT_TIMEOUT, 30);
		curl_setopt($ch, CURLOPT_COOKIEJAR, ".cookie.txt");
	    curl_setopt($ch, CURLOPT_COOKIEFILE, ".cookie.txt");
	    curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0)");
	    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
	    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
		$response = curl_exec($ch);
		if (self::DEBUG) {
			echo __METHOD__ . ' :: ' . $response . "\n";
		}
		curl_close($ch);
		return $response;
	}
	
}
?>