from struct import unpack
import logging

SIZE_TYPE_OF_MESSAGE = 1
SIZE_AGENCY = 1
SIZE_NACIMIENTO = 10
SIZE_NUMERO = 4


def traduce_bet_from_bytes_to_object(bytes_recvd):
    agency_id = bytes_recvd[0:SIZE_AGENCY].decode('utf-8')
    name_len = int(unpack('!i', bytes_recvd[SIZE_AGENCY:SIZE_AGENCY+SIZE_NUMERO])[0])
    name = bytes_recvd[
        SIZE_AGENCY+SIZE_NUMERO:
        SIZE_AGENCY+name_len+SIZE_NUMERO
    ].decode('utf-8')
    surname_len = int(unpack('!i', bytes_recvd[
        SIZE_AGENCY+SIZE_NUMERO+name_len:
        SIZE_AGENCY+SIZE_NUMERO*2+name_len
    ])[0])
    surname = bytes_recvd[
        SIZE_AGENCY+SIZE_NUMERO*2+name_len:
        SIZE_AGENCY+SIZE_NUMERO*2+name_len+surname_len
    ].decode('utf-8')
    document = int(unpack('!i', bytes_recvd[
        SIZE_AGENCY+SIZE_NUMERO*2+name_len+surname_len:
        SIZE_AGENCY+SIZE_NUMERO*3+name_len+surname_len
    ])[0])
    birth_day = bytes_recvd[
        SIZE_AGENCY+SIZE_NUMERO*3+name_len+surname_len:
        SIZE_AGENCY+SIZE_NUMERO*3+name_len+surname_len+SIZE_NACIMIENTO
    ].decode('utf-8')
    number = int(unpack('!i', bytes_recvd[
        SIZE_AGENCY+SIZE_NUMERO*3+name_len+surname_len+SIZE_NACIMIENTO:
        SIZE_AGENCY+SIZE_NUMERO*4+name_len+surname_len+SIZE_NACIMIENTO
    ])[0])
    return {
        "agency": agency_id,
        "name": name,
        "surname": surname,
        "document": document,
        "birth_day": birth_day,
        "number": number
    }


TYPES_OF_MESSAGE = {
    "B": {
        "type": "BET",
        "traducer": traduce_bet_from_bytes_to_object
    },
    "E": {
        "type": "END_BETS",
        "traducer": lambda _: None
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
