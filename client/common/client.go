package common

import (
	"fmt"
	"time"

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

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	c.socket = NewClientSocket(c.config)
	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	msgID := 1
loop:
	// Send messages if the loopLapse threshold has not been surpassed
	for timeout := time.After(c.config.LoopLapse); ; {
		select {
		case <-timeout:
	        log.Infof("action: timeout_detected | result: success | client_id: %v",
                c.config.ID,
            )
			break loop
		default:
		}

		// Create the connection the server in every loop iteration. Send an
		c.createClientSocket()
		msg, err := c.sendBet("Nombre", "Apellido", 42676004, "2000-06-30", msgID)
		c.socket.CloseSocket()
		msgID++

		if err != nil {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
                c.config.ID,
				err,
			)
			return
		}
		log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
            c.config.ID,
            msg,
        )

		// Wait a time between sending one message and the next one
		time.Sleep(c.config.LoopPeriod)
	}

	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}


func (c *Client) End() {
	fmt.Println("\n[CLIENT] Shutting down Socket...")
	c.socket.CloseSocket()
	fmt.Println("\n[CLIENT] Socket closed, ending instance...")
}


func (c *Client) sendBet(nombre string, apellido string, documento int, nacimiento string, numero int) ([]byte, error){
	bytesToSend, err := BetToBytes(nombre, apellido, documento, nacimiento, numero)
	if err != nil{
		return nil, fmt.Errorf("%v", err)
	}
	fmt.Println("\n[CLIENT] Sending bet...")
	c.socket.Send(bytesToSend, len(bytesToSend))
	fmt.Println("\n[CLIENT] Bet Sent! ", "Name: ", nombre, "; Surname: ", apellido, "; Document: ", documento, "; Born in: ", nacimiento, "; Number: ", numero)
	bytes, err := c.socket.Receive(len(bytesToSend))
	if err != nil {
		return nil, fmt.Errorf("%v", err)
	}
	return bytes, nil
} 
