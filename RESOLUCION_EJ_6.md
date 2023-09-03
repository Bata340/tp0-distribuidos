# Ejercicio 6
En la resolución de este ejercicio se implementó un mecanismo para procesar archivos de apuestas de forma "batch" o "por chunks".
A continuación se plantean las modificaciones presentes en el código tanto para enviar los archivos en este formato, como así también para recibirlos y almacenarlos dentro del servidor.

## Cliente
En el cliente en principio se implementó el siguiente mecanismo para generar los mensajes batch:

Partiendo del mensaje de apuestas ya existente en el ejercicio 5 (Ver RESOLUCION_EJ5.md para mas detalles, y la rama ejercicio_5 para ver la resolución del mismo), se realiza un empaquetamiento de la siguiente forma:

1) Se añade en el ENV del Dockerfile del cliente un campo de BETS_PER_BATCH que permite definir el número de apuestas que ingresan por cada batch. Por defecto esta cantidad es 20 que estimativamente tiene un tamaño de entre 0,8 y 1 Kb por mensaje (Variable según la longitud de los nombres y los apellidos de los apostadores).
2) Se utiliza el valor BETS_PER_BATCH para empaquetar esa cantidad de apuestas dentro del mensaje batch.
3) Al generar el mensaje batch se reutiliza la función de BetToBytes con ciertas modificaciones:
    * El mensaje de Apuestas no incluye dentro de este la agencia ni el identificador de tipo de mensaje 'B' para apuestas.
    * Previo a los BETS_PER_BATCH mensajes de apuestas se incorporan 2 bytes:
      * Un byte de identificador de mensaje 'B' que identifica al mensaje 'BET' que ahora se procesa siempre de forma batch (Aunque el N sea 1 que sería el mensaje original).
      * Un byte de identificador de agencia en donde irá el ID de la misma para que el servidor pueda identificarla. *(De esta forma se evita ocupar bytes extra en cada mensaje de apuesta generando menor overhead al aumentar el valor de BETS_PER_BATCH)*.
4) Se envía al servidor en principio el tamaño del batch generado vía socket (4 bytes), al igual que sucedía anteriormente con el mensaje de apuestas, y posteriormente se envía el mensaje de batch completo con un send que evita los short writes (Wrapper de clientSocket).
5) Se continúan generando batches mientras el archivo de texto posea líneas hasta finalizar con el mismo.
6) Al finalizar el envío de Batches se envía el mensaje END para denotar que la agencia finalizó con el envío de sus apuestas.


En resumen, el mensaje de Batch se estructura de la siguiente forma:

* Identificador de tipo de mensaje (1 byte)
* Identificador de agencia (1 byte)
* BETS_PER_BATCH mensajes de tipo BET (Bytes variables)

*Aclaración: Cada mensaje que envía el cliente al servidor establece una nueva conexión TCP para permitir que al no existir hilos, ninguno de los clientes sufra de starvation, y todos tengan una determinada responsividad manejada por los mecanismos de I/O del sistema.*

## Servidor
El servidor de la misma forma que en el ejercicio 5 realiza el siguiente procedimiento:

1) Recibe por mensaje el número de bytes correspondientes al mensaje a recibir.
2) Recibe el mensaje Batch o End del cliente.
   * En caso de ser Batch, procede con el paso 3.
   * En caso de ser END, reenvía el mensaje a estilo ECHO para asegurar al servidor que todas las apuestas se persistieron correctamente (No hacía falta dar respuestas a los mensajes Batch puesto que al usar TCP se asegura la correcta transferencia de datos). *(Este paso se modificará en el ejercicio 7 para realizar el comportamiento de obtener los ganadores en la agencia que envía el mensaje END).*
3) Al ser un mensaje batch, el socket leerá la totalidad del batch y posteriormente enviará los bytes al handler de mensajes, y este al traductor de mensajes.
4) El traductor verificará con el byte 'B' que es un batch, y a la agencia con el byte consecuente de ID de agencia. Luego realiza un bucle de las apuestas, y comienza a traducir los mensajes de BET de a 1 por vez (De la misma forma que lo hacía en el ejercicio 5, removiendo el campo de agency_id del mensaje en sí mismo, pero recibiendolo de forma genérica en el mensaje batch).
5) Al traducir todo el batch, la función de traducción retorna un array de Bet que será enviado posteriormente a store_bets para que se persistan las BETS_PER_BATCH apuestas en el servidor.
6) El servidor continuará recibiendo conexiones y manejandolas de forma independiente para cada batch que reciba desde cualquier agencia.