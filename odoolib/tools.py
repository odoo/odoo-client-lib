import httpx
import logging
import random


def _getChildLogger(logger, subname):
    return logging.getLogger(logger.name + "." + subname)

def json_rpc(url, fct_name, params):
    data = {
        "jsonrpc": "2.0",
        "method": fct_name,
        "params": params,
        "id": random.randint(0, 1000000000),
    }
    result_req = httpx.post(url, json=data, headers={
        "Content-Type":"application/json",
    })
    result = result_req.json()
    if result.get("error", None):
        raise JsonRPCException(result["error"])
    return result.get("result", False)


class JsonRPCException(Exception):
    def __init__(self, error):
         self.error = error
    def __str__(self):
         return repr(self.error)


class AuthenticationError(Exception):
    """
    An error thrown when an authentication to an Odoo server failed.
    """
    pass


class RemoteModel(object):
    """
    Useful class to dialog with one of the models provided by an Odoo server.
    An instance of this class depends on a Connection instance with valid authentication information.
    """

    def __init__(self, connection, model_name):
        """
        :param connection: A valid Connection instance with correct authentication information.
        :param model_name: The name of the model.
        """
        self.connection = connection
        self.model_name = model_name
