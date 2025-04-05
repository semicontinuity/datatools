import socket


SERVER_PORT = 7777


def get_local_ip():
    """Get the IP address that would be used to connect to the internet"""
    try:
        # Create a dummy socket to get the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google's public DNS
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return '127.0.0.1'  # Fallback

