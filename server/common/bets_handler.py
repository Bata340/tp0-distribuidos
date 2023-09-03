from common.message_traducer import traduce_message, winner_to_bytes
from common.utils import store_bets, load_bets, has_won
import logging

NUM_AGENCIES = 5

class BetsHandler:

    def __init__(self):
        self.betsMade = []
        self.agenciesEnded = 0
        self.agenciesIdEnded = []


    def handleMessasge(self, message):
        traducedMessage = traduce_message(message)
        if traducedMessage["type"] == "BET":
            return {
                "type": "BET",
                "message": self.__handleBatch(traducedMessage["message"])
            }
        elif traducedMessage["type"] == "END_BETS":
            return {
                "type": "END_BETS",
                "message": self.__handleEnd(traducedMessage["message"]["agency_id"])
            }
        

    def __get_winners(self, agency_id):
        if self.agenciesEnded < NUM_AGENCIES:
            return b"P"
        winners = b"W"
        for bet in load_bets():
            if has_won(bet) and int(bet.agency) == int(agency_id):
                winners += winner_to_bytes(bet.document)
        return winners
        


    def __handleBatch(self, batch):
        store_bets(batch)
        for bet in batch:
            logging.info(f'action: apuesta_almacenada | result: success | dni: ${bet.document} | numero: ${bet.number}')
        return None
    

    def __handleEnd(self, agency_id):
        if not (agency_id in self.agenciesIdEnded):
            self.agenciesEnded += 1
            self.agenciesIdEnded.append(agency_id)
            if self.agenciesEnded == NUM_AGENCIES:
                logging.info("action: sorteo | result: success")
        return self.__get_winners(agency_id)

    