from struct import unpack
import logging

SIZE_NACIMIENTO = 10
SIZE_NUMERO = 4

def traduce_bet_from_bytes_to_object(bytes_recvd):
    name_len = int(unpack('!i', bytes_recvd[0:SIZE_NUMERO])[0])
    name = bytes_recvd[
        SIZE_NUMERO:
        name_len+SIZE_NUMERO
    ].decode('utf-8')
    surname_len = int(unpack('!i', bytes_recvd[SIZE_NUMERO+name_len:SIZE_NUMERO*2+name_len])[0])
    surname = bytes_recvd[
        SIZE_NUMERO*2+name_len:
        SIZE_NUMERO*2+name_len+surname_len
    ].decode('utf-8')
    document = int(unpack('!i', bytes_recvd[
        SIZE_NUMERO*2+name_len+surname_len:
        SIZE_NUMERO*3+name_len+surname_len
    ])[0])
    birth_day = bytes_recvd[
        SIZE_NUMERO*3+name_len+surname_len:
        SIZE_NUMERO*3+name_len+surname_len+SIZE_NACIMIENTO
    ].decode('utf-8')
    number = int(unpack('!i', bytes_recvd[
        SIZE_NUMERO*3+name_len+surname_len+SIZE_NACIMIENTO:
        SIZE_NUMERO*4+name_len+surname_len+SIZE_NACIMIENTO
    ])[0])
    return {
        "name": name,
        "surname": surname,
        "document": document,
        "birth_day": birth_day,
        "number": number
    }
