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
            return self.__handleBet(traducedMessage["message"])
        elif traducedMessage["type"] == "END_BETS":
            return self.__handleEnd()


    def __handleBet(self, bet):
        store_bets([Bet(
            bet["agency"],
            bet["name"],
            bet["surname"],
            str(bet["document"]),
            bet["birth_day"],
            str(bet["number"])
        )])
        logging.info(f'action: apuesta_almacenada | result: success | dni: ${bet["document"]} | numero: ${bet["number"]}')
        return bet
    

    def __handleEnd(self):
        self.agenciesEnded += 1
        return "END"

    