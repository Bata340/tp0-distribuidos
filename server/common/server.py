import socket
import logging
from common.bets_handler import BetsHandler
from common.server_socket import ServerSocket

MAX_SIZE = 8192

class Server:
    def __init__(self, port, listen_backlog):
        self.bets_handler = BetsHandler()
        self.should_end_loop = False
        self.serverSocket = ServerSocket(port, listen_backlog)
        

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        # Handles shutdown of SIGTERM Gracefully
        while not self.should_end_loop:
            client_sock = self.serverSocket.accept_client()
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
            msg_bytes = self.serverSocket.receive(client_sock)
            addr = client_sock.getpeername()
            traducedMessage = self.bets_handler.handleMessasge(msg_bytes)
            if traducedMessage["type"] == "END":
                #TODO: Ejercicio 7 - Agregar el llamado para obtener los ganadores
                self.serverSocket.send(client_sock, msg_bytes)
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {[traducedMessage["message"]]}')
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()


    def end_server(self):
        logging.info("[SERVER] Shutting down")
        self.serverSocket.shutdown()
        logging.info("[SERVER] Shutted Down Gracefully")