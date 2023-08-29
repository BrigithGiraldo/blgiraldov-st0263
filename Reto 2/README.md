# info de la materia: ST0263 

# Estudiante(s): Brigith Lorena Giraldo Vargas, blgiraldov@eafit.edu.co
#
# Profesor: Edwin Nelson Montoya Munera, eemontoya@eafit.edu.co
#

# Microservicios gRPC y MOM (Reto 2)
#
# 1. breve descripción de la actividad
##Para este reto, se implementaron 2 microservicios:

- **Microservicio 1:** Encargado de listar archivos a través de gRPC. 
- **Microservicio 2:** Encargado de buscar archivos mediante una query a través de MOM (RabbitMQ). 

Ambos se comunican con el API gateway.

- **Microservicio API Gateway:** Encargado de funcionar tanto como gateway como balanceador de cargas y proxy.


## 1.1. Aspectos que se cumplieron o desarrollaron de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales):

**Microservicio 1 (gRPC):**

1. **Implementación del servicio gRPC:** Se ha desarrollado y configurado correctamente el microservicio 1 utilizando el protocolo gRPC, lo que permite la comunicación entre el cliente y el servidor de manera eficiente.

2. **Definición de servicios y mensajes:** Se han definido los servicios y los mensajes necesarios para que el cliente y el servidor puedan comunicarse y realizar las operaciones requeridas.

3. **Despliegue del servidor:** Se ha desplegado el servidor gRPC y está funcionando correctamente al responder a las solicitudes del cliente, por medio de peticiones HTTP.

**Microservicio 2 (MOM):**

1. **Implementación del productor y consumidor:** Se ha desarrollado el productor y el consumidor para el microservicio 2 utilizando RabbitMQ como MOM.

2. **Conexión a RabbitMQ:** Se ha establecido la conexión a RabbitMQ tanto en el productor como en el consumidor.

3. **Definición de colas y mensajes:** Se han definido las colas y los mensajes necesarios para que el productor envíe solicitudes y el consumidor las procese.

## 1.2. Que aspectos NO cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)

**Aspectos no cumplidos o con problemas:**

1. **Ejecución incorrecta del microservicio 2:** Aunque se ha desarrollado tanto el productor como el consumidor para el microservicio 2, se están experimentando problemas en la ejecución, ya que no se están enviando ni procesando correctamente las solicitudes. Es posible que esto se deba a problemas en la configuración de RabbitMQ, en el enrutamiento de mensajes o en la lógica de manejo de mensajes en el consumidor, los cuales no se pudieron resolver a tiempo.

En resumen, se ha logrado desarrollar y ejecutar correctamente el microservicio 1 utilizando gRPC, pero se ha experimentado problemas en el microservicio 2 con la implementación y ejecución de RabbitMQ. Es importante aclarar que el uso de RabbitMQ se dificultó mucho más debido al poco conocimiento previo que se tenía acerca de este software de negociación de mensajes.

# 2. información general de diseño de alto nivel, arquitectura, patrones, mejores prácticas utilizadas.

1. El sistema incluye un componente llamado API Gateway.
2. Uno de los microservicios implementados se conoce como Microservicio 1 (gRPC).
3. La comunicación entre los distintos componentes se logra a través de un sistema de mensajería orientado a mensajes (MOM) conocido como RabbitMQ.
4. Otro componente, designado como Microservicio 2, también emplea la comunicación a través de RabbitMQ como parte del sistema MOM.

Cuando un usuario realiza una solicitud, ya sea mediante su navegador web o la herramienta Postman, esta solicitud se transmite a través de una interfaz de programación de aplicaciones (API) utilizando el protocolo REST. Luego, el API Gateway, como intermediario, establece una comunicación mediante el protocolo gRPC con el primer microservicio. Este microservicio, a su vez, tiene la función de listar los archivos.

Por otro lado, el segundo microservicio utiliza el sistema de mensajería RabbitMQ como método de comunicación. Se basa en el uso de colas para procesar solicitudes de búsqueda de archivos que los usuarios pasan a través de una consulta. El sistema determina qué tipo de comunicación se requiere según el tipo de solicitud realizada.

El desarrollo del sistema se llevó a cabo utilizando el lenguaje de programación Python, y para la gestión de los componentes se empleó Docker como herramienta de orquestación. Además, se siguen prácticas recomendadas, como la utilización de variables de entorno, la implementación de métodos desacoplados y la organización de los directorios de manera efectiva.

# 3. Descripción del ambiente de desarrollo y técnico: lenguaje de programación, librerias, paquetes, etc, con sus numeros de versiones.

Todo el proyecto fue implementado con Python 3.11.4

**librerías utilizadas:**

1. Flask:
   Es un marco de desarrollo web ligero y flexible para Python. Permite crear aplicaciones web de manera rápida y sencilla, proporcionando herramientas esenciales para el enrutamiento de URLs, gestión de plantillas y manejo de solicitudes y respuestas HTTP.

2. grpc:
   Es una plataforma de comunicación remota de alto rendimiento desarrollada por Google. Permite definir y crear servicios de forma eficiente utilizando un protocolo de serialización binaria para intercambiar datos entre diferentes aplicaciones.

3. grpcio:
   Es la biblioteca de Python para gRPC. Proporciona la implementación de gRPC en Python, permitiendo la creación y el consumo de servicios gRPC en aplicaciones Python.

4. pika:
   Es una biblioteca para interactuar con RabbitMQ, un sistema de mensajería de código abierto. Pika facilita la comunicación entre aplicaciones y colas de mensajes, lo que es útil para la implementación de patrones de mensajería como el sistema de mensajería orientado a mensajes (MOM).

5. protobuf:
   También llamado protobuf, es un formato de serialización de datos desarrollado por Google. Proporciona una forma eficiente y compacta de serializar estructuras de datos para su intercambio entre aplicaciones en diferentes lenguajes de programación.

6. python-dotenv:
   Es una biblioteca que permite cargar variables de entorno desde archivos de configuración (.env) en proyectos de Python. Esto facilita la gestión de configuraciones sensibles, como contraseñas y claves de API, sin exponerlas directamente en el código fuente.


## como se compila y ejecuta.

1. Se debe clonar el repositorio:

    git clone https://github.com/BrigithGiraldo/blgiraldov-st0263.git

2. Después se debe ejecutar y correr el servidor, estando en la carpeta .../S1_gRPC/src/: 

    python server.py

3. Luego se debe correr el API, estando en la carpeta .../API/src/:

    python app.py

4. Por último se accede a la dirección http://127.0.0.1:5000/archivos

Así el cliente puede observar la lista de archivos.

5. Cabe resaltar que no se pondrán las instrucciones de uso de la dirección http://127.0.0.1:5000/buscar-archivos, ya que esta no funciona correctamente.
## detalles del desarrollo.

En una primera etapa, se puso en marcha el primer microservicio que habilita la consulta de archivos mediante la utilización de gRPC para la comunicación. Después de lograr el funcionamiento efectivo de este microservicio, se avanzó a la integración de Flask como API Gateway. En la fase final, se implementó el segundo microservicio, que permite la búsqueda de archivos a través de una consulta específica y se conecta mediante el uso de MOM, en particular con RabbitMQ, el cual como se menciona anteriormente presenta conflictos de conexión.

- El proyecto se construyó utilizando el lenguaje de programación Python.

# 4. Descripción del ambiente de EJECUCIÓN (en producción) lenguaje de programación, librerias, paquetes, etc, con sus numeros de versiones.

Cada microservicio cuenta con su archivo .env

- API:
    HOST_GRPC=localhost
    PORT_GRPC=50051
    HOST_RMQ=localhost
    PORT_RMQ=5672
    USER=guest
    PASSWORD=guest
    QUEUE="archivo_rpc"

- S1_gRPC:
    PORT_GRPC=50051

- S2_MOM:
    HOST_RMQ=localhost
    PORT_RMQ=5672
    USER=guest
    PASSWORD=guest
    QUEUE="archivo_rpc"

## una mini guia de como un usuario utilizaría el software o la aplicación

Este proyecto se ejecuta por consola, y para probar las peticiones se hacen a traves del navegador o postman.

# referencias:
- https://pypi.org/project/python-dotenv/ 
- https://geekflare.com/es/rabbitmq-explained/
- https://www.ionos.es/digitalguide/paginas-web/desarrollo-web/flask/
- https://www.paradigmadigital.com/dev/grpc-que-es-como-funciona/

#### versión README.md -> 1.0 (2023-agosto)