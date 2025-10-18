import socket
import sys
import random
import time
from tcp.stop_and_wait import SocketTCP

def main():
    HOST = 'localhost'
    PORT = 5000
    
    client_socket = SocketTCP()
    
    if not client_socket.connect((HOST, PORT)):
        print("[CLIENT] No se pudo conectar")
        return
    
    try:
        file_path = input("Ingrese la ruta del archivo a enviar: ")
        
        # Leer todo el archivo
        with open(file_path, 'rb') as file:
            message = file.read()
        
        print(f"[CLIENT] Enviando archivo de {len(message)} bytes")
        
        # Enviar mensaje completo (send() lo divide en chunks)
        if client_socket.send(message):
            print(f"[CLIENT]  Archivo enviado exitosamente")
        else:
            print(f"[CLIENT]  Error enviando archivo")
        
    except FileNotFoundError:
        print(f"[CLIENT]  Archivo no encontrado")
    except Exception as e:
        print(f"[CLIENT]  Error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()