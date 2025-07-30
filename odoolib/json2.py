import logging
import httpx

from http import HTTPStatus

from .tools import AuthenticationError, RemoteModel, _getChildLogger

_logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 60


class JsonModel(RemoteModel):
    def __init__(self, connection, model_name):
        res = super().__init__(connection, model_name)
        self.__logger = _getChildLogger(_getChildLogger(_logger, 'object'), model_name or "")
        self.methods = {}
        self.model_methods = []
        return res

    def __getattr__(self, method):
        """
        Provides proxy methods that will forward calls to the model on the remote Odoo server.

        :param method: The method for the linked model (search, read, write, unlink, create, ...)
        """
        def proxy(*args, **kwargs):
            """
            :param args: A list of values for the method
            """
            # self.__logger.debug(args)
            data = kwargs
            if args:
                # Should convert args list into dict of args
                self._introspect()
                offset = 0
                if method not in self.model_methods and 'ids' not in kwargs.keys():
                    data['ids'] = args[0]
                    offset = 1
                for i in range(offset, len(args)):
                    if i-offset < len(self.methods[method]):
                        data[self.methods[method][i-offset]] = args[i]
                    else:
                        _logger.warning(f"Method {method} called with too many arguments: {args}")

            result = httpx.post(
                self._url(method),
                headers=self.connection.bearer_header,
                json=data,
                timeout=DEFAULT_TIMEOUT,
            )

            if result.status_code == HTTPStatus.UNAUTHORIZED:
                raise AuthenticationError("Authentication failed. Please check your API key.")
            if result.status_code == 422:
                raise ValueError(f"Invalid request: {result.text} for data {data}")
            if result.status_code != 200:
                raise ValueError(f"Unexpected status code {result.status_code}: {result.text}")
            return result.json()
        return proxy
    
    def _introspect(self):
        if not self.methods:
            url = f"{self.connection.connector.url.removesuffix('/json/2/')}/doc-bearer/{self.model_name}.json"
            response = httpx.get(url, headers=self.connection.bearer_header)
            response.raise_for_status()
            m = response.json().get('methods', {})
            self.methods = {k: tuple(m[k]['parameters'].keys()) for k in m.keys()}
            self.model_methods = [ k for k in m.keys() if 'model' in m[k].get('api', []) ]

    def read(self, *args, **kwargs):
        res = self.__getattr__('read')(*args, **kwargs)
        if len(res) == 1:
            return res[0]
        return res

    def _url(self, method):
        """
        Returns the URL of the Odoo server.
        """
        return f"{self.connection.connector.url}{self.model_name}/{method}"


class Json2Connector(object):
    def __init__(self, hostname, port="8069"):
        """
        Initialize by specifying the hostname and the port.
        :param hostname: The hostname of the computer holding the instance of Odoo.
        :param port: The port used by the Odoo instance for JsonRPC (default to 8069).
        """
        if port != 80:
            self.url = f'http://{hostname}:{port}/json/2/'
        else:
            self.url = f'http://{hostname}/json/2/'


class Json2SConnector(Json2Connector):
    def __init__(self, hostname, port="443"):
        super().__init__(hostname, port)
        if port != 443:
            self.url = f'https://{hostname}:{port}/json/2/'
        else:
            self.url = f'https://{hostname}/json/2/'


class Json2Connection(object):
    """
    A class representing a connection to an Odoo server.
    """
    
    def __init__(self, connector, database, api_key):
        self.connector = connector
        self.database = database
        self.bearer_header = {"Authorization": f"Bearer {api_key}", 'Content-Type': 'application/json; charset=utf-8', "X-Odoo-Database": database}
        self.user_context = None

    def get_model(self, model_name):
        return JsonModel(self, model_name)
    
    def get_connector(self):
        return self.connector
    
    def get_user_context(self):
        """
        Query the default context of the user.
        """
        if not self.user_context:
            self.user_context = self.get_model('res.users').context_get()
        return self.user_context
