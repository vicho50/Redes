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
        # Socket UDP
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
        
        
    def send(self, data):
        """
        Envia datos de manera confiable al address remoto previamente configurado
        Espera ACK

        Args:
            data: bytes a enviar
            
        Returns:
            True si funca, False si no
        """
        if not self.remote_address:
            raise ValueError("Dirección remota no configurada.")
        
        # crear pack
        packet = struct.pack('B', self.seq_num) + data
        
        retries = 0
        while retries < self.max_retrys:
            try:
                # mandar pack
                self.socket.sendto(packet, self.remote_address)
                self.packets_sent += 1
                print(f"[SEND] Seq: {self.seq_num}, Retries: {retries}, Size: {len(data)} bytes")
                
                # confi Tout para el ACK
                self.socket.settimeout(self.timout)
                
                # waiteamos el ACK
                ack_packet, _ = self.socket.recvfrom(self.buffer_size)
                ack_seq = struct.unpack('B', ack_packet[:1])[0]
                
                # chequeamos que el ACK sea el correcto
                if ack_seq == self.seq_num:
                    print(f"[ACK] Seq: {ack_seq} recibido correctamente.")
                    self.seq_num = 1 - self.seq_num  # Alternar entre 0 y 1 (S&W)
                    return True
                else:
                    print(f"[ACK] Seq: {ack_seq} incorrecto, esperando {self.seq_num}.")
            
            except socket.timeout:
                retries += 1
                self.retransmissions += 1
                print(f"[TIMEOUT] Retransmitiendo paquete con Seq: {self.seq_num}. Intento {retries}/{self.max_retrys}")
        
        print(f"[FAIL] No se pudo enviar el paquete con Seq: {self.seq_num} después de {self.max_retrys} intentos.")
        return False
    
    def recv(self, max_bytes=16):
        """
        Recibe la data de forma confiable
        Envía ACK auto
        
        Args:
            max_bytes: maximo de bytes a recibir
        
        Returns:
            bytes recibidos (sin el header de secuencia)
        """
        
        # N° de seq esperado (parte en 0)
        if not hasattr(self, 'expected_seq'):
            self.expected_seq = 0
        
        while True:
            # recibir pack
            packet, sender_address = self.socket.recvfrom(self.buffer_size)
            self.packets_received += 1
            
            # guarda la direccion del remitente si no ta etablecida
            if not self.remote_address:
                self.remote_address = sender_address
                
            # extraer n° de seq y data
            seq_num = struct.unpack('B', packet[:1])[0]
            data = packet[1:]
            print(f"[RECV] Seq: {seq_num}, Size: {len(data)} bytes, desde: {sender_address}")
            
            # mandar ACK con el n° de seq recibido
            ack_packet = struct.pack('B', seq_num)
            self.socket.sendto(ack_packet, sender_address)
            print(f"[ACK] Enviando ACK para Seq: {seq_num}")
            
            # Si es el pack esperado, retornar data y actualizar n° de seq esperado
            if seq_num == self.expected_seq:
                self.expected_seq = 1 - self.expected_seq  # Alternar entre 0 y 1
                return data
            else:
                print(f"[DUPLICATE] Paquete duplicado con Seq: {seq_num} recibido, esperando {self.expected_seq}. Ignorando data.")
                # Si es duplicado, simplemente ignorar la data (ACK ya fue enviado)
                continue
    def close(self):
        """
        Cierra el socket y libera recursos
        """
        self.socket.close()
        print(f"Paquetes enviados: {self.packets_sent}")
        print(f"Paquetes recibidos: {self.packets_received}")
        print(f"Retransmisiones: {self.retransmissions}")
