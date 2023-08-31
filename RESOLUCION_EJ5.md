# Ejercicio 5

Para la resolución del presente ejercicio se hizo en principio una refactorización, quedando separado el código como se explicará a lo largo del presente documento.

## Servidor
En el caso del servidor tenemos los siguientes archivos:

* **bets_handler.py:** Es el encargado de tomar un mensaje, y realizar un handle sobre el mismo. Previo a el manejo del mismo, llama a la función de traducir mensaje del message_traducer para pasar ese mensaje de bytes a algo legible por el programa. Esa traducción le permite denotar el tipo de mensaje, y a partir de un diccionario, referenciar a una función de handle específica de ese tipo de mensaje. Por ejemplo: Si recibo un mensaje de END, este handler llamaría a la función __handleEnd, y viceversa si recibe un BetMessage.
A su vez, es en este documento también donde se realiza la persistencia de las apuestas al administrar un mensaje de apuestas, utilizando las funciones del archivo utils.py.

* **message_traducer.py:** En este archivo encontraremos la traducción de los bytes del mensaje recibido, a un objeto de python que sea intepretable por el resto del código. Para ello, es importante comprender el protocolo de comunicación utilizado que se nombra más adelante en su sección correspondiente.

* **server_socket.py:** Es el archivo encargado de manejar la capa de comunicación de sockets, con métodos para aceptar una conexión, leer un determinado mensaje de una longitud dada evitando short reads, y para escriturar un mensaje de bytes evitando short writes.

* **server.py:** Es considerado como el "main" del servidor. Es quien unifica al resto de componentes, ya que: 
    * Instancia su propio server socket, manejando los llamados a las funciones del mismo.
    * Realiza llamados a bets_handler para administrar los mensajes recibidos a partir del socket.

<br>

* **utils.py:** Provisto por la cátedra, permite persistir apuestas, recuperar apuestas, y brinda una función de comparación de número apostado para determinar si dicho número fue o no ganador de las apuestas.

## Cliente

De forma similar, el cliente también posee separada las capas de traducción de mensajes, socket, y dominio. Esto puede verse reflejado en los siguientes archivos:

* **client.go:** En este archivo encontraremos la toma de datos a partir de variables de entorno para la apuesta, y la manipulación sobre el socket que provee clientSocket.go. De esta forma, en este archivo encontramos la capa de dominio que se encarga de inicializar el socket de clientSocket, ordenarle que envíe una determinada apuesta, y posteriormente esperar por la respuesta de la misma, y enviar un fin de la casa de apuestas para que se registre en el servidor que dicha casa terminó de apostar.

* **clientSocket.go:** En este archivo encontramos la capa de red, donde se utilizan los sockets TCP, brindando primitivas de:
    * Generación de nuevo socket
    * Lectura de bytes que evita short reads con una longitud específica recibida también vía socket.
    * Escritura de bytes que evita short writes para la longitud determinada de los bytes recibidos.

<br>

* **messageFormater.go:** En este archivo encontramos la traducción de una apuesta a bytes cumpliendo con nuestro protocolo específico de comunicación para el presente problema.

## Protocolo de Comunicación

El protocolo de comunicación establecido es simple, y será explicado por pasos:

Al instanciarse una conexión de socket TCP entre cliente y servidor, sucederá lo siguiente:
1) El servidor aceptará la conexión entrante y administrará al socket del cliente.
2) El servidor queda a la escucha de un mensaje del cliente.
3) El cliente al haber recibido una aceptación de la conexión prepara un mensaje de apuesta específico.
4) Al poseer el mensaje de la apuesta, cuenta la cantidad de bytes que posee dicho mensaje y lo envía como un 1er mensaje de longitud (De tamaño 4 bytes. Será un int.).
5) Luego de enviada la longitud del mensaje, el cliente procede a enviar la totalidad de los bytes de la apuesta, y se quedará esperando por un Echo message igual al que este envió (Será la confirmación de la recepción del mensaje para realizar el logging pedido por consigna).
6) Del lado del servidor se recibirá primero la longitud en forma de bytes, se desempaquetará (Siempre en formato BigEndian), y luego se procede a la lectura de los bytes de la apuesta.
7) Una vez recibida la apuesta, se la desempaqueta, se la persiste con la función store_bets, y luego se envía el "Echo Message".
8) El cliente al recibir el "Echo Message", cierra el socket, y loggea que la apuesta fue correctamente persistida. 
9) Al finalizar las apuestas, el cliente crea una nueva instancia que será aceptada por el servidor, para enviar un mensaje de END que será un único byte correspondiente al caracter 'E'.
10) El servidor recibirá el mensaje de END y sumará 1 a las agencias finalizadas en el bets_handler, para facilitar posteriormente la resolución del ejercicio 7.
11) El servidor envía el "Echo Message" para el END.
12) El cliente reconoce el Echo Message del menssaje de END, y finaliza su ejecución correctamente. (En el ejercicio 7 se agregará un mensaje extra para solicitar los ganadores de las apuestas).

Los mensajes se componen de la siguiente forma:

* **MENSAJE END:** Un único byte 'E' que permite identificar el tipo de mensaje como "END"

* **MENSAJE BET:** Se compone de la siguiente forma:
    * **Byte del caracter 'B'**, que representa el tipo de mensaje como 'B'etMessage. (1 byte)
    * **Id de la agencia**: Caracter con el id de la agencia (1 Byte). Es un char que es mas chico que un int por el hecho de que solo usaremos hasta 5 agencias. En caso de ser más agencias convendría que sea un short como mínimo.
    * **Longitud del nombre del apostador** [N] (4 bytes - int)
    * **Nombre del apostador** (N bytes - determinado por la longitud anterior).
    * **Longitud del apellido del apostador** [M] (4 bytes - int)
    * **Apellido del apostador** (M bytes - determiando por la long. del apellido).
    * **Documento del apostador** (4 bytes - int)
    * **Fecha de nacimiento** (10 bytes - string - formato "YYYY-MM-DD")
    * **Número Apostado** (4 bytes - int)

    <br>
    Finalmente, el mensaje de apuestas toma una longitud total de (1+1+4+N+4+M+4+10+4) Bytes. Es decir, calculado: (28+M+N) bytes por apuesta (Dependiente de las longitudes de los nombres y apellidos de los apostadores).
    
    <br>

    ***ACLARACIÓN:** TODOS LOS ENTEROS SON MANEJADOS EN FORMATO BIG ENDIAN*