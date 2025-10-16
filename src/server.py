import socket
import sys

def main():
    # ola configurazao socket UDP
    HOST = 'localhost'
    PORT = 5000
    BUFFER_SIZE = 1024
    
    #CREO LA VAINA
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # AYYY BENJA acá se hace el bind del socket
    server_socket.bind((HOST, PORT))
    print(f"Servidor UDP escuchando en {HOST}:{PORT}")
    
    try:
        while True:
            # RECIBO LA DATA
            data, client_address = server_socket.recvfrom(BUFFER_SIZE)
            
            # PRINT
            # USAR sys.stdout.buffer para escribir bytes directamente
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()  
            
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server_socket.close()
        
if __name__ == "__main__":
    main()
            