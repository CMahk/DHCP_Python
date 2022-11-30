from socket import *
from ipaddress import IPv4Address
from random import *
import dhcppython
from dhcppython.options import MessageType, OptionList


ip_pool = list(range(2, 254))
ip_current = [1]

def dhcp_getip():
	index = randint(2, len(ip_pool))
	ip = ip_pool[index]
	ip_current.append(ip)
	del ip_pool[index]
	return "192.168.0." + str(ip) # 192.168.1.x

def dhcp_offer(MAC, XID, ip_offered):

	pkt = dhcppython.packet.DHCPPacket(
		op = "BOOTREPLY",
		htype = "ETHERNET",
		hlen = 6,
		hops = 0,
		xid = XID,
		secs = 0,
		flags = 0,
		ciaddr = IPv4Address("0.0.0.0"),
		yiaddr = IPv4Address(ip_offered),
		siaddr = IPv4Address("192.168.0.1"),
		giaddr = IPv4Address("0.0.0.0"),
		chaddr = MAC,
		sname = b"",
		file = b"",
		options = OptionList(
			[
				MessageType(code = 53, length = 1, data = b"\x02"),		# OFFER
				dhcppython.options.options.short_value_to_object(51, 7200),
				dhcppython.options.options.short_value_to_object(58, 3600),
			])
		)

	return pkt

def dhcp_ack(MAC, XID, ip_requested):

	pkt = dhcppython.packet.DHCPPacket(
		op = "BOOTREPLY",
		htype = "ETHERNET",
		hlen = 6,
		hops = 0,
		xid = XID,
		secs = 0,
		flags = 0,
		ciaddr = IPv4Address("0.0.0.0"),
		yiaddr = IPv4Address(ip_requested),
		siaddr = IPv4Address("192.168.0.1"),
		giaddr = IPv4Address("0.0.0.0"),
		chaddr = MAC,
		sname = b"",
		file = b"",
		options = OptionList(
			[
				MessageType(code = 53, length = 1, data = b"\x05"),		# ACK
				dhcppython.options.options.short_value_to_object(51, 7200),
				dhcppython.options.options.short_value_to_object(58, 3600),
			])
		)

	return pkt

DHCP_SERVER = ('', 67)
DHCP_CLIENT = ('255.255.255.255', 68)

# Create a UDP socket
s = socket(AF_INET, SOCK_DGRAM)

# Allow socket to broadcast messages
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

# Bind socket to the well-known port reserved for DHCP servers
s.bind(DHCP_SERVER)

print("Server successfully set up")

while True:
	# Recieve client DISCOVER
	msg, addr = s.recvfrom(1024)

	# Get current client transaction ID
	client_mac = format(msg[28], 'x')
	XID_current = int.from_bytes(msg[4:8], "big")

	# Print the client's MAC Address from the DHCP header
	print("DISCOVERY - MAC Address is " + format(msg[28], 'x'), end = '')
	for i in range(29, 34):
		print(":" + format(msg[i], 'x'), end = '')
		client_mac += ":" + format(msg[i], 'x')
	print()

	# Send OFFER via UDP message (Broadcast)
	ip_offered = dhcp_getip()
	print("Offering IP: " + ip_offered)
	offer = dhcp_offer(client_mac, XID_current, ip_offered)

	print("Sending DHCP OFFER to client")
	s.sendto(offer.asbytes, DHCP_CLIENT)
	print("-----------------------------------------")

	# Wait for client to REQUEST
	msg, addr = s.recvfrom(1024)

	pkt_request = dhcppython.packet.DHCPPacket.from_bytes(msg)
	ip_requested = pkt_request.options.by_code(50) # Look for the IP requested in the options field
	ip_requested = int.from_bytes(ip_requested.data, "big")

	# Get current client transaction ID
	client_mac = format(msg[28], 'x')
	XID_current = int.from_bytes(msg[4:8], "big")

	# Print the client's MAC Address from the DHCP header
	print("REQUEST - MAC Address is " + format(msg[28], 'x'), end = '')
	for i in range(29, 34):
		print(":" + format(msg[i], 'x'), end = '')
		client_mac += ":" + format(msg[i], 'x')
	print()

	print("IP requested: " + str(ip_requested))

	# Send ACK via UDP message (Broadcast)
	acknowledge = dhcp_ack(client_mac, XID_current, ip_requested)

	print("Sending DHCP ACK to client")
	s.sendto(acknowledge.asbytes, DHCP_CLIENT)
	print("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
