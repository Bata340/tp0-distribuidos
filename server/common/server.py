from threading import Thread
import logging
from common.bets_handler import BetsHandler
from common.server_socket import ServerSocket
from common.process_joiner import Joiner
import multiprocessing as mp
from queue import Queue

MAX_SIZE = 8192
NUM_AGENCIES = 5

class Server:
    def __init__(self, port, listen_backlog):
        self.bets_handler = BetsHandler()
        self.should_end_loop = False
        self.serverSocket = ServerSocket(port, listen_backlog)
        self.finished_agencies = []
        self.process_queue = Queue()
        self.joiner = Thread(target=self.join_processes)
        

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        self.joiner.start()
        # Handles shutdown of SIGTERM Gracefully
        while not self.should_end_loop:
            client_sock = self.serverSocket.accept_client()
            if not client_sock:
                break
            return_value = mp.Queue()
            process = mp.Process(target = self.__handle_client_connection, args=(client_sock,return_value,))
            process.start()
            self.process_queue.put([process, return_value])
        #Signal to finish
        self.process_queue.put((None, None))
        self.joiner.join()
        logging.debug("[SERVER] Joined Joiner correctly")

    def __handle_client_connection(self, client_sock, return_value):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            msg_bytes = self.serverSocket.receive(client_sock)
            addr = client_sock.getpeername()
            traducedMessage = self.bets_handler.handleMessasge(msg_bytes, return_value, self.finished_agencies)
            if traducedMessage["type"] == "END_BETS":
                logging.info(f'action: send_winners | result_ success | msg: {traducedMessage["message"]}')
                self.serverSocket.send(client_sock, traducedMessage["message"])
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {traducedMessage["type"]}')
        except OSError as e:
            client_sock.close()
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()


    def add_agency_id(self, agency_id):
        if not (agency_id in self.finished_agencies):
            self.finished_agencies.append(agency_id)
            if len(self.finished_agencies) == NUM_AGENCIES:
                    logging.info("action: sorteo | result: success")


    def join_processes(self):
        while True:
            child = self.process_queue.get()
            process = child[0]
            queue = child[1]
            if process == None:
                return
            process.join()
            queue_msg = queue.get()
            queue.close()
            if queue_msg != None:
                self.add_agency_id(queue_msg)

    def end_server(self):
        logging.info("[SERVER] Shutting down")
        self.serverSocket.shutdown()
        self.should_end_loop = True
        self.process_queue.put([None, None])
        logging.info("[SERVER] Shutted Down Gracefully")