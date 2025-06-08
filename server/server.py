# Server
import socket
import threading
import os
import hashlib


'''
    Client Commands (client -> server):
        EXIT: command to exit the server
        GET <filename>: command to get a file from the server
        MSGC <message>: command to send a message to the server
    
    Server Commands (server -> client):
        MSGS <message>: command to send a message to all clients
        ERR <message>: message to send an error status to the client
        OK <filename> <filesize> <filehash>: message to send the metadata after receiving a GET from the client
'''
class clientsHandler:
    def __init__(self):
        self.clients = []
        self.clients_lock = threading.Lock() # to ensure thread-safe access to the clients list (no race conditions)

    def add_client(self, client_socket):
        with self.clients_lock:
            if client_socket not in self.clients:
                self.clients.append(client_socket)
                print(f"New client connected: {client_socket.getpeername()}")
    
    def remove_client(self, client_socket):
        with self.clients_lock:
            if client_socket in self.clients:
                print(f"Client disconnected: {client_socket.getpeername()}")
                self.clients.remove(client_socket)
                try:
                    client_socket.close()
                except:
                    pass
    
    def broadcast(self, message):
        with self.clients_lock:
            clients_to_remove = []
            for client in self.clients:
                try:
                    client.sendall(message.encode('utf-8'))
                    print(f"Broadcasting message to {client.getpeername()}: {message.strip()}")
                except socket.error as e:
                    print(f"Error sending message to client: {e}")
                    clients_to_remove.append(client)
            
            # Remove failed clients
            for client in clients_to_remove:
                self.remove_client(client)

    def handle_client(self, client_socket, client_address):
        self.add_client(client_socket)
        print(f"Client {client_address} connected.")
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break

                command, param = parse_request(data)

                if command == "GET":
                    file_format = param.split('.')[-1] if param else None
                    if file_format is None:
                        error_message = "Invalid filename format"
                        client_socket.sendall(f"ERR {error_message}\n".encode('utf-8'))
                    else:
                        file_path = f"./files/{param}"
                        if(os.path.exists(file_path)):
                            file_name = os.path.basename(file_path)
                            file_size = os.path.getsize(file_path)
                            with open (file_path, "rb") as f:
                                file_data = f.read()
                                file_hash = hashlib.sha256(file_data).hexdigest()
                            client_socket.sendall(f"OK {file_name} {file_size} {file_hash}\n".encode('utf-8'))
                            client_socket.sendall(file_data)
                            print(f"File '{file_name}' sent to {client_address}")
                        else:
                            error_message = "File not found"
                            client_socket.sendall(f"ERR {error_message}\n".encode('utf-8'))

                elif command == "MSGC":
                    if param is None or len(param) == 0:
                        error_message = "Invalid MSGC command format"
                        client_socket.sendall(f"ERR {error_message}\n".encode('utf-8'))
                    else:
                        print(f"MSGC from {client_address}: {param}")
                        # self.broadcast(f"MSGS [Client {client_address[0]}:{client_address[1]}]: {param}\n")
                    
                elif command == "EXIT":
                    print(f"EXIT received from {client_address}")
                    self.remove_client(client_socket)
                    break
                    
            except socket.error:
                break
            except Exception as e:
                print(f"Error handling client {client_address}: {e}")
                break
        
        self.remove_client(client_socket)

# Function to parse the request from the client
def parse_request(data):
    if not data:
        return None,None
    request = data.strip()
    parts = request.split(' ', 1) #split the string in two parts
    command = parts[0].upper()
    param = parts[1] if len(parts) > 1 else None
    return command, param

# Function to handle server console input
def handle_server_input(clients_handler):
    print("Server console ready. Type messages to broadcast to all clients.")
    print("Commands: 'quit' to shutdown server, or any text to broadcast")
    
    while True:
        try:
            message = input("Server> ")
            clients_handler.broadcast(f"MSGS [SERVER]: {message}\n")
        except KeyboardInterrupt:
            break
        except EOFError:
            break

def main():
    print("Server is starting...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.2', 8080))
    server_socket.listen()

    clients = clientsHandler()
    print("Server is listening on port 8080...")

    # Start server input thread
    input_thread = threading.Thread(target=handle_server_input, args=(clients,), daemon=True)
    input_thread.start()

    try:
        while(True):
            client_socket, addr = server_socket.accept()
            threading.Thread(target=clients.handle_client, args=(client_socket, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()