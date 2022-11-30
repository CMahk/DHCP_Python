def dhcp_request(XID, given_ip):
	request = b"\x01" 									# OP code
	request += b"\x01"									# Hardware type
	request += b"\x06" 									# Hardware address length
	request += b"\x00" 									# Hops
	request += XID										# Transaction ID
	request += b"\x00\x00"								# Seconds
	request += b"\x00\x00"								# Flags
	request += b"\x00\x00\x00\x00"						# Client IP address (currently unassigned)
	request += b"\x00\x00\x00\x00"						# Your (client) IP address
	request += b"\x00\x00\x00\x00"						# Next server IP address
	request += b"\x00\x00\x00\x00"						# Relay IP address

	hexed = []
	for val in client_mac:								# Client MAC address (6 bytes)
		hexed.append(hex(val))

	request += bytes([int(x, 0) for x in hexed])

	for i in range(0, 10):								# 10 bytes of zeroes (for CHADDR1 - 4 after client MAC address)
		request += b"\x00"
	
	for i in range(0, 64):								# Server host name not given
		request += b"\x00"

	for i in range(0, 128):								# Boot file name not given
		request += b"\x00"

	request += b"\x63\x82\x53\x63"						# Magic cookie

	request += b"\x35\x01\x03"							# DHCP REQUEST to client
	request += b"\x0C\x02\x63\x6C"						# Host name "cl"
	request += b"\x36\x04\xC0\xA8\x00\x01"				# DHCP server identifier (192.168.0.1)
	request += b"\x32\x04" + given_ip					# Requested IP address

	request += b"\x3D\x07\x01"							# Client MAC address
	request += bytes([int(x, 0) for x in hexed])

	request += b"\xFF"									# End

	return request