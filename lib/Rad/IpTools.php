<?php
/**
 * IpTools takes an ip range string and converts it into an object allowing you to get information about the range
 * @author Mark Hobson
 */
require_once(dirname(__FILE__) . '/Core/Common.php');

class Rad_IpTools extends Rad_Core_Common {

	protected $ip_range;
	protected $domain;
	protected $range_prefix;
	protected $minimum_octet;
	protected $maximum_octet;
	protected $gateway;
	protected $broadcast;
	protected $cidr;
	protected $netmask;
	protected $ip_address_array;
	
	/**
	 * Constructs a new object
	 * @arg0 string Ip Range
	 */
	function __construct($arg0 = null) {
		if (!is_null($arg0)) {
			$this->setIpRange($arg0);	
		}
	}
	
	/**
	 * Returns the domain
	 * @return string
	 */
	function getDomain() {
		if (is_null($this->domain)) {
			$this->domain = "";
		}
		return $this->domain;
	}
	
	/**
	 * Sets the domain
	 * @param $arg0 string
	 */
	function setDomain($arg0) {
		$this->domain = $arg0;
		return $this;
	}
	
	/**
	 * Returns the ip_range
	 * @return string
	 */
	function getIpRange() {
		if (is_null($this->ip_range)) {
			$this->ip_range = '0.0.0.0';
		}
		return $this->ip_range;
	}
	
	/**
	 * Sets the ip_range
	 * @param $arg0 string
	 */
	function setIpRange($arg0) {
		$this->ip_range = $arg0;
		if (strpos($this->ip_range, "-") !== false) {
			$matches = array();
			preg_match('/([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})-([0-9]{1,3})/', $this->ip_range, $matches);
			if (isset($matches[1]) && isset($matches[2]) && isset($matches[3]) && isset($matches[4]) && isset($matches[5])) {
				$ip_difference = $matches[5] - $matches[4];
				if ($ip_difference <= 8) {
					$ip_difference = 8;
				} else if ($ip_difference <= 16) {
					$ip_difference = 16;
				} else if ($ip_difference <= 32) {
					$ip_difference = 32;
				} else if ($ip_difference <= 64) {
					$ip_difference = 64;
				} else if ($ip_difference <= 128) {
					$ip_difference = 128;
				} else if ($ip_difference > 128) {
					$ip_difference = 256;
				}
				$cidr = substr_count((string)decbin(ip2long('255.255.255.' . (256 - $ip_difference))), '1');
				$this->setCidr($matches[1] . '.' . $matches[2] . '.' . $matches[3] . '.' . $matches[4] . '/' . $cidr);
				$this->calculateRangeSettings();
				if ($matches[5] > substr($this->getBroadcast(), strrpos($this->getBroadcast(), '.') + 1)) {
					$this->setCidr($matches[1] . '.' . $matches[2] . '.' . $matches[3] . '.' . $matches[4] . '/' . ($cidr - 1));
					$this->calculateRangeSettings();
				}
				$this->setMinimumOctet($matches[4]);
				$this->setMaximumOctet($matches[5]);
				$this->calculateIpArray();
			}
		} else if (strpos($this->ip_range, "/") !== false) {
			$matches = array();
			preg_match('/([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\/([0-9]{1,2})/', $this->ip_range, $matches);
			if (isset($matches[1]) && isset($matches[2]) && isset($matches[3]) && isset($matches[4]) && isset($matches[5])) {
				$this->setCidr($this->ip_range);
				$this->calculateRangeSettings();
				$this->calculateIpArray();
			}
		} else {
			$matches = array();
			preg_match('/([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})/', $this->ip_range, $matches);
			if (isset($matches[1]) && isset($matches[2]) && isset($matches[3]) && isset($matches[4])) {
				$this->setCidr($this->ip_range . '/32');
				$this->calculateRangeSettings();
				$this->calculateIpArray();
			}
		}
		return $this;
	}
	
	/**
	 * Calculates the gateway, netmask, cidr and broadcast from an ip range
	 * @return DaoOffer_Form_IpRange
	 */
	function calculateRangeSettings() {
		// Calculate the netmask from the ip difference 
		$netmask = long2ip(bindec(str_pad(str_repeat('1', substr($this->getCidr(), strrpos($this->getCidr(), '/') + 1)), 32, '0', STR_PAD_RIGHT)));
		$this->setNetmask($netmask);
		// Calculate the binary representation of the netmask, first ip and last ip
		$netmask_bin = decbin(ip2long($netmask));
		$first = substr($this->getCidr(), 0, strpos($this->getCidr(), '/'));
		$first_bin = (str_pad(decbin(ip2long($first)), 32, "0", STR_PAD_LEFT) & $netmask_bin);
		$last_bin = '';
		for ($i = 0; $i < 32; $i++) {
			$last_bin .= ($netmask_bin[$i] == "1") ? $first_bin[$i] : "1"; 
		}
		// Count the # of 1's in the netmask for the cidr
		$cidr = substr_count((string)$netmask_bin, '1');
		$this->setCidr(long2ip(bindec($first_bin)) . '/' . $cidr);
		$this->setBroadcast(long2ip(bindec($last_bin)));
		if (ip2long($this->getBroadcast()) > (bindec($first_bin) + 1)) {
			$this->setGateway(long2ip(bindec($first_bin) + 1));
		} else {
			$this->setGateway(long2ip(bindec($first_bin)));
		}
		if (ip2long($this->getGateway()) <= (ip2long($this->getBroadcast()) - 1)) {
			$this->setMaximumOctet(substr(long2ip(ip2long($this->getBroadcast()) - 1), strrpos(long2ip(ip2long($this->getBroadcast()) - 1), '.') + 1));
		} else {
			$this->setMaximumOctet(substr(long2ip(ip2long($this->getBroadcast())), strrpos(long2ip(ip2long($this->getBroadcast())), '.') + 1));
		}
		if (ip2long($this->getBroadcast()) > (ip2long($this->getGateway()) + 1)) {
			$this->setMinimumOctet(substr(long2ip(ip2long($this->getGateway()) + 1), strrpos(long2ip(ip2long($this->getGateway()) + 1), '.') + 1));
		} else {
			$this->setMinimumOctet(substr(long2ip(ip2long($this->getGateway())), strrpos(long2ip(ip2long($this->getGateway())), '.') + 1));
		}
		$prefix_array = explode(".", $this->getCidr());
		array_pop($prefix_array);
		$this->setRangePrefix(implode(".", $prefix_array));
		return $this;
	}
	
	/**
	 * Calculates the available ips on a range
	 * @return DaoOffer_Form_IpRange
	 */
	function calculateIpArray() {
		// Calculate the netmask from the ip difference 
		$this->setIpAddressArray(null);
		for ($i=$this->getMinimumOctet();$i<=$this->getMaximumOctet();$i++) {
			$this->addIpAddressArray($this->getRangePrefix() . '.' . $i);
		}
		return $this;
	}
	
	/**
	 * Returns the ip_address_array
	 * @return array
	 */
	function getIpAddressArray() {
		if (is_null($this->ip_address_array)) {
			$this->ip_address_array = array();
		}
		return $this->ip_address_array;
	}
	/**
	 * Sets the ip_address_array
	 * @param array
	 */
	function setIpAddressArray($arg0) {
		$this->ip_address_array = $arg0;
		return $this;
	}
	/**
	 * Sets the ip_address_array
	 * @param array
	 */
	function addIpAddressArray($arg0) {
		$tmp_array = $this->getIpAddressArray();
		$tmp_array[] = $arg0;
		$this->setIpAddressArray($tmp_array);
		return $this;
	}
	
	/**
	 * Returns the range_prefix
	 * @return string
	 */
	function getRangePrefix() {
		if (is_null($this->range_prefix)) {
			$this->range_prefix = "";
		}
		return $this->range_prefix;
	}
	
	/**
	 * Sets the range_prefix
	 * @param $arg0 string
	 */
	function setRangePrefix($arg0) {
		$this->range_prefix = $arg0;
		return $this;
	}
	
	/**
	 * Returns the minimum_octet
	 * @return integer
	 */
	function getMinimumOctet() {
		if (is_null($this->minimum_octet)) {
			$this->minimum_octet = 2;
		}
		return $this->minimum_octet;
	}
	
	/**
	 * Sets the minimum_octet
	 * @param $arg0 integer
	 */
	function setMinimumOctet($arg0) {
		$this->minimum_octet = $arg0;
		return $this;
	}
	
	/**
	 * Returns the maximum_octet
	 * @return integer
	 */
	function getMaximumOctet() {
		if (is_null($this->maximum_octet)) {
			$this->maximum_octet = 254;
		}
		return $this->maximum_octet;
	}
	
	/**
	 * Sets the maximum_octet
	 * @param $arg0 integer
	 */
	function setMaximumOctet($arg0) {
		$this->maximum_octet = $arg0;
		return $this;
	}

	/**
	 * Returns the gateway
	 * @return string
	 */
	function getGateway() {
		if (is_null($this->gateway)) {
			$this->gateway = "";
		}
		return $this->gateway;
	}
	
	/**
	 * Sets the gateway
	 * @param $arg0 string
	 */
	function setGateway($arg0) {
		$this->gateway = $arg0;
		return $this;
	}
	
	/**
	 * Returns the broadcast
	 * @return string
	 */
	function getBroadcast() {
		if (is_null($this->broadcast)) {
			$this->broadcast = "";
		}
		return $this->broadcast;
	}
	
	/**
	 * Sets the broadcast
	 * @param $arg0 string
	 */
	function setBroadcast($arg0) {
		$this->broadcast = $arg0;
		return $this;
	}
	
	/**
	 * Returns the cidr
	 * @return string
	 */
	function getCidr() {
		if (is_null($this->cidr)) {
			$this->cidr = "/24";
		}
		return $this->cidr;
	}
	
	/**
	 * Sets the cidr
	 * @param $arg0 string
	 */
	function setCidr($arg0) {
		$this->cidr = $arg0;
		return $this;
	}
	
	/**
	 * Returns the netmask
	 * @return string
	 */
	function getNetmask() {
		if (is_null($this->netmask)) {
			$this->netmask = "255.255.255.0";
		}
		return $this->netmask;
	}
	
	/**
	 * Sets the netmask
	 * @param $arg0 string
	 */
	function setNetmask($arg0) {
		$this->netmask = $arg0;
		return $this;
	}
	
	/**
	 * Binds the range to this box
	 * @return boolean
	 */
	static function bindRange($arg0) {
		$ip_range = new Rad_IpTools();
		$ip_range->setIpRange($arg0);
		for ($i = $ip_range->getMinimumOctet(); $i <= $ip_range->getMaximumOctet(); $i++) {
			$label = sprintf("%u", ip2long($ip_range->getRangePrefix() . '.' . $i));
			// Issue the ip addr add command to bind the ip to this box
			$cmd = '/sbin/ip addr add ' . $ip_range->getRangePrefix() . '.' . $i . '/32 dev eth0 label eth0:' . $label;
			shell_exec($cmd);
			// Issue the arping command to update the routing table
			$cmd = '/sbin/arping -c 1 -s ' . $ip_range->getRangePrefix() . '.' . $i . ' 4.2.2.2';
			shell_exec($cmd);
			// Issue the gateway command if this is an alias
//			$cmd = '';
//			shell_exec($cmd);
			// Now create the ifcfg file
			$file_contents = array();
			$file_contents[] = 'DEVICE=eth0:' . $label;
			$file_contents[] = 'BOOTPROTO=static';
			$file_contents[] = 'IPADDR=' . $ip_range->getRangePrefix() . '.' . $i;
			$file_contents[] = 'NETMASK=255.255.255.255';
			$file_contents[] = 'ONBOOT=yes';
			file_put_contents('/etc/sysconfig/network-scripts/ifcfg-eth0:' . $label, implode("\n", $file_contents));
		}
	}
	
	/**
	 * Unbinds the range from this box
	 * @return boolean
	 */
	static function unbindRange($arg0) {
		$ip_range = new Rad_IpTools();
		$ip_range->setIpRange($arg0);
		for ($i = $ip_range->getMaximumOctet(); $i >= $ip_range->getMinimumOctet(); $i--) {
			$label = sprintf("%u", ip2long($ip_range->getRangePrefix() . '.' . $i));
			// Issue the ifconfig down command to take down this ip address
			$cmd = '/sbin/ifconfig eth0:' . $label . ' down';
			shell_exec($cmd);
			// Remove the ifcfg file
			if (file_exists('/etc/sysconfig/network-scripts/ifcfg-eth0:' . $label)) {
				$cmd = 'rm -f /etc/sysconfig/network-scripts/ifcfg-eth0:' . $label;
				shell_exec($cmd);
			}
		}
	}
	
	/**
	 * Checks that an IP address is bound to this box
	 * @param string $ip_address
	 * @return boolean
	 */
	public static function isIpBound($ip_address) {
		$cmd = 'ip addr show | grep "' . $ip_address . '/" | wc -l';
		$ret_val = trim(shell_exec($cmd));
		return ($ret_val == '1');
	}
	
	/**
	 * Returns a list of server ips bound to this box
	 * @return array
	 */
	public static function getServerIps() {
		$ret_val = array();
		$cmd = 'ifconfig | grep "inet addr" | awk \'{print $2}\'';
		$ip_lines = explode("\n", trim(shell_exec($cmd)));
		foreach ($ip_lines as $ip_line) {
			$ip_address = substr($ip_line, strlen('addr:'));
			if ($ip_address == '127.0.0.1') { continue; }
			$ret_val[] = $ip_address;
		}
		return $ret_val;
	}
	
	/**
	 * Returns a list of server ips bound to this box
	 * @return array
	 */
	public static function getServerIpsAsLong() {
		$ret_val = array();
		$cmd = 'ifconfig | grep "inet addr" | awk \'{print $2}\'';
		$ip_lines = explode("\n", trim(shell_exec($cmd)));
		foreach ($ip_lines as $ip_line) {
			$ip_address = substr($ip_line, strlen('addr:'));
			if ($ip_address == '127.0.0.1') { continue; }
			$ret_val[] = sprintf("%u", ip2long($ip_address));
		}
		return $ret_val;
	}
	
	/**
	 * Returns a list of server ip ranges bound to this box
	 * @return array
	 */
	public static function getServerIpRanges() {
		$ret_val = array();
		$ips = self::getServerIpsAsLong();
		$next_ip = '';
		asort($ips);
		$current_ip_array = array();
		foreach ($ips as $key => $ip) {
			if ($ip == '0') { continue; }
			if (trim($ip) == '') { continue; }
			$ip = long2ip($ip);
			if ($ip == '127.0.0.1') { continue; }
			$ip_prefix = substr($ip, 0, strrpos($ip, "."));
			$ip_octet = substr($ip, strrpos($ip, ".") + 1);
			if ($ip != $next_ip) {
				$ret_val[] = $current_ip_array;
				$current_ip_array = array();
				$current_ip_array['prefix'] = $ip_prefix;
				$current_ip_array['min'] = $ip_octet;
				$current_ip_array['max'] = $ip_octet;
			} else {
				$current_ip_array['max'] = $ip_octet;
			}
			$next_ip = $ip_prefix . '.' . ($ip_octet + 1);
		}
		$ret_val[] = $current_ip_array;
		return $ret_val;
	}
	
}
?>