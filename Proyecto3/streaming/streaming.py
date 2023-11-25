from kakfa_productor import KafkaProductor

from websocket import WebSocketApp

class TradesStreaming:
    """
    Clase para realizar transmisiones de datos de operaciones.

    Attributes:
        _api_key (str): Clave de API para autenticación.
        _tycker_symbols (set): Conjunto de símbolos de ticker para los cuales realizar transmisiones.
        _url (str): URL de la conexión WebSocket.
        _web_socket (WebSocketApp): Objeto de conexión WebSocket.
    """
    def __init__(
        self,
        api_key: str,
        tycker_symbols: list[str],
        kafka_productor: KafkaProductor = None
    ):
        """
        Inicia una nueva instancia de TradesStreaming.

        Args:
            api_key (str): Clave de API para la autenticación.
            tycker_symbols (list[str]): Lista de símbolos de tycker.
            kafka_productor (KafkaProductor, optional): Instancia de KafkaProductor para la producción de mensajes Kafka.
        """
        self._api_key = api_key
        self._tycker_symbols = set(tycker_symbols)
        self._url = f'wss://ws.finnhub.io?token={self._api_key} '  
        self._web_socket = WebSocketApp(
            self._url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self._kafka_productor = kafka_productor
    
    @property
    def api_key(self) -> None:
        """
        Getter para la clave de API.
        """
        pass
    
    
    @api_key.setter
    def api_key(
        self,
        new_api_key: str
    ) -> None:
        """
        Setter para actualizar la clave de API.
        """
        self._api_key = new_api_key
        
    @property
    def url(self) -> str:
        """
        Getter para la URL de conexión.
        """
        return self._url
    
    @url.setter
    def url(self, new_url: str) -> None:
        """
        Setter para actualizar la URL de conexión.
        """
        self._url = new_url
    
    def on_open(self, web_socket: WebSocketApp) -> None:
        """
        Callback llamado cuando se abre la conexión WebSocket.

        Parameters:
            web_socket (WebSocketApp): Objeto WebSocket que representa la conexión abierta.

        Returns:
            None

        Description:
            Este método se utiliza como un callback que se llama automáticamente cuando se abre
            la conexión WebSocket. Envía solicitudes de suscripción para los símbolos de ticker
            proporcionados en `_tycker_symbols`.
        """
        for tycker_symbol in self._tycker_symbols:
            web_socket.send(f'{{"type":"subscribe","symbol":"{tycker_symbol}"}}')
    
    def on_message(self, _: WebSocketApp, message: str) -> None:
        """
        Maneja los mensajes recibidos a través del WebSocket.

        Args:
            _: WebSocketApp: Objeto WebSocketApp (ignorado en la implementación actual).
            message (str): Mensaje recibido.

        Returns:
            None
        """
        if message and self._kafka_productor:
            self._kafka_productor.send(message=message)
            self._kafka_productor.flush()
        print(message)       
        
    def on_error(self, _: WebSocketApp, error) -> None:
        """
        Maneja los errores ocurridos en el WebSocket.

        Args:
            _: WebSocketApp: Objeto WebSocketApp (ignorado en la implementación actual).
            error: Objeto que representa el error.

        Returns:
            None
        """
        print(error)
    
    def on_close(
        self,
        _: WebSocketApp,
        close_status: int,
        message: str
    ) -> None:
        """
        Maneja el cierre del WebSocket.

        Args:
            _: WebSocketApp: Objeto WebSocketApp (ignorado en la implementación actual).
            close_status (int): Código de estado del cierre.
            message (str): Mensaje de cierre.

        Returns:
            None
        """
        print(message)
    
    def execute(self):
        """
        Configura el WebSocket y ejecuta la aplicación.

        Returns:
            None
        """
        self._web_socket.on_open = self.on_open
        self._web_socket.run_forever()


if __name__ == "__main__":
    productor = KafkaProductor(topic_name="raw_data", bootstrap_servers=['104.197.171.58:9092'])
    TradesStreaming("clegilhr01qnc24e2e50clegilhr01qnc24e2e5g", ["BINANCE:BTCUSDT"], productor).execute()
    