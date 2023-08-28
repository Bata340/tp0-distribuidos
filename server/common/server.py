import socket
import logging
from struct import unpack
from common.message_traducer import traduce_bet_from_bytes_to_object

MAX_SIZE = 8192

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self.should_end_loop = False
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        # Handles shutdown of SIGTERM Gracefully
        while not self.should_end_loop:
            client_sock = self.__accept_new_connection()
            if not client_sock:
                break
            self.__handle_client_connection(client_sock)

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            msg_bytes = self.__receive(client_sock)
            addr = client_sock.getpeername()
            bet_data = traduce_bet_from_bytes_to_object(msg_bytes)
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {bet_data}')
            self.__send(client_sock, msg_bytes)
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
    

    def end_server(self):
        logging.info("[SERVER] Shutting down")
        self.should_end_loop = True
        # Close connection and send EOF to peers
        self._server_socket.shutdown(socket.SHUT_RDWR)
        # Deallocates socket
        self._server_socket.close()
        logging.info("[SERVER] Shutted Down Gracefully")


    def __send(self, client_sock, msg_bytes):
        # Send that avoids short writes
        size_sent = 0
        while size_sent < len(msg_bytes):
            iter_sent_size = client_sock.send(msg_bytes)
            size_sent += iter_sent_size
        return size_sent

    
    def __receive(self, client_sock):
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
