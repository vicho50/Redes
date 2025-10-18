import socket
import sys
import random
import time
from tcp.stop_and_wait import SocketTCP

def main():
    # Borra esto despues waton, acá va la confi del socket UDP
    HOST = 'localhost'
    PORT = 5000
    CHUNK_SIZE = 16
    
    
    # BORRA DSP BENJA acá se crea el socket UDP
    client_socket = SocketTCP()
    
    if not client_socket.connect((HOST, PORT)):
        print("Error estableciendo la dirección remota del servidor.")
        return
    
    try:
        # AYYY BENJAAAAA lee la ruta del archivoooo pero desde la entrada estándar
        file_path = input("Ingrese la ruta del archivo a enviar: ")
        
        # Abrir y leer el archivo waton, no se si le sabes
        
        with open(file_path, 'rb') as file:
            chunk_number = 0

            while True:
                # Maximo 16 bytes, no se aceptan watones
                chunk = file.read(CHUNK_SIZE)
                
                # si no quedan gatitas salimos
                if not chunk:
                    break
                
                
                # Crear y enviar segmento
                segment = SocketTCP.create_segment(
                    seq=client_socket.seq_num,
                    data=chunk,
                )
                
                # Enviar chunk usando el método send() de SocketTCP
                print(f"[CLIENT] Enviando chunk {chunk_number}: {len(chunk)} bytes")
                
                if client_socket.send(chunk):
                    print(f"[CLIENT] Chunk {chunk_number} enviado exitosamente")
                else:
                    print(f"[CLIENT] Error enviando chunk {chunk_number}")
                    break
                
                chunk_number += 1
               
        # No te voy a mentir el debug se autocompleto
        print("Archivo enviado correctamente.")
    except FileNotFoundError:
        print("Error: Archivo no encontrado.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()