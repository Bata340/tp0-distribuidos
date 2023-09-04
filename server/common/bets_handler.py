from common.message_traducer import traduce_message, winner_to_bytes
from common.utils import store_bets, load_bets, has_won
import logging
from multiprocessing import Lock

NUM_AGENCIES = 5

class BetsHandler:

    def __init__(self):
        self.betsMade = []
        self.agenciesEnded = 0
        self.agenciesIdEnded = []
        self.fileLock = Lock()


    def handleMessasge(self, message, return_value, agencies_ended):
        traducedMessage = traduce_message(message)
        if traducedMessage["type"] == "BET":
            return_value.put(None)
            return {
                "type": "BET",
                "message": self.__handleBatch(traducedMessage["message"])
            }
        elif traducedMessage["type"] == "END_BETS":
            return {
                "type": "END_BETS",
                "message": self.__handleEnd(traducedMessage["message"]["agency_id"], return_value, agencies_ended)
            }
        

    def __get_winners(self, agency_id, agencies_ended):
        if len(agencies_ended) < NUM_AGENCIES:
            return b"P"
        winners = b"W"
        self.fileLock.acquire()
        for bet in load_bets():
            if has_won(bet) and int(bet.agency) == int(agency_id):
                winners += winner_to_bytes(bet.document)
        self.fileLock.release()
        return winners
        


    def __handleBatch(self, batch):
        self.fileLock.acquire()
        store_bets(batch)
        self.fileLock.release()
        for bet in batch:
            logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')
        return None
    

    def __handleEnd(self, agency_id, return_value, agencies_ended):
        return_value.put(agency_id)
        if not (agency_id in agencies_ended):
            agencies_ended.append(agency_id)
        return self.__get_winners(agency_id, agencies_ended)

    