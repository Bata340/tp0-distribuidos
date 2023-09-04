import logging
from struct import unpack
import socket
import errno

MAX_SIZE = 8192

class ServerSocket:


    def __init__(self, port, listen_backlog):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)


    def send(self, client_socket, msg_bytes):
        '''
        Send that avoids short writes
        '''
        size_sent = 0
        while size_sent < len(msg_bytes):
            iter_sent_size = client_socket.send(msg_bytes[size_sent:])
            size_sent += iter_sent_size
        return size_sent


    def receive(self, client_sock):
        '''
        Receive that avoids short reads and receives message size from client
        '''
        # Receives size
        size_recvd = 0
        length_chunk = b""
        while size_recvd < 4:
            length_of_message_bytes = client_sock.recv(4)
            size_recvd = len(length_of_message_bytes)
            length_chunk += length_of_message_bytes
        length_of_msg = int(unpack("!i", length_chunk)[0])
        logging.debug(f"Length of message to receive is: {length_of_msg}. Now reading...")

        # Receives a message which has the length that was previously received from client
        size_recvd = 0
        bytes_recvd = b""
        while size_recvd < length_of_msg:
            msg_bytes = client_sock.recv(min(length_of_msg - size_recvd, MAX_SIZE))
            bytes_recvd += msg_bytes
            size_recvd += len(msg_bytes)
        logging.debug(f"Message received correctly.")
        return bytes_recvd


    def shutdown(self):
        logging.info("[ServerSocket] Shutting down...")
        # Close connection and send EOF to peers
        self._server_socket.shutdown(socket.SHUT_RDWR)
        # Deallocates socket
        self._server_socket.close()
        logging.info("[ServerSocket] Shutted down correctly...")


    def accept_client(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        try:
            c, addr = self._server_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except OSError as osError:
            if osError.errno == errno.EBADF:
                logging.info("[ServerSocket] Socket closed. Won't be accepting any more incoming connections.")
                return None
            else:
                logging.error(f"[ServerSocket] An error has ocurred when trying to accept: ${osError}")
                return None
        

