from common.message_traducer import traduce_message
from common.utils import store_bets, Bet

class BetsHandler:

    def __init__(self):
        self.betsMade = []
        self.agencysEnded = 0


    def handleMessasge(self, message):
        traducedMessage = traduce_message(message)
        if traducedMessage["type"] == "BET":
            return self.__handleBet(traducedMessage["message"])
        elif traducedMessage["type"] == "END_BETS":
            return self.__handleEnd()

    def __handleBet(self, bet):
        self.betsMade.append(Bet(
            bet["agency"],
            bet["name"],
            bet["surname"],
            str(bet["document"]),
            bet["birth_day"],
            str(bet["number"])
        ))
        return bet
    

    def __handleEnd(self):
        store_bets(self.betsMade)
        self.agencysEnded += 1
        return "END"

    