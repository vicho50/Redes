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
    client_socket.set_remote_address((HOST, PORT))
    
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
                
                """
                Crear segmento TCP con header
                """
                segment = SocketTCP.create_segment(
                    seq = client_socket.seq_num,
                    data = chunk,
                    ack = False,
                    syn = False,
                    fin = False,
                )
                
                print(f"[CLIENT] Envando chunk {chunk_number}: {len(chunk)} bytes")
                
                client_socket.socket.sendto(segment, (HOST, PORT))
                
                # Esperar ACK
                try:
                    client_socket.socket.settimeout(2.0)
                    ack_segment, _ = client_socket.socket.recvfrom(1024)
                    
                    #Parsear ACK
                    ack_info = SocketTCP.parse_segment(ack_segment)
                    if ack_info['ack'] and ack_info['seq'] == client_socket.seq_num:
                        print(f"[CLIENT] ACK recibido para seq={client_socket.seq_num}")
                        # alterar numero de secuencia
                        client_socket.seq_num = 1 - client_socket.seq_num
                except socket.timeout:
                    print(f"[CLIENT] timout esperando ACK")
                    
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