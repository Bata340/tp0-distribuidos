package common

import (
	"fmt"
	"time"
	"os"
	"strconv"
	log "github.com/sirupsen/logrus"
)

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopLapse     time.Duration
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	socket *ClientSocket
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
	}
	return client
}


func (c *Client) createClientSocket() error {
	c.socket = NewClientSocket(c.config)
	return nil
}


func (c *Client) StartClientLoop() {
	doc, errDocAtoi := strconv.Atoi(os.Getenv("DOCUMENTO"))
	if errDocAtoi != nil{
		log.Errorf("Error al tomar el documento desde las variables de entorno: %v", errDocAtoi)
		return
	}
	num, errNum := strconv.Atoi(os.Getenv("NUMERO"))
	if errNum != nil{
		log.Errorf("Error al tomar el número desde las variables de entorno: %v", errNum)
		return
	}

	err := c.sendBet(
		os.Getenv("NOMBRE"), 
		os.Getenv("APELLIDO"), 
		doc,
		os.Getenv("NACIMIENTO"),
		num,
	)
	if err != nil{
		log.Errorf("Error al enviar la apuesta: %v", err)
		return
	}
	errEnd := c.sendEnd()
	if errEnd != nil{
		log.Errorf("Error al enviar el mensaje de END: %v", err)
	}

	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}


func (c *Client) End() {
	log.Infof("[CLIENT] Shutting down Socket...")
	c.socket.CloseSocket()
	log.Infof("[CLIENT] Socket closed, ending instance...")
}


func (c *Client) sendBet(nombre string, apellido string, documento int, nacimiento string, numero int) error {
	bytesToSend, err := BetToBytes(nombre, apellido, documento, nacimiento, numero, c.config.ID)
	c.createClientSocket()
	if err != nil{
		return fmt.Errorf("%v", err)
	}
	log.Infof("\n[CLIENT] Sending bet...")
	c.socket.Send(bytesToSend, len(bytesToSend))
	_, err_recv := c.socket.Receive(len(bytesToSend))
	c.socket.CloseSocket()
	if err_recv != nil {
		return fmt.Errorf("Error sending bet: %v", err_recv)
	}
	log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v", documento, numero)
	return nil
} 

func (c *Client) sendEnd() error{
	bytesToSend := []byte{byte('E')}
	c.createClientSocket()
	log.Infof("\n[CLIENT] Sending END...")
	c.socket.Send(bytesToSend, len(bytesToSend))
	log.Infof("Sent END Succesfully...")
	_, err := c.socket.Receive(len(bytesToSend))
	c.socket.CloseSocket()
	if err != nil {
		return fmt.Errorf("Error sending END: %v", err)
	}
	return nil
}
