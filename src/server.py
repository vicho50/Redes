import socket
import sys
from tcp.stop_and_wait import SocketTCP

def main():
    # ola configurazao socket UDP
    HOST = 'localhost'
    PORT = 5000
   # BUFFER_SIZE = 1024
    
    #CREO LA VAINA
    server_socket = SocketTCP()
    server_socket.bind((HOST, PORT))
    print(f"Servidor UDP escuchando en {HOST}:{PORT}")
    
    try:
        packet_count = 0
        while True:
            
            # Recibir segmento TCP
            segment, client_address = server_socket.socket.recvfrom(1024)

            # Parsear segmento
            try:
                segment_info = SocketTCP.parse_segment(segment)
                
                seq = segment_info['seq']
                payload = segment_info['payload']
                is_ack = segment_info['ack']
                is_syn = segment_info['syn']
                is_fin = segment_info['fin']
                
                print(f"[SERVER] Segmento recibido: Seq={seq}, ACK={is_ack}, SYN={is_syn}, FIN={is_fin}, Payload size={len(payload)} bytes", file=sys.stderr)
                
                # Escribir payload
                if len(payload) > 0:
                    sys.stdout.buffer.write(payload)
                    sys.stdout.buffer.flush()
                
                # Enviar ACK de vuelta
                ack_segment = SocketTCP.create_segment(
                    seq=seq,
                    data=b"",
                    ack=True,
                )
                server_socket.socket.sendto(ack_segment, client_address)
                print(f"[SERVER] Enviado ACK para Seq={seq} a {client_address}", file=sys.stderr)
                
                packet_count += 1
            except ValueError as e:
                print(f"[SERVER] Error parseando segmento: {e}", file=sys.stderr)
            
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server_socket.close()
        
if __name__ == "__main__":
    main()
            