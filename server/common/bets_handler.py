from common.message_traducer import traduce_message
from common.utils import store_bets, Bet
import logging

class BetsHandler:

    def __init__(self):
        self.betsMade = []
        self.agenciesEnded = 0


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
                "message": self.__handleEnd()
            }
        

    def get_winners(self):
        pass


    def __handleBatch(self, batch):
        store_bets(batch)
        for bet in batch:
            logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')
        return bet
    

    def __handleEnd(self):
        self.agenciesEnded += 1
        return "END"

    