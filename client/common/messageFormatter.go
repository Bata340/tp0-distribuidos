package common

import (
	"encoding/binary"
	"fmt"
)

const (	
	SIZE_NAME = 200
	SIZE_SURNAME = 200
	SIZE_DOCUMENTO = binary.MaxVarintLen64
	SIZE_NACIMIENTO = 10
	SIZE_NUMERO = binary.MaxVarintLen64
	SIZE_MESSAGE = 418
)

func BetToBytes(nombre string, apellido string, documento int, nacimiento string, numero int) ([]byte, error){

	bytesNombre := []byte(nombre)
	bytesApellido := []byte(apellido)
	bytesDoc := make([]byte,SIZE_DOCUMENTO)
	binary.PutVarint(bytesDoc, int64(documento))
	bytesNacimiento := []byte(nacimiento)
	bytesNumero := make([]byte,SIZE_NUMERO)
	binary.PutVarint(bytesNumero, int64(numero))
	if SIZE_NAME - len(bytesNombre) < 0{
		return make([]byte, 0), fmt.Errorf("Size of name is too long for message.")
	}
	if SIZE_SURNAME - len(bytesApellido) < 0{
		return make([]byte, 0), fmt.Errorf("Size of surname is too long for message.")
	}
	if len(nacimiento) != SIZE_NACIMIENTO{
		return make([]byte, 0), fmt.Errorf("Size of birth date is too long for message.")
	}
	bytesNombre = append(bytesNombre, make([]byte, SIZE_NAME - len(bytesNombre))...)
	bytesApellido = append(bytesApellido, make([]byte, SIZE_SURNAME - len(bytesApellido))...)
	finalMessage := append(bytesNombre, bytesApellido...)
	finalMessage = append(finalMessage, bytesDoc...)
	finalMessage = append(finalMessage, bytesNacimiento...)
	finalMessage = append(finalMessage, bytesNumero...)
	return finalMessage, nil
}