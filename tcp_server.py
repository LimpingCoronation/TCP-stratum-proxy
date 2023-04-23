import argparse
import socket
import select


class TCPServer:
    BUFFER_SIZE = 1024

    def __init__(self, proxy_addr: tuple, server_addr: tuple):
        self.proxy_addr = self._ip_to_tuple(proxy_addr)
        self.server_addr = self._ip_to_tuple(server_addr)
        self._rsockets = []
    

    def run(self):
        # Proxy server socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(self.proxy_addr)
        server.listen(1)
        
        client, addr = server.accept()

        print(f"{addr[0]}:{addr[1]} was connected!")

        # Remote server socket
        pool_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostbyname(self.server_addr[0])
        pool_client.connect((host, self.server_addr[1]))

        self._rsockets += [client, pool_client]

        while True:
            s_read, _, _ = select.select(self._rsockets, [], [])

            for s in s_read:
                data = s.recv(self.BUFFER_SIZE)

                if s == pool_client:
                    if data: print(data)
                    client.send(data)
                
                if s == client:
                    if data: print(data)
                    pool_client.send(data)
    

    def _ip_to_tuple(self, ip: str):
        ip_tuple = tuple(ip.split(':'))

        if len(ip_tuple) < 2:
            raise ValueError("Address must be in the format 127.0.0.1:8000")
        else:
            return (ip_tuple[0], int(ip_tuple[1]))
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser("TCP proxy server")
    parser.add_argument('-ps', '--proxy_server_address', required=True, help="Your proxy server address. Example: 127.0.0.1:8000")
    parser.add_argument('-s', '--server_address', required=True, help="Server address. Example:  127.0.0.1:8000")
    
    args = parser.parse_args()

    tcp_server = TCPServer(args.proxy_server_address, args.server_address)
    tcp_server.run()

