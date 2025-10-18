import sys
from tcp.stop_and_wait import SocketTCP

def main():
    HOST = 'localhost'
    PORT = 5000
    
    server_socket = SocketTCP()
    server_socket.bind((HOST, PORT))
    
    print(f"[SERVER] Escuchando en {HOST}:{PORT}", file=sys.stderr)
    
    connection_socket, client_address = server_socket.accept()
    print(f"[SERVER] Cliente conectado: {client_address}", file=sys.stderr)
    
    try:
        # Recibir mensaje completo (recv() maneja los chunks)
        message = connection_socket.recv(buff_size=1024*1024)  # 1MB max
        
        print(f"[SERVER] Mensaje recibido: {len(message)} bytes", file=sys.stderr)
        
        # Escribir a stdout
        sys.stdout.buffer.write(message)
        sys.stdout.buffer.flush()
        
    except Exception as e:
        print(f"[SERVER]  Error: {e}", file=sys.stderr)
    finally:
        connection_socket.close()

if __name__ == "__main__":
    main()
