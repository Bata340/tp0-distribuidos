# Ejercicio 8

Para el ejercicio 8 se implementó el manejo de las conexiones entrantes con multiprocesamiento. Para ello se utilizó la librería multiprocessing de Python y veremos la explicación en las siguientes secciones:

## Multiprocessing

Como se dijo inicialmente, el desarrollo de la solución del ejercicio 8 se hizo con multiprocesamiento con la biblioteca multiprocessing de Python. En particular se reestructuro el handle de mensajes del bet_handler para que en caso de recibir un END no almacene dentro de su estado interno, sino que envia un mensaje a partir de una cola a server.py, y este se encargará de administrar las agencias finalizadas (En resumen, se modifica el lugar donde esta responsabilidad yace).

Para ello entonces se instancia un proceso por por cada conexión entrante:
```py
return_value = mp.Queue()
process = mp.Process(target = self.__handle_client_connection, args=(client_sock,return_value,))
process.start()
```

Y luego se encola hacia otro hilo del server.py el proceso para joinearlo sin bloquear el aceptado de conexiones:
```py
self.process_queue.put([process, return_value])
```

Esta cola de procesos se utiliza en el hilo "Joiner" que se explica mas adelante en la sección de sincronización.

Cada proceso entonces recibe el mensaje del socket en específico, y lo handlea de la misma forma que se hacía en el ejercicio 7. El único comportamiento modificado como ya se mencionó es en el mensaje end, y por otra parte, el uso de la Queue "return_value" para ambos mensaje(Se ve en detalle en "Notificación de agencia finalizada" en la sección de Sincronización).

*ACLARACIÓN: Reconozco que la presente implementación a gran escala puede tener problemas de memoria, ya que spawnear procesos por cada petición tomaría una gran utilización de recursos. Para ello se requeriría readaptar la apertura de una única conexión TCP cliente-servidor para realizar toda la comunicación manejada en un único proceso independiente para cada cliente. Sin embargo, dado que ya fue resuelto con un proceso por cada request de cada cliente, y que carezco de tiempo, lo dejaré implementado de dicha manera.*

## Sincronización

Para la sincronización se desarrolló un mecanismo basado en colas, donde la comunicación surge de la siguiente forma:

* Una cola encargada de enviar los procesos pendientes a un Thread para que pueda leerlos y joinearlos a medida que vayan finalizando el handle de cada uno de los mensajes que vienen vía socket.
* Una cola por cada proceso generado en donde se ingresa un valor de retorno del proceso (Este valor de retorno es None en caso de que ninguna agencia haya finalizado, y sino, el id de la agencia en caso de que el mensaje recibido sea de tipo END). Ese valor de retorno es manejado por el hilo "Joiner" al joinear un proceso específico, tomando de la cola de dicho proceso el valor que este haya establecido con el método put.

En detalle podemos verlo en las siguientes subsecciones:

### Notificación de agencia finalizada

Cuando un proceso en su handler de mensajes identifica que recibió un mensaje de tipo "END" (Es decir, que una agencia finalizó con la subida de todas sus apuestas), se encargará de encolar en la cola que le fue asignada al momento de instanciar el proceso el valor del id de dicha agencia. De esta forma, cuando el hilo "Joiner" joinee el proceso, leerá la cola de retorno, y si el valor no es None, entonces almacenará la agencia en el estado interno del servidor en caso de que no haya sido almacenada aún.

De esta forma, se independiza totalmente el procesamiento de cada uno de los procesos, manejando el resto de lógica a partir del retorno con la comunicación de dicha cola.

### Join de procesos sin bloquear el accept

Es en esta subsección donde explicamos el comportamiento del hilo "Joiner". Este hilo se instancia en el __init__ del server.py:
```py
self.joiner = Thread(target=self.join_processes)
```
Y se ejecuta en el run:
```py
self.joiner.start()
```
Luego al finalizar el server su bucle de ejecución, se encargará de señalizar el fin para el hilo Joiner, y luego joineará el hilo:
```py
self.process_queue.put((None, None))
self.joiner.join()
```

En caso de recibir un SIGTERM también se encolará un mensaje para la finalización del Joiner:
```py
def end_server(self):
    logging.info("[SERVER] Shutting down")
    self.serverSocket.shutdown()
    self.should_end_loop = True
    self.process_queue.put([None, None]) # <-- Mensaje de fin del Joiner. Luego se joinea en el run que finaliza su ejecución.
    logging.info("[SERVER] Shutted Down Gracefully")
```

La cola utilizada para este hilo no es la perteneciente a multiprocessing, sino que es la propia de Python.

Y finalmente el comportamiento del hilo "Joiner" es tan sencillo como la siguiente función:

```py
def join_processes(self):
    while True:
        child = self.process_queue.get()
        process = child[0]
        queue = child[1]
        if process == None: # <-- Denotar que finaliza cuando el process es None, y esto solo pasa en un mensaje de fin para el hilo.
            return
        process.join()
        queue_msg = queue.get()
        queue.close()
        if queue_msg != None:
            self.add_agency_id(queue_msg)
```

La finalidad del presente hilo es de evitar el bloqueo del hilo principal para que pueda seguir aceptando conexiones e instanciando procesos para que el servidor efectivamente pueda manejar de a más de a un cliente a la vez. Por el contrario, si el join se realizara en el mismo hilo, estaríamos bloqueando el bucle hasta la finalización de la conexión entrante, y luego recién podríamos aceptar otra conexión.

En resumen, nos permite el siguiente comportamiento sin bloqueos adicionales dentro del hilo principal de server.py:

```py
while not self.should_end_loop:
            client_sock = self.serverSocket.accept_client()
            if not client_sock:
                break
            return_value = mp.Queue()
            process = mp.Process(target = self.__handle_client_connection, args=(client_sock,return_value,))
            process.start()
            self.process_queue.put([process, return_value])
```

### File Locks

El ultimo mecanismo de sincronización requerido es para acceder a los archivos, tanto para lectura como para escritura, ya que sino podemos encontrarnos con datos inconsistentes en los mismos. Para ello, se incorporó un lock al bets_handler.py:
```py
def __init__(self):
    self.fileLock = Lock() #<-- Incorporación del lock
```

Y luego se utilizan tanto en la escritura como en la lectura de archivos:

```py
def __get_winners(self, agency_id, agencies_ended):
    if len(agencies_ended) < NUM_AGENCIES:
        return b"P"
    winners = b"W"
    self.fileLock.acquire() # <-- ACQUIRE DEL LOCK
    for bet in load_bets(): # <-- LECTURA DEL ARCHIVO
        if has_won(bet) and int(bet.agency) == int(agency_id):
            winners += winner_to_bytes(bet.document)
    self.fileLock.release() # <-- RELEASE DEL LOCK
    return winners


def __handleBatch(self, batch):
    self.fileLock.acquire() # <-- ACQUIRE DEL LOCK
    store_bets(batch) # <-- ESCRITURA EN ARCHIVO
    self.fileLock.release() # <-- RELEASE DEL LOCK
    for bet in batch:
        logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')
    return None
```