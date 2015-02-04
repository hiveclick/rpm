<?php
/**
 * Sends a request via curl and returns the response
 * @author Mark Hobson
 */
require_once(dirname(__FILE__) . '/Api/Abstract.php');

class Rad_Api extends Rad_Api_Abstract {
	
	/**
	 * Sends a call out using the global gapi tokens
	 * @param string $func
	 * @param string $params
	 * @param string $method
	 * @param array $headers
	 * @param string $url
	 */
	static function send($func, $params, $method = 'GET', $headers = array(), $host = '') {
		$ajax = new Rad_Api();
		if ($host == '') {
			$host = 'http://api.radinteractive.net';	
		}
		return $ajax->curl($host, $func, $params, $method, $headers);
	}
	
	/**
	 * Sends a call out using the global gapi tokens
	 * @param string $func
	 * @param string $params
	 * @param string $method
	 * @param array $headers
	 * @param string $url
	 */
	static function sendAjax($func, $params, $method = 'GET', $headers = array(), $host = '') {
		return Zend_Json::decode(self::send($func, $params, $method, $headers, $host));
	}
}
?>