import socket

def getIP():

# getting the IP address using socket.gethostbyname() method
    ip_address = socket.gethostbyname(socket.gethostname())

    return ip_address