# Ejercicio 1
Puede visualizarse en docker-compose-dev.yaml con las siguientes lineas agregadas:

```
client2:
    container_name: client2
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID=2
      - CLI_LOG_LEVEL=DEBUG
    networks:
      - testing_net
    depends_on:
      - server
    volumes:
      - ./client/config:/build/config:ro
```

## Ejercicio 1.1
Para el ejercicio 1.1 existe el script create_docker_compose_template.py que puede correrse instalando Jinja2 con el comando:

`
pip install Jinja2
`

Y ejecutandolo con python:

`
python ./create_docker_compose_template.py
`

Esto dará como resultado un nuevo "docker-compose-dev.yaml" con la cantidad de clientes especificados por línea de comandos al ejecutar el script de python.

Luego pueden generarse los contenedores con el mismo comando del makefile de:

`
make docker-compose-up
`


# Ejercicio 2

Para realizar esto se utilizaron los volúmenes de Docker, y se reestructuraron los archivos de configuración a su propia carpeta config tanto en **client** como en **server**.

Para la config del cliente se agregaron las siguientes lineas al docker compose del cliente en cuestión:

```
volumes:
      - ./client/config:/build/config:ro
```

Y para el servidor las siguientes:
```
volumes:
      - ./server/config:/config:ro
```

Vinculando de esta forma la carpeta como volumen montado dentro del contenedor en formato Readonly.

# Ejercicio 3

Para el test de netcat se creó un nuevo comando en el Makefile:

```Makefile
docker-compose-netcat-test:
	docker build ./netcat-test -t "netcat-test:latest"
	docker-compose -f docker-compose-dev.yaml run --rm netcat-test -d --build
.PHONY: docker-compose-server-test
```

Que básicamente lo que hace es:
* Crear un nuevo contenedor "netcat-test:latest" con el Dockerfile existente dentro de la carpeta ./netcat-test (Permite configurar el mensaje de test, el puerto del servidor, y el nombre del contenedor del servidor a partir de variables de entorno):
```Dockerfile
FROM subfuzion/netcat
COPY ./netcat.sh /netcat.sh
ENV NETCAT_MESSAGE="TEST_MESSAGE"
ENV SVR_CONTAINER_NAME="server"
ENV PORT=12345
ENTRYPOINT ["/bin/sh"]
```
* Correr el docker compose agregando el contenedor de netcat-test específicamente que solo corre en caso de que exista el profile "test".
* Se corre con el flag --rm para remover el contenedor una vez finalizada su ejecución.
* La imagen es reutilizable debido al orden de ejecución de los comandos, ya que al no existir modificaciones durante su ejecución, reutilizará siempre la misma imagen.

# Ejercicio 4
En este caso se modificaron tanto el cliente como el servidor para garantizar el correcto handle de la señal SIGTERM.

## Cliente
Para el cliente en Go se utilizó una GoRoutine que escucha por las señales, y en específico la de SIGTERM, y la maneja para finalizar con todos los recursos (Sockets y canales de escucha):

(Lineas 123 a 130 - main.go):
```Go
//Before starting client, handle sigterm with channel & signal notify
signals := make(chan os.Signal, 1)
signal.Notify(signals, os.Interrupt, syscall.SIGTERM)
//Make a goroutine to handle the signal of SIGTERM
go endOnSigTerm(client, signals)

client.StartClientLoop()
close(signals)
```
(Lineas 92 a 99 - main.go):
```Go
func endOnSigTerm (client *common.Client, signals chan os.Signal) {
	//Read from channel, won't execute except SIGTERM is thrown.
	<-signals
	fmt.Println("\nReceived SIGTERM. shutting down client...")
	client.End()
	fmt.Println("\nEnding Main Instance... Graceful exit")
	close(signals)
}
```
(Lineas 102 a 106 - client.go):
```Go
func (c *Client) End() {
	fmt.Println("\n[CLIENT] Shutting down Socket...")
	c.conn.Close()
	fmt.Println("\n[CLIENT] Socket closed, ending instance...")
}
```

## Servidor
En el caso del servidor, de forma similar se utiliza el import signal de python para poder manejar las señales con callbacks. Además, se agrega un booleano al server para determinar cuando debe dejar de aceptar conexiones por haber recibido la señal SIGTERM.

En este caso tenemos en la línea 55 (main.py):
```py
#On SIGTERM triggers the end server function that destructs all socket connections and shut downs gracefully.
signal.signal(signal.SIGTERM, lambda _signum, _frame: server.end_server())
```
En las líneas 24 a 28 de server.py:
```py
# TODO: Modify this program to handle signal to graceful shutdown
# the server
while not self.should_end_loop:
    client_sock = self.__accept_new_connection()
    if not client_sock:
        break
    self.__handle_client_connection(client_sock)
```

En las lineas 64 a 71 de server.py:
```py
def end_server(self):
    logging.info("[SERVER] Shutting down")
    self.should_end_loop = True
    # Close connection and send EOF to peers
    self._server_socket.shutdown(socket.SHUT_RDWR)
    # Deallocates socket
    self._server_socket.close()
    logging.info("[SERVER] Shutted Down Gracefully")
```