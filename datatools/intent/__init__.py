import socket


SERVER_PORT = 7777

import netifaces


def get_local_ip():
    """Get LAN IP using netifaces with subnet filtering"""
    lan_prefixes = ('192.168.', '10.', '172.16.', '172.17.', '172.18.', '172.19.',
                    '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.',
                    '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.')

    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface).get(netifaces.AF_INET, [])
        for addr_info in addrs:
            ip = addr_info['addr']
            if any(ip.startswith(prefix) for prefix in lan_prefixes):
                return ip
    return '127.0.0.1'
