import sys
from tcp.stop_and_wait import SocketTCP

def main():
    HOST = 'localhost'
    PORT = 5000
    
    server_socket = SocketTCP()
    server_socket.bind((HOST, PORT))
    
    print(f"[SERVER] Escuchando en {HOST}:{PORT}", file=sys.stderr)
    
    # Aceptar conexión (3-way handshake)
    connection_socket, client_address = server_socket.accept()
    print(f"[SERVER] Cliente conectado: {client_address}", file=sys.stderr)
    
    try:
        # Recibir mensaje completo
        message = connection_socket.recv(buff_size=1024*1024)
        
        print(f"[SERVER] Mensaje recibido: {len(message)} bytes", file=sys.stderr)
        
        # Escribir a stdout
        sys.stdout.buffer.write(message)
        sys.stdout.buffer.flush()
        
        # Esperar cierre de conexión (FIN del cliente)
        connection_socket.recv_close()
        
    except Exception as e:
        print(f"[SERVER]  Error: {e}", file=sys.stderr)
    finally:
        # Cerrar socket del servidor
        connection_socket.socket.close()
        print(f"[SERVER]  Servidor cerrado", file=sys.stderr)

if __name__ == "__main__":
    main()
