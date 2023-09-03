from struct import unpack, pack
import logging

SIZE_TYPE_OF_MESSAGE = 1
SIZE_AGENCY = 1
SIZE_NACIMIENTO = 10
SIZE_NUMERO = 4

from common.utils import Bet


def traduce_bet_from_bytes_to_object(bytes_recvd):
    agency_id = bytes_recvd[0:SIZE_AGENCY].decode('utf-8')
    betsArray = []
    betOffset = 0
    while betOffset + SIZE_AGENCY < len(bytes_recvd):
        name_len = int(unpack('!i', bytes_recvd[betOffset+SIZE_AGENCY:betOffset+SIZE_AGENCY+SIZE_NUMERO])[0])
        name = bytes_recvd[
            betOffset+SIZE_AGENCY+SIZE_NUMERO:
            betOffset+SIZE_AGENCY+name_len+SIZE_NUMERO
        ].decode('utf-8')
        surname_len = int(unpack('!i', bytes_recvd[
            betOffset+SIZE_AGENCY+SIZE_NUMERO+name_len:
            betOffset+SIZE_AGENCY+SIZE_NUMERO*2+name_len
        ])[0])
        surname = bytes_recvd[
            betOffset+SIZE_AGENCY+SIZE_NUMERO*2+name_len:
            betOffset+SIZE_AGENCY+SIZE_NUMERO*2+name_len+surname_len
        ].decode('utf-8')
        document = int(unpack('!i', bytes_recvd[
            betOffset+SIZE_AGENCY+SIZE_NUMERO*2+name_len+surname_len:
            betOffset+SIZE_AGENCY+SIZE_NUMERO*3+name_len+surname_len
        ])[0])
        birth_day = bytes_recvd[
            betOffset+SIZE_AGENCY+SIZE_NUMERO*3+name_len+surname_len:
            betOffset+SIZE_AGENCY+SIZE_NUMERO*3+name_len+surname_len+SIZE_NACIMIENTO
        ].decode('utf-8')
        number = int(unpack('!i', bytes_recvd[
            betOffset+SIZE_AGENCY+SIZE_NUMERO*3+name_len+surname_len+SIZE_NACIMIENTO:
            betOffset+SIZE_AGENCY+SIZE_NUMERO*4+name_len+surname_len+SIZE_NACIMIENTO
        ])[0])
        betOffset += SIZE_NUMERO*4+name_len+surname_len+SIZE_NACIMIENTO
        betsArray.append(Bet(
            agency_id,
            name,
            surname,
            str(document),
            birth_day,
            str(number)
        ))
    return betsArray


def traduce_agency_id_from_end_msg(msg):
    return {"agency_id": msg[0:].decode('utf-8')}


TYPES_OF_MESSAGE = {
    "B": {
        "type": "BET",
        "traducer": traduce_bet_from_bytes_to_object
    },
    "E": {
        "type": "END_BETS",
        "traducer": traduce_agency_id_from_end_msg 
    }
}

def __get_type_of_message(bytes_type):
    type_code = bytes_type.decode('utf-8')
    type_data = TYPES_OF_MESSAGE[type_code]
    return type_data


def traduce_message(bytes_recvd):
    type_of_message = __get_type_of_message(bytes_recvd[0:SIZE_TYPE_OF_MESSAGE])
    return {
        "type": type_of_message["type"],
        "message": type_of_message["traducer"](bytes_recvd[SIZE_TYPE_OF_MESSAGE:])
    }


def winner_to_bytes(dni):
    '''
    Packs winner as DNI and number in an 8 bytes message (Two ints)
    '''
    return pack("!i", int(dni))
