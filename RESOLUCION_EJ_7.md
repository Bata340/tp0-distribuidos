# Ejercicio 7
Para el ejercicio 7 se modificó levemente el protocolo del ejercicio 6 (Ver RESOLUCION_EJ_6.md para explicación, y rama ejercicio_6 para código fuente), modificando el mensaje END y su lógica de dominio para su manejo.

Se verán diferenciadas las soluciones tanto para cliente como para servidor en las siguientes secciones:

## Cliente

A nivel cliente se realizaron los siguiente cambios:

* En la función sendEnd de client.go: 
    * Ya no solo envía un byte 'E' y luego recibe un Echo del servidor, sino que envía byte'E'byte'{AGENCY_ID}', especificando que dicha agencia finalizó su tanda de apuestas, y está a la espera de los ganadores del sorteo.
    * Al enviar dicho mensaje, recibe una respuesta que podrá ser byte'P' o byte'W'bytes'{DNIS_GANADORES_EN_ARRAY}'. Entonces si el byte es P, significa que está pendiente el sorteo, y realizará un sleep con exponential backoff (Tiempos: 1, 2, 4, 8, ...) realizando una petición en cada despertar hasta recibir el mensaje cuyo byte inicial es una 'W'.
    * Si la respuesta recibida inicia con 'W', entonces se desempaquetan el resto de bytes de 4 en 4, correspondiendo cada int de estos al DNI de un ganador (Si no hay bytes restantes, no existen ganadores en dicha agencia.).
    * Finalmente se loggean los ganadores, y el mensaje de la cantidad de ganadores especificado en la consigna para dicha agencia.

* Se implementó la función TraduceWinners para desempaquetar los bytes de los ganadores en un array de DNI's ganadores (En messageFormater.go).

## Servidor

A nivel servidor se implementó lo siguiente:

* Una función __get_winners que a partir de la funcion load_bets de la cátedra, la itera y utiliza la función has_won en conjunto con una comparación del id de agencia de la apuesta, y el recibido en la función get_winners para ver si es una apuesta realizada en dicha agencia. Eso se ve reflejado en este código:

```py
for bet in load_bets():
    if has_won(bet) and int(bet.agency) == int(agency_id):
        winners += winner_to_bytes(bet.document)
    return winners
```

En caso de que get_winners denote que no finalizaron aún todas las agencias, no leerá el archivo, y en su lugar retorna un mensaje de tipo Pending que es simplemente un Byte'P'.

* Al recibir un mensaje END desde un socket cliente, el servidor revisa el id de la agencia. En caso de no haber recibido un end de dicha agencia, la añade a un array de agencias finalizadas, y aumenta la cantidad de agencias finalizadas en 1. Si la agencia ya había sido recibida, entonces únicamente le devuelve el mensaje de ganadores (Byte'P' si aún quedan agencias por finalizar, y Byte'W'Bytes'{DNI_GANADORES}' si todas las 5 agencias finalizaron). Para generar el mensaje de ganadores se llama a __get_winners. En código se ve como:
```py
def __handleEnd(self, agency_id):
    if not (agency_id in self.agenciesIdEnded):
        self.agenciesEnded += 1
        self.agenciesIdEnded.append(agency_id)
        if self.agenciesEnded == NUM_AGENCIES:
            logging.info("action: sorteo | result: success")
    return self.__get_winners(agency_id)
```

A este punto, ya no existe comportamiento como "Echo Server" ante ningún mensaje proveniente del cliente, sino que directamente el servidor pasa a ser un manejador de apuestas en formato Batch, y posteriormente, en sorteador e informador de ganadores de las apuestas.

