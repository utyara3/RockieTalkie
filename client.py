import socket
import threading
import readline


class RockieTalkieClient:
    def __init__(
        self,
        server_ip: str = socket.gethostbyname(socket.gethostname()),
        server_port: int = 5050,
        buffer_size: int = 1024,
        disconnect_message: str = "!DISCONNECT",
        username: str = None
    ):
        self.server_ip = server_ip
        self.server_port = server_port
        self.buffer_size = buffer_size
        self.format = "utf-8"
        self.disconnect_message = disconnect_message
        
        self.addr = (self.server_ip, self.server_port)
        if not username:
            username = input("Enter your username: ")
        self.username = username
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.connected = False

    def connect(self) -> bool:
        try:
            self.client.connect(self.addr)
            self.send_message(self.username)
            self.connected = True
            print(f"[CONNECTED] Connected to server at {self.server_ip}:{self.server_port}")
            return True
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False

    def send_message(self, message: str) -> None:
        try:
            self.client.send(message.encode(self.format))
            if message == self.disconnect_message:
                self.connected = False
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")
            self.connected = False

    def receive_messages(self) -> None:
        while self.connected:
            try:
                message = self.client.recv(self.buffer_size).decode(self.format)
                if not message or message == self.disconnect_message:
                    self.connected = False
                    print("[DISCONNECTED] Server closed the connection")
                    break

                current_input = readline.get_line_buffer()
                print(f"\r{message}\n{self.username} > {current_input}", end="", flush=True)
                #print(message)
            except Exception as e:
                print(f"[ERROR] Failed to receive message: {e}")
                self.connected = False
                break

    def start(self) -> None:
        if not self.connect():
            return

        receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        receive_thread.start()

        try:
            while self.connected:
                message = input(f"{self.username} > ")
                self.send_message(message)
                if message == self.disconnect_message:
                    break
        except KeyboardInterrupt:
            self.send_message(self.disconnect_message)
        finally:
            self.client.close()


if __name__ == "__main__":
    client = RockieTalkieClient()
    print("[START] Client is starting...")
    print("Type your messages (enter !DISCONNECT to quit):")
    client.start()
