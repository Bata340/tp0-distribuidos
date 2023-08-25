package common

import (
	"fmt"
	"net"
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
		fmt.Printf("%v", err)
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
	for accum_sent < length_of_message {
		size_sent, send_err := socket.conn.Write(bytes_to_send)
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
			return buffer, fmt.Errorf("%v", err)
		}
		accum += size
	}
	return buffer, nil
} 


func (socket *ClientSocket) CloseSocket() {
	socket.conn.Close()
}