package common

import (
	"fmt"
	"time"
	"os"
	"io"
	"encoding/csv"
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
	betsPerBatch, err := strconv.Atoi(os.Getenv("BETS_PER_BATCH"))
	if err != nil {
		log.Errorf("Error al obtener la cantidad de apuestas por batch: %v", err)
		return
	}
	err = c.sendBetsAsBatch(betsPerBatch)
	if err != nil{
		log.Errorf("Error al enviar las apuestas: %v", err)
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


func (c *Client) sendBetsAsBatch(sizePerBatch int) error {
	idBatch := 0
	bytesBatchIdentifier := GetBatchIdentifier(c.config.ID)
	file, err := os.Open("data/agency-"+c.config.ID+".csv")
	if err != nil {
		log.Errorf("Error opening the agency csv file: %v", err)
		return err
	}
	defer file.Close()
	reader := csv.NewReader(file)
	filesInCurrentBatch := 0
	currBatch := bytesBatchIdentifier
	for {
		line, err := reader.Read()
		if err != nil {
			if err == io.EOF {
				if len(currBatch) > 2 {
					c.createClientSocket()
					c.socket.Send(currBatch, len(currBatch))
					c.socket.CloseSocket()
				}
				break
			}
			log.Errorf("Error reading CSV line: %v", err)
			return err
		}
		dni, errDni := strconv.Atoi(line[2])
		if errDni != nil{
			log.Errorf("Error reading DNI from line: %v", errDni)
			return errDni
		}
		betNum, errNum := strconv.Atoi(line[4])
		if errNum != nil{
			log.Errorf("Error reading Bet Number from line: %v", errNum)
			return errNum
		}
		bytesToSend, err := BetToBytes(line[0], line[1], dni, line[3], betNum)
		if err != nil{
			log.Errorf("Error transforming bet to bytes: %v", err)
			return err
		}
		currBatch = append(currBatch, bytesToSend...)
		filesInCurrentBatch += 1
		if filesInCurrentBatch == sizePerBatch {
			fmt.Println("ID: ", idBatch)
			fmt.Println("Length of current batch: ", len(currBatch))
			c.createClientSocket()
			c.socket.Send(currBatch, len(currBatch))
			c.socket.CloseSocket()
			currBatch = bytesBatchIdentifier
			filesInCurrentBatch = 0
		}
	}
	return nil
}

func (c *Client) sendEnd() error{
	bytesToSend := []byte{byte('E')}
	c.createClientSocket()
	log.Infof("\n[CLIENT] Sending END...")
	c.socket.Send(bytesToSend, len(bytesToSend))
	log.Infof("Sent END Succesfully...")
	_, err := c.socket.Receive()
	c.socket.CloseSocket()
	if err != nil {
		return fmt.Errorf("Error sending END: %v", err)
	}
	return nil
}
