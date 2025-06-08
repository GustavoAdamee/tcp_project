# Client
import socket
import hashlib
import threading

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

# Global flag to control client shutdown
running = True

# Function to receive a line from the server
def recv_line(socket):
    data = b""
    while not data.endswith(b"\n"):
        chunk = socket.recv(1)
        if not chunk:
            break
        data+=chunk
    return data.decode('utf-8').strip()

# Function to receive a specific number of bytes from the server
def recv_exat(socket, num_bytes):
    data = b""
    while len(data) < num_bytes:
        chunk = socket.recv(num_bytes - len(data))
        if not chunk:
            break
        data += chunk
    return data

# Thread to handle incoming messages from server
def receive_messages():
    global running
    while running:
        try:
            server_data = recv_line(client_socket)
            if not server_data:
                break
                
            print(f"\n[SERVER]: {server_data}")
            
            if server_data.startswith("ERR"):
                print(f"Error from server: {server_data[4:]}")
                
            elif server_data.startswith("OK"):
                parts = server_data.split()
                file_name = parts[1]
                file_size = int(parts[2])
                file_hash = parts[3]
                # print(f"File '{file_name}' of size {file_size} bytes with hash {file_hash} is ready to be received.")
                file_data = recv_exat(client_socket, file_size)
                if hashlib.sha256(file_data).hexdigest() != file_hash:
                    print("File hash mismatch. The file may be corrupted.")
                    continue
                with open(file_name, 'wb') as f:
                    f.write(file_data)
                print(f"File '{file_name}' received successfully.")
                
            elif server_data.startswith("MSGS"):
                print(f"Chat message: {server_data[5:]}")
            
        except socket.error:
            break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

# Thread to handle user input
def handle_input():
    global running
    while running:
        try:
            data = input("Enter command: ")
            if data.lower() == 'exit':
                running = False
                client_socket.sendall(data.encode('utf-8'))
                print("Exiting client...")
                break
            client_socket.sendall(data.encode('utf-8'))
        except EOFError:
            running = False
            break
        except Exception as e:
            print(f"Error sending message: {e}")
            break


# Initialize the client socket and connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = input("Enter server address IP:PORT: ")
ip, port = server_address.split(':')
try:
    client_socket.connect((ip, int(port)))
except socket.error as e:
    print(f"Could not connect to server at {server_address}: {e}")
    exit(1) 

print(f"Connected to server at {server_address}.")
print("Available commands: GET <filename>, MSGC <message>, exit")
print("You can start sending commands and will receive messages from other clients.")

# Start threads for receiving and sending
receive_thread = threading.Thread(target=receive_messages, daemon=True)
input_thread = threading.Thread(target=handle_input, daemon=True)

receive_thread.start()
input_thread.start()

# Wait for input thread to finish (exit command)
input_thread.join()

# Clean up
running = False
client_socket.close()
