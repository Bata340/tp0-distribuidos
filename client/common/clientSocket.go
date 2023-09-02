package common

import (
	"fmt"
	"net"
	"encoding/binary"
	log "github.com/sirupsen/logrus"
)

type ClientSocket struct {
	sockConf ClientConfig
	conn net.Conn
}

func NewClientSocket(config ClientConfig) *ClientSocket {
	socket := &ClientSocket{
		sockConf: config,
	}
	err := socket.initConnection()
	if err != nil{
		log.Fatalf("action: creating socket | result: fail | error: %v", err)
	}
	return socket
}


func (socket *ClientSocket) initConnection() error {
	conn, err := net.Dial("tcp", socket.sockConf.ServerAddress)
	if err != nil {
		log.Fatalf(
	        "action: connect | result: fail | client_id: %v | error: %v",
			socket.sockConf.ID,
			err,
		)
		return fmt.Errorf("Error initializing socket conn: %v", err)
	}
	socket.conn = conn
	return nil
}


func (socket *ClientSocket) Send(bytes_to_send []byte, length_of_message int) error {
	// Sends specific length of bytes from socket.
	// And avoids short writes.
	accum_sent := 0
	sizeOfMessage := make([]byte, 4)
	binary.BigEndian.PutUint32(sizeOfMessage, uint32(len(bytes_to_send)))
	for accum_sent < 4 {
		size_sent, send_err := socket.conn.Write(sizeOfMessage[accum_sent:])
		if send_err != nil {
			return fmt.Errorf("%v", send_err)
		}
		accum_sent += size_sent
	}
	accum_sent = 0
	for accum_sent < length_of_message {
		size_sent, send_err := socket.conn.Write(bytes_to_send[accum_sent:])
		if send_err != nil {
			return fmt.Errorf("%v", send_err)
		}
		accum_sent += size_sent
	}
	return nil
}


func (socket *ClientSocket) Receive(length int) ([]byte, error) {
	// Receives specific length of bytes from socket.
	// And avoids short reads.
	accum := 0
	buffer := make([]byte, length)
	for accum < length {
		size, err := socket.conn.Read(buffer[accum:])
		if err != nil{
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
				socket.sockConf.ID,
				err,
			)
			return buffer, fmt.Errorf("Error: %v", err)
		}
		accum += size
	}
	log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
		socket.sockConf.ID,
		buffer,
	)
	return buffer, nil
} 


func (socket *ClientSocket) CloseSocket() {
	log.Infof("[SOCKET] Closing...")
	socket.conn.Close()
	log.Infof("[SOCKET] Closed Correctly.")
}