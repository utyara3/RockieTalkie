import socket
import threading
from typing import Dict


class RockieTalkieServer:
    def __init__(
        self,
        ip: str = socket.gethostbyname(socket.gethostname()),
        port: int = 5050,
        max_connections: int = 10,
    ):
        self.ip = ip
        self.port = port
        self.max_connections = max_connections

        self.buffer_size = 1024
        self.format = "utf-8"
        self.disconnect_message = "!DISCONNECT"

        self.addr = (self.ip, self.port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.active_connections: Dict[tuple, tuple] = {}

        try:
            self.server.bind(self.addr)
        except OSError as e:
            print(f"[ERROR] Could not bind to {self.addr}: {e}")
            raise

    def broadcast(self, sender_addr: tuple, message: str) -> None:
        for addr, conn in self.active_connections.items():
            if addr != sender_addr:
                try:
                    conn[0].send(message.encode(self.format))
                except (ConnectionError, socket.error):
                    print(f"[ERROR] Failed to send to {addr}")
                    del self.active_connections[addr]

    def _handle_client(self, conn: socket.socket, addr: tuple) -> None:
        print(f"[NEW CONNECTION] {addr} connected")
        nickname = conn.recv(1024).decode(self.format)
        self.active_connections[addr] = (conn, nickname)

        try:
            while True:
                message = conn.recv(self.buffer_size).decode(self.format)
                if not message or message == self.disconnect_message:
                    break
                print(f"[{addr}] {message}")
                self.broadcast(addr, f"{nickname}: {message}")
        except (ConnectionResetError, socket.error):
            print(f"[ERROR] Client {addr} {nickname} disconnected abruptly")
        finally:
            conn.close()
            del self.active_connections[addr]  # Удаляем из активных
            print(f"[DISCONNECTED] {addr} disconnected")

    def start(self) -> None:
        self.server.listen(self.max_connections)
        print(f"[LISTENING] Server is listening on {self.ip}:{self.port}")

        try:
            while True:
                conn, addr = self.server.accept()
                thread = threading.Thread(target=self._handle_client, args=(conn, addr))
                thread.start()
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Server stopped by user")
        finally:
            self.server.close()


if __name__ == "__main__":
    server = RockieTalkieServer()
    print("[START] Server is starting...")
    server.start()
