import socket
import struct

class SocketTCP:
    """
    Clase que comunica de manera confiable sobre UDP usando el para y holdea cabron
    Almacena todos los recursos necesarios para pasar el contenido linguistico que se intenta transmitir uknow?
    """
    
    def __init__(self):
        """
        Constructor sin parametros
        Inicializa todos los recursos necesarios para entablas una interacción que busca el paso de informacion de una parte a la otra AKA comunicación
        """
        # Socket TCP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Direcciones
        self.local_address = None
        self.remote_address = None
        
        # N° seq
        self.seq_num = 0
        
        # Tout y retransmisiones
        self.timout = 2.0
        self.max_retrys = 5
        
        # Buffer
        self.buffer_size = 1024
        
        # stats para debug
        self.packets_sent = 0
        self.packets_received = 0
        self.retransmissions = 0
        
    def bind(self, address):
        """
        Asocia el socket a una direccion local

        Args:
            address: Tuple (host, port)
        """
        self.socket.bind(address)
        self.local_address = address
        
        
    def send(self, message):
        """
        Envía un mensaje completo dividiéndolo en chunks con Stop & Wait.

        Args:
            message: bytes - Mensaje completo a enviar
            
        Returns:
            True si se envió exitosamente, False si falló
        """
        if not self.remote_address:
            raise ValueError("Dirección remota no configurada.")
        
        # paso 1: enviar largo del msg
        message_length = len(message)
        length_data = struct.pack('!I', message_length)
        
        print(f"[SEND] Enviando longitud del mensaje: {message_length} bytes")
        
        # Crear y enviar segmento de longitud
        length_segment = self.create_segment(
            seq=self.seq_num,
            data=length_data,
            ack=False
        )
        
        # Enviar con retransmisiones
        
        if not self._send_with_retry(length_segment):
            print(f"[SEND] Error enviando longitud del mensaje.")
            return False
        
        # paso 2: enviar data en chunks
        CHUNK_SIZE = 16
        offset = 0
        chunk_number = 0
        
        while offset < message_length:
            # extraer chunk
            chunk = message[offset:offset+CHUNK_SIZE]
            
            print(f"[SEND] Enviando chunk {chunk_number}: {len(chunk)} bytes (offset {offset})")
            
            # crear segmento con el chunk
            data_segment = self.create_segment(
                seq=self.seq_num,
                data=chunk,
                ack=False
            )
            
            # Enviar con retransmisiones
            if not self._send_with_retry(data_segment):
                print(f"[SEND] Error enviando chunk {chunk_number}.")
                return False
            
            offset += len(chunk)
            chunk_number += 1
        
        print(f"[SEND] Mensaje enviado exitosamente.")
        return True
    
    def _send_with_retry(self, segment):
        """
        Método auxiliar para enviar un segmento con retransmisiones y timeout
        
        Args:
            segment: bytes - Segmento completo
            
        Returns:
            True si se envió y recibió ACK, False si falló
        """
        retries = 0
        
        while retries <= self.max_retrys:
            try:
                # Enviar segmento
                self.socket.sendto(segment, self.remote_address)
                self.packets_sent += 1
                
                # timout
                self.socket.settimeout(self.timout)
                
                # Esperar ACK
                ack_segment, _ = self.socket.recvfrom(self.buffer_size)
                ack_info = self.parse_segment(ack_segment)
                
                # Verificar ACK
                if ack_info['ack'] and ack_info['seq'] == self.seq_num:
                    print(f"[SEND] Recibido ACK para Seq: {self.seq_num}")
                    # Actualizar n° de seq
                    self.seq_num = 1 - self.seq_num 
                    return True
                else:
                    print(f"[SEND] ACK inválido recibido. Esperando Seq: {self.seq_num}")
            
            except socket.timeout:
                retries += 1
                self.retransmissions += 1
                print(f"[SEND] timeout esperando ACK. Retransmisión {retries}/{self.max_retrys}")
        
        print(f"[SEND] Máximo de retransmisiones alcanzado. Fallo al enviar segmento.")
        return False
                
                
            
    
    def recv(self, buff_size=1024):
        """
        Recibe un mensaje completo usando Stop & Wait
        
        Args:
            buff_size: int - Tamaño del buffer para recibir datos
        
        Returns:
            bytes - Mensaje recibido
        """
        
       # Inicializar N° de seq esperado
        if not hasattr(self, 'expected_seq'):
           self.expected_seq = 0
        
        # paso 1: recibir largo del mensaje
        print(f"[RECV] Esperando longitud del mensaje...")
        length_data = self._recv_segment()
        if len(length_data) < 4:
            raise ValueError("Error recibiendo longitud del mensaje.")
        
        mesage_length = struct.unpack('!I', length_data[:4])[0]
        print(f"[RECV] Longitud del mensaje recibida: {mesage_length} bytes")
        
        # paso 2: recibir data en chunks
        received_data = b""
        chunk_number = 0
        
        while len(received_data) < mesage_length:
            chunk = self._recv_segment()
            received_data += chunk
            chunk_number += 1
            print(f"[RECV] Chunk {chunk_number} recibido: {len(chunk)} bytes")
        
        print(f"[RECV] Mensaje recibido exitosamente.")
        
        return received_data[:buff_size]
        
    
    def _recv_segment(self):
        """
        Método auxiliar para recibir un segmento y enviar ACK
        
        Returns:
            bytes - Payload del segmento recibido
        """
        while True:
            # Recibir segmento
            segment, sender_address = self.socket.recvfrom(self.buffer_size)
            self.packets_received += 1

            # Guardar dirección remota
            if not self.remote_address:
                self.remote_address = sender_address
            
            # Parsear segmento
            segment_info = self.parse_segment(segment)
            seq_num = segment_info['seq']
            payload = segment_info['payload']
            
            # Enviar ACK
            ack_segment = self.create_segment(
                seq=seq_num,
                data=b"",
                ack=True
            )
            self.socket.sendto(ack_segment, sender_address)

            #si es el esperado, retornarlo
            if seq_num == self.expected_seq:
                self.expected_seq = 1 - self.expected_seq
                return payload
            else:
                # Paquete duplicado, ignorar pero ACK ya fue enviado
                print(f"[DUP] Paquete duplicado Seq={seq_num}, esperado={self.expected_seq}.")
                continue


    def close(self):
        """
        Cierra el socket y libera recursos
        """
        self.socket.close()
        print(f"Paquetes enviados: {self.packets_sent}")
        print(f"Paquetes recibidos: {self.packets_received}")
        print(f"Retransmisiones: {self.retransmissions}")
    
    @staticmethod
    def parse_segment(segment):
        """"
        Parsea un segmento TCP recibido y extrae la info del header
        """
        if len(segment) < 5:
            raise ValueError("Segmento TCP demasiado corto para parsear el header.")
        
        # Extraer header (5 bytes)
        
        seq_num = struct.unpack('B', segment[0:1])[0]
        flags = struct.unpack('B', segment[1:2])[0]
        payload_size = struct.unpack('!H', segment[2:4])[0]
        checksum = struct.unpack('B', segment[4:5])[0]
        
        # Extraer payload
        payload = segment[5:5+payload_size]
        
        # deco flags
        ack_flag = bool(flags & 0x01) #0
        syn_flag = bool(flags & 0x02) #1
        fin_flag = bool(flags & 0x04) #2
        
        return {
            'seq': seq_num,
            'ack': ack_flag,
            'syn': syn_flag,
            'fin': fin_flag,
            'payload_size': payload_size,
            'payload': payload
        }
        
    @staticmethod
    def create_segment(seq, data, ack=False, syn=False, fin=False):
        """
        Crea un segmento TCP con header a partir de los datos
        """
        # construir flags
        flags = 0
        if ack:
            flags |= 0x01
        if syn:
            flags |= 0x02
        if fin:
            flags |= 0x04
            
        # Tamaño payload
        payload_size = len(data)
        
        # cacl checksum
        checksum = (seq + flags + payload_size + sum(data)) % 256
        
        # construir header
        header = struct.pack('B', seq)
        header += struct.pack('B', flags)
        header += struct.pack('!H', payload_size)
        header += struct.pack('B', checksum)
        
        # Retornar seg completo
        return header + data
    
    def connect(self, address):
        """
        Configura la direccion remota para el socket

        Args:
            address: Tuple (host, port)
        """
        self.remote_address = address
        
        import random
        self.remote_address = address
        print(f"[CONNECT] Iniciando 3-way handshake con {address}")
        # Paso 1: Enviar SYN
        self.seq_num = random.randint(0, 100)
        syn_segment = self.create_segment(
            seq=self.seq_num,
            data=b"",
            syn=True
        )
        
        print(f"[CONNECT] Enviando SYN con Seq: {self.seq_num}")
        self.socket.sendto(syn_segment, self.remote_address)
        
        # Paso 2: Esperar SYN-ACK
        try:
            self.socket.settimeout(5.0)
            response, _ = self.socket.recvfrom(self.buffer_size)
            syn_ack_info = self.parse_segment(response)
            
            if syn_ack_info['syn'] and syn_ack_info['ack']:
                print(f"[CONNECT] Recibido SYN-ACK con Seq: {syn_ack_info['seq']}")
                
                # Guardar el seq del servidor
                self.remote_seq = syn_ack_info['seq']
                
                # Paso 3: Enviar ACK
                # con seq = 0 para comenzar a enviar data
                self.seq_num = 0
                ack_segment = self.create_segment(
                    seq=self.seq_num,
                    data=b"",
                    ack=True
                )
                
                print(f"[CONNECT] Enviando ACK final")
                self.socket.sendto(ack_segment, self.remote_address)
                
                print(f"[CONNECT] Conexión establecida con {address}")
                return True
            else:
                print(f"[CONNECT] Respuesta inválida durante el handshake.")
                return False
        except socket.timeout:
            print(f"[CONNECT] Timeout esperando SYN-ACK.")
            return False
    
    def accept(self):
        """
        Espera y acepta una conexión entrante (3-way handshake)
        """
        import random
        print(f"[ACCEPT] Esperando conexión entrante...")
        
        # Paso 1: Esperar SYN
        while True:
            segment, client_address = self.socket.recvfrom(self.buffer_size)
            syn_info = self.parse_segment(segment)
            
            if syn_info['syn']:
                
                print(f"[ACCEPT] Recibido SYN con Seq: {syn_info['seq']} desde {client_address}")
                
                # guardar seq cliente
                client_seq = syn_info['seq']
                
                # Paso 2: Enviar SYN-ACK con seq aleatorio
                server_seq = random.randint(0, 100)
                syn_ack_segment = self.create_segment(
                    seq=server_seq,
                    data=b"",
                    syn=True,
                    ack=True
                )
                
                print(f"[ACCEPT] Enviando SYN-ACK con Seq: {server_seq} a {client_address}")
                self.socket.sendto(syn_ack_segment, client_address)
                
                # Paso 3: Esperar ACK final
                try:
                    self.socket.settimeout(5.0)
                    ack_segment, _ = self.socket.recvfrom(self.buffer_size)
                    ack_info = self.parse_segment(ack_segment)
                    
                    if ack_info['ack']:
                        print(f"[ACCEPT] ACK final recibido)")
                        
                        # Crear nuevo socket para la conexión
                        connection_socket = SocketTCP()
                        connection_socket.remote_address = client_address
                        connection_socket.seq_num = 0
                        connection_socket.socket = self.socket
                        connection_socket.local_address = self.local_address
                        
                        print(f"[ACCEPT] Conexión establecida con {client_address}")
                        return connection_socket, client_address
                    else:
                        print(f"[ACCEPT] Respuesta inválida durante el handshake.")
                        continue
                except socket.timeout:
                    print(f"[ACCEPT] Timeout esperando ACK final.")
                    continue
