from socket import *
from ipaddress import IPv4Address
from random import *
import dhcppython
from dhcppython.options import MessageType, OptionList, SubnetMask

ip_range = list(range(2, 254))
ip_pool = {"127.0.0.1": "192.168.0.1"}

def dhcp_getip(MAC):
 index = randint(2, len(ip_range))
 ip = ip_range[index]
 ip_pool[MAC] = "192.168.0." + str(ip)
 del ip_range[index]
 return ip_pool[MAC] # 192.168.1.x

def dhcp_offer(MAC, XID):

 pkt = dhcppython.packet.DHCPPacket(
  op = "BOOTREPLY",
  htype = "ETHERNET",
  hlen = 6,
  hops = 0,
  xid = XID,
  secs = 0,
  flags = 0,
  ciaddr = IPv4Address("0.0.0.0"),
  yiaddr = IPv4Address(dhcp_getip(MAC)),
  siaddr = IPv4Address("192.168.0.1"),
  giaddr = IPv4Address("0.0.0.0"),
  chaddr = MAC,
  sname = b"",
  file = b"",
  options = OptionList(
   [
    # Subnet mask, OFFER, lease time, and renewal time
    SubnetMask(code = 1, length = 4, data = b"\xFF\xFF\xFF\x00"),
    MessageType(code = 53, length = 1, data = b"\x02"),
    dhcppython.options.options.short_value_to_object(51, 7200),
    dhcppython.options.options.short_value_to_object(58, 3600)
   ])
  )

 return pkt

def dhcp_ack(MAC, XID):

 pkt = dhcppython.packet.DHCPPacket(
  op = "BOOTREPLY",
  htype = "ETHERNET",
  hlen = 6,
  hops = 0,
  xid = XID,
  secs = 0,
  flags = 0,
  ciaddr = IPv4Address("0.0.0.0"),
  yiaddr = IPv4Address(ip_pool[MAC]),
  siaddr = IPv4Address("192.168.0.1"),
  giaddr = IPv4Address("0.0.0.0"),
  chaddr = MAC,
  sname = b"",
  file = b"",
  options = OptionList(
   [
    # Subnet mask, ACK, lease time, and renewal time
    SubnetMask(code = 1, length = 4, data = b"\xFF\xFF\xFF\x00"),
    MessageType(code = 53, length = 1, data = b"\x05"),
    dhcppython.options.options.short_value_to_object(51, 7200),
    dhcppython.options.options.short_value_to_object(58, 3600)
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
 offer = dhcp_offer(client_mac, XID_current)
 print("Offering " + client_mac + " IP: " + ip_pool[client_mac])

 s.sendto(offer.asbytes, DHCP_CLIENT)
 print("-----------------------------------------")

 # Wait for client to REQUEST
 msg, addr = s.recvfrom(1024)

 pkt_request = dhcppython.packet.DHCPPacket.from_bytes(msg)
 ip_requested = pkt_request.options.by_code(50) # Look for the IP requested in the options field
 req_list = list(ip_requested.data)
 ip_requested = str(req_list[0]) + "." + str(req_list[1]) + "." + str(req_list[2]) + "." + str(req_list[3])

 # Get current client transaction ID
 client_mac = format(msg[28], 'x')
 XID_current = int.from_bytes(msg[4:8], "big")

 # Print the client's MAC Address from the DHCP header
 print("REQUEST - MAC Address is " + format(msg[28], 'x'), end = '')
 for i in range(29, 34):
  print(":" + format(msg[i], 'x'), end = '')
  client_mac += ":" + format(msg[i], 'x')
 print()

 print(client_mac + " is requesting IP: " + ip_requested)
 if (ip_requested == ip_pool[client_mac]):
  print("Assigning " + ip_requested + " to " + client_mac)

  # Send ACK via UDP message (Broadcast)
  acknowledge = dhcp_ack(client_mac, XID_current)

  print("Sending DHCP ACK to client")
  s.sendto(acknowledge.asbytes, DHCP_CLIENT)

  print("Current pool of assigned IPs:")
  for x in ip_pool:
   print(x + " : " + ip_pool[x])

 else:
  print("ERROR: " + ip_requested + " was not previously offered to " + client_mac)

 print("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
