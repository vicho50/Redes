import socket
import sys
import random
import time

def main():
    # Borra esto despues waton, acá va la confi del socket UDP
    HOST = 'localhost'
    PORT = 5000
    CHUNK_SIZE = 16
    
    #Cosas pa los test , comentar LOSS y DELAY para el test 1 del paso 1
    SIMULATE_LOSS = False # para test 1 es False
    LOSS_PROBABILITY = 0.20
    DELAY = 0.5
    
    # BORRA DSP BENJA acá se crea el socket UDP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # AYYY BENJAAAAA lee la ruta del archivoooo pero desde la entrada estándar
        file_path = input("Ingrese la ruta del archivo a enviar: ")
        
        # Abrir y leer el archivo waton, no se si le sabes
        
        with open(file_path, 'rb') as file:
            chunk_number = 0
            sent_count = 0
            lost_count = 0
            while True:
                # Maximo 16 bytes, no se aceptan watones
                chunk = file.read(CHUNK_SIZE)
                
                # si no quedan gatitas salimos
                if not chunk:
                    break
                
                # sim Delay
                if SIMULATE_LOSS and DELAY > 0:
                    time.sleep(DELAY)
                    
                # sim perdida
                if SIMULATE_LOSS and random.random() < LOSS_PROBABILITY:
                    lost_count += 1
                    print(f"Simulando perdida del chunk {chunk_number}: {chunk}")
                else:
                    client_socket.sendto(chunk, (HOST, PORT))
                    sent_count += 1
                    print(f"Enviado chunk {chunk_number}: {chunk}")
                chunk_number += 1
        print(f"Total chunks enviados: {sent_count}")
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