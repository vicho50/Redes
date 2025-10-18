import socket
import sys
from tcp.stop_and_wait import SocketTCP

def main():
    HOST = 'localhost'
    PORT = 5000
    
    client_socket = SocketTCP()
    
    # Conectar (3-way handshake)
    if not client_socket.connect((HOST, PORT)):
        print("[CLIENT]  Error estableciendo conexión")
        return
    
    try:
        file_path = input("Ingrese la ruta del archivo a enviar: ")
        
        with open(file_path, 'rb') as file:
            message = file.read()
        
        print(f"[CLIENT] Enviando archivo de {len(message)} bytes")
        
        # Enviar mensaje
        if client_socket.send(message):
            print(f"[CLIENT]  Archivo enviado exitosamente")
        else:
            print(f"[CLIENT]  Error enviando archivo")
        
    except FileNotFoundError:
        print("[CLIENT]  Archivo no encontrado")
    except Exception as e:
        print(f"[CLIENT]  Error: {e}")
    finally:
        # Cerrar conexión (envía FIN)
        client_socket.close()

if __name__ == "__main__":
    main()