# Client-Server File Transfer Application

This project implements a simple client-server application for file transfer and messaging using TCP sockets in Python.

## Project Structure

```
projeto_2/
├── server/
│   └── server.py     # Server implementation
├── client/
│   └── client.py     # Client implementation
└── README.md         # This documentation
```

## Features

- File transfer from server to client
- Message broadcasting from server to connected clients
- Client-to-server messaging
- Thread-safe client management
- File integrity verification using SHA-256 hash

## Protocol

The application uses a simple text-based protocol for communication:

### Client → Server Commands:
- `GET <filename>`: Request a file from the server
- `MSGC <message>`: Send a message to the server
- `EXIT`: Disconnect from the server

### Server → Client Responses:
- `OK <filename> <filesize> <filehash>`: Metadata before sending a file
- `ERR <message>`: Error notification
- `MSGS <message>`: Broadcast message from server

## How to Run

### Server Setup

1. Navigate to the server directory:
   ```
   cd /home/adame/Documents/UTFPR/redes/projeto_2/server
   ```

2. Create a `files` directory inside the server directory for storing files to be transferred:
   ```
   mkdir files
   ```

3. Place any files you want to make available for download in the `files` directory.

4. Run the server:
   ```
   python server.py
   ```

5. The server will start listening on port 8080 (default address is 127.0.0.2).

### Client Setup

1. Navigate to the client directory:
   ```
   cd /home/adame/Documents/UTFPR/redes/projeto_2/client
   ```

2. Run the client:
   ```
   python client.py
   ```

3. Enter the server's address when prompted (e.g., `127.0.0.2:8080`).

4. Start using the available commands:
   - `GET <filename>`: Download a file from the server
   - `MSGC <message>`: Send a message to the server
   - `exit`: Disconnect from the server

## Implementation Details

### Server

- Multi-threaded design to handle multiple client connections simultaneously
- Thread-safe client management with locking mechanisms
- Console interface for server administrators to broadcast messages
- File transfer with integrity verification

### Client

- Separate threads for handling user input and server messages
- File integrity checking using SHA-256 hash verification
- Simple command-line interface

## Error Handling

- The application includes error handling for:
  - Connection failures
  - File not found
  - Data corruption during transfer
  - Unexpected client disconnections

## Security Considerations

This is a simple implementation for educational purposes. For production use, consider:
- Implementing encryption for data transfer
- Adding authentication mechanisms
- Additional error handling and logging
- Rate limiting to prevent DoS attacks