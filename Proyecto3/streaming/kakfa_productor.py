from kafka import KafkaProducer

class KafkaProductor:
    """
    Clase que representa un productor de Kafka.

    Args:
        bootstrap_servers (List[str]): Lista de servidores Kafka para la conexión.
        topic_name (str, optional): Nombre del tema al que enviar mensajes.

    Attributes:
        _bootstrap_servers (List[str]): Lista de servidores Kafka para la conexión.
        _kafka_producer (KafkaProducer): Instancia del productor Kafka.
        _topic_name (str): Nombre del tema al que enviar mensajes.
    """
    def __init__(
        self,
        bootstrap_servers: list[str],
        topic_name: str = None
    ):
        """
        Inicializa un nuevo objeto KafkaProductor.

        Args:
            bootstrap_servers (List[str]): Lista de servidores Kafka para la conexión.
            topic_name (str, optional): Nombre del tema al que enviar mensajes.
        """
        self._bootstrap_servers = bootstrap_servers
        self._kafka_producer = KafkaProducer(bootstrap_servers=self._bootstrap_servers)
        self._topic_name = topic_name
    
    @property
    def topic_name(self) -> str:
        """
        Obtiene el nombre del topico actual.

        Returns:
            str: Nombre del topico.
        """
        return self._topic_name
    
    @topic_name.setter
    def topic_name(self, new_topic_name: str) -> None:
        """
        Establece el nombre del topico.

        Args:
            new_topic_name (str): Nuevo nombre del topico.
        """
        self._topic_name = new_topic_name

    def send(self, message: str) -> None:
        """
        Envía un mensaje al topico configurado.

        Args:
            message (str): Mensaje a enviar.
        
        Raises:
            ValueError: Si el nombre del topico no está configurado.
        """
        if self._topic_name is None:
            raise ValueError()
        self._kafka_producer.send(
            self._topic_name,
            value=message.encode()
        )
    
    def flush(self):
        """
        Flushea los mensajes pendientes en el productor.
        """
        self._kafka_producer.flush()

if __name__ == "__main__":
    producer = KafkaProductor(topic_name="mi_tema", bootstrap_servers=['34.27.126.27:9092'])
    producer.send("otra prueba mas")
    producer.flush()