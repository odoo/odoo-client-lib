"""
Odoo Client Library

Home page: http://pypi.python.org/pypi/odoo-client-lib
Code repository: https://github.com/odoo/odoo-client-lib
"""

import sys
if sys.version_info >= (3, 0, 0):
    from xmlrpc.client import ServerProxy
else:
    from xmlrpclib import ServerProxy
import logging
import json
import random

from .tools import _getChildLogger, json_rpc, AuthenticationError, RemoteModel

_logger = logging.getLogger(__name__)


class Connector(object):
    """
    The base abstract class representing a connection to an Odoo Server.
    """

    __logger = _getChildLogger(_logger, 'connector')

    def get_service(self, service_name):
        """
        Returns a Service instance to allow easy manipulation of one of the services offered by the remote server.

        :param service_name: The name of the service.
        """
        return Service(self, service_name)

class XmlRPCConnector(Connector):
    """
    A type of connector that uses the XMLRPC protocol.
    """
    PROTOCOL = 'xmlrpc'
    
    __logger = _getChildLogger(_logger, 'connector.xmlrpc')

    def __init__(self, hostname, port="8069"):
        """
        Initialize by specifying the hostname and the port.
        :param hostname: The hostname of the computer holding the instance of Odoo.
        :param port: The port used by the Odoo instance for XMLRPC (default to 8069).
        """
        self.url = 'http://%s:%d/xmlrpc' % (hostname, port)

    def send(self, service_name, method, *args):
        url = '%s/%s' % (self.url, service_name)
        service = ServerProxy(url)
        return getattr(service, method)(*args)

class XmlRPCSConnector(XmlRPCConnector):
    """
    A type of connector that uses the secured XMLRPC protocol.
    """
    PROTOCOL = 'xmlrpcs'

    __logger = _getChildLogger(_logger, 'connector.xmlrpcs')

    def __init__(self, hostname, port="8069"):
        super(XmlRPCSConnector, self).__init__(hostname, port)
        self.url = 'https://%s:%d/xmlrpc' % (hostname, port)

class JsonRPCConnector(Connector):
    """
    A type of connector that uses the JsonRPC protocol.
    """
    PROTOCOL = 'jsonrpc'
    
    __logger = _getChildLogger(_logger, 'connector.jsonrpc')

    def __init__(self, hostname, port="8069"):
        """
        Initialize by specifying the hostname and the port.
        :param hostname: The hostname of the computer holding the instance of Odoo.
        :param port: The port used by the Odoo instance for JsonRPC (default to 8069).
        """
        self.url = 'http://%s:%d/jsonrpc' % (hostname, port)

    def send(self, service_name, method, *args):
        return json_rpc(self.url, "call", {"service": service_name, "method": method, "args": args})

class JsonRPCSConnector(Connector):
    """
    A type of connector that uses the JsonRPC protocol.
    """
    PROTOCOL = 'jsonrpcs'
    
    __logger = _getChildLogger(_logger, 'connector.jsonrpc')

    def __init__(self, hostname, port="8069"):
        """
        Initialize by specifying the hostname and the port.
        :param hostname: The hostname of the computer holding the instance of Odoo.
        :param port: The port used by the Odoo instance for JsonRPC (default to 8069).
        """
        self.url = 'https://%s:%d/jsonrpc' % (hostname, port)

    def send(self, service_name, method, *args):
        return json_rpc(self.url, "call", {"service": service_name, "method": method, "args": args})

class Service(object):
    """
    A class to execute RPC calls on a specific service of the remote server.
    """
    def __init__(self, connector, service_name):
        """
        :param connector: A valid Connector instance.
        :param service_name: The name of the service on the remote server.
        """
        self.connector = connector
        self.service_name = service_name
        self.__logger = _getChildLogger(_getChildLogger(_logger, 'service'),service_name or "")
        
    def __getattr__(self, method):
        """
        :param method: The name of the method to execute on the service.
        """
        self.__logger.debug('method: %r', method)
        def proxy(*args):
            """
            :param args: A list of values for the method
            """
            self.__logger.debug('args: %r', args)
            result = self.connector.send(self.service_name, method, *args)
            self.__logger.debug('result: %r', result)
            return result
        return proxy

class Connection(object):
    """
    A class to represent a connection with authentication to an Odoo Server.
    It also provides utility methods to interact with the server more easily.
    """
    __logger = _getChildLogger(_logger, 'connection')

    def __init__(self, connector,
                 database=None,
                 login=None,
                 password=None,
                 user_id=None):
        """
        Initialize with login information. The login information is facultative to allow specifying
        it after the initialization of this object.

        :param connector: A valid Connector instance to send messages to the remote server.
        :param database: The name of the database to work on.
        :param login: The login of the user.
        :param password: The password of the user.
        :param user_id: The user id is a number identifying the user. This is only useful if you
        already know it, in most cases you don't need to specify it.
        """
        self.connector = connector

        self.set_login_info(database, login, password, user_id)
        self.user_context = None

    def set_login_info(self, database, login, password, user_id=None):
        """
        Set login information after the initialisation of this object.

        :param connector: A valid Connector instance to send messages to the remote server.
        :param database: The name of the database to work on.
        :param login: The login of the user.
        :param password: The password of the user.
        :param user_id: The user id is a number identifying the user. This is only useful if you
        already know it, in most cases you don't need to specify it.
        """
        self.database, self.login, self.password = database, login, password

        self.user_id = user_id
        
    def check_login(self, force=True):
        """
        Checks that the login information is valid. Throws an AuthenticationError if the
        authentication fails.

        :param force: Force to re-check even if this Connection was already validated previously.
        Default to True.
        """
        if self.user_id and not force:
            return
        
        if not self.database or not self.login or self.password is None:
            raise AuthenticationError("Credentials not provided")

        # TODO use authenticate instead of login
        self.user_id = self.get_service("common").login(self.database, self.login, self.password)
        if not self.user_id:
            raise AuthenticationError("Authentication failure")
        self.__logger.debug("Authenticated with user id %s", self.user_id)
        
    def get_user_context(self):
        """
        Query the default context of the user.
        """
        if not self.user_context:
            self.user_context = self.get_model('res.users').context_get()
        return self.user_context
    
    def get_model(self, model_name):
        """
        Returns a Model instance to allow easy remote manipulation of an Odoo model.

        :param model_name: The name of the model.
        """
        return Model(self, model_name)

    def get_service(self, service_name):
        """
        Returns a Service instance to allow easy manipulation of one of the services offered by the remote server.
        Please note this Connection instance does not need to have valid authentication information since authentication
        is only necessary for the "object" service that handles models.

        :param service_name: The name of the service.
        """
        return self.connector.get_service(service_name)

class Model(RemoteModel):
    def __init__(self, connection, model_name):
        res = super().__init__(connection, model_name)
        self.__logger = _getChildLogger(_getChildLogger(_logger, 'object'), model_name or "")
        return res

    def __getattr__(self, method):
        """
        Provides proxy methods that will forward calls to the model on the remote Odoo server.

        :param method: The method for the linked model (search, read, write, unlink, create, ...)
        """
        def proxy(*args, **kw):
            """
            :param args: A list of values for the method
            """
            self.connection.check_login(False)
            self.__logger.debug(args)
            result = self.connection.get_service('object').execute_kw(
                                                    self.connection.database,
                                                    self.connection.user_id,
                                                    self.connection.password,
                                                    self.model_name,
                                                    method,
                                                    args, kw)
            if method == "read":
                if isinstance(result, list) and len(result) > 0 and "id" in result[0]:
                    index = {}
                    for r in result:
                        index[r['id']] = r
                    if isinstance(args[0], list):
                        result = [index[x] for x in args[0] if x in index]
                    elif args[0] in index:
                        result = index[args[0]]
                    else:
                        result = False
            self.__logger.debug('result: %r', result)
            return result
        return proxy

    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, context=None):
        """
        A shortcut method to combine a search() and a read().

        :param domain: The domain for the search.
        :param fields: The fields to extract (can be None or [] to extract all fields).
        :param offset: The offset for the rows to read.
        :param limit: The maximum number of rows to read.
        :param order: The order to class the rows.
        :param context: The context.
        :return: A list of dictionaries containing all the specified fields.
        """
        record_ids = self.search(domain or [], offset, limit or False, order or False, context=context or {})
        if not record_ids: return []
        records = self.read(record_ids, fields or [], context=context or {})
        return records
