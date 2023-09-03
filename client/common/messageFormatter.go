package common

import (
	"encoding/binary"
	"fmt"
)

const (
	SIZE_NACIMIENTO = 10
	SIZE_NUMERO = 4
	SIZE_TYPE_OF_MSG = 1
)


func GetBatchIdentifier(agencyID string) [] byte {
	return []byte{byte('B'), byte(agencyID[0])}
}

func BetToBytes(nombre string, apellido string, documento int, nacimiento string, numero int) ([]byte, error){
	bytesNombre := []byte(nombre)
	bytesApellido := []byte(apellido)
	bytesDoc := make([]byte,SIZE_NUMERO)
	binary.BigEndian.PutUint32(bytesDoc, uint32(documento))
	bytesNacimiento := []byte(nacimiento)
	bytesNumero := make([]byte,SIZE_NUMERO)
	binary.BigEndian.PutUint32(bytesNumero, uint32(numero))
	if len(nacimiento) != SIZE_NACIMIENTO{
		return make([]byte, 0), fmt.Errorf("Size of birth date is too long for message.")
	}
	sizeOfName := make([]byte,SIZE_NUMERO)
	binary.BigEndian.PutUint32(sizeOfName, uint32(len(bytesNombre)))
	sizeOfSurname := make([]byte,SIZE_NUMERO)
	binary.BigEndian.PutUint32(sizeOfSurname, uint32(len(bytesApellido)))
	bytesNombre = append(sizeOfName, bytesNombre...)
	bytesApellido = append(sizeOfSurname, bytesApellido...)
	finalMessage := append(bytesNombre, bytesApellido...)
	finalMessage = append(finalMessage, bytesDoc...)
	finalMessage = append(finalMessage, bytesNacimiento...)
	finalMessage = append(finalMessage, bytesNumero...)
	return finalMessage, nil
}


func TraduceWinners(bytes []byte) (string, []int) {
	typeMessage := string(bytes[0])
	if typeMessage == "P"{
		return "PENDING", []int{}
	}else{
		restOfBytes := bytes[1:];
		lengthOfBytes := len(restOfBytes)
		currOffset := 0
		winners := []int{}
		for currOffset < lengthOfBytes{
			dni := int(binary.BigEndian.Uint32(restOfBytes[currOffset:currOffset+4]))
			winners = append(winners, dni)
			currOffset += 4
		}
		return "WINNERS", winners
	}

}