
Odoo Client Library
======================


The Odoo Client Library is a Python3 library to communicate with an Odoo Server using its web
services in an user-friendly way. It was created for those that doesn't want to code XML-RPC calls
on the bare metal. It handles XML-RPC as well as JSON-RPC protocol and provides a bunch of syntaxic
sugar to make things a lot easier.

Guide
-----

First install the library: ::

    pip install odoo-client-lib

Now copy-paste the following script describing a simple interaction with an Odoo server: ::

    import odoolib

    connection = odoolib.get_connection(hostname="localhost", database="my_db", \
        login="my_user", password="xxx")
    user_model = connection.get_model("res.users")
    ids = user_model.search([("login", "=", "admin")])
    user_info = user_model.read(ids[0], ["name"])
    print user_info["name"]
    # will print "Administrator"

In the previous script, the get_connection() method creates a Connection object that represents a
communication channel with authentification to an Odoo server. By default, get_connection() uses
XML-RPC, but you can specify it to use JSON-RPC. You can also change the port. Example with a JSON-RPC
communication on port 6080: ::

    connection = odoolib.get_connection(hostname="localhost", protocol="jsonrpc", port=6080, ...)

The get_model() method on the Connection object creates a Model object. That object represents a
remote model on the Odoo server (for Odoo addon programmers, those are also called osv).
Model objects are dynamic proxies, which means you can remotely call methods in a natural way.
In the previous script we demonstrate the usage of the search() and read() methods. That scenario
is equivalent to the following interaction when you are coding an Odoo addon and this code is
executed on the server: ::

    user_osv = self.pool.get('res.users')
    ids = user_osv.search([("login", "=", "admin")])
    user_info = user_osv.read(ids[0], ["name"])

Also note that coding using Model objects offer some syntaxic sugar compared to vanilla addon coding:

- The read() method automatically sort rows according the order of the ids you gave it to.
- The Model objects also provides the search_read() method that combines a search and a read, example: ::
    
    user_info = user_model.search_read([('login', '=', 'admin')], ["name"])[0]

Here are also some considerations about coding using the Odoo Client Library:

- Since you are using remote procedure calls, every call is executed inside its own transaction. So it can
  be dangerous, for example, to code multiple interdependant row creations. You should consider coding a method 
  inside an Odoo addon for such cases. That way it will be executed on the Odoo server and so it will be
  transactional.
- The browse() method can not be used. That method returns a dynamic proxy that lazy loads the rows' data from
  the database. That behavior is not implemented in the Odoo Client Library.

JSON-RPC
--------

The jsonrpc protocol is available since Odoo version 8.0. It has the exact same methods as the XML-RPC protocol,
but uses a different endpoint: `/jsonrpc/`. The Odoo Client Library provides a `get_connection()` to specify the protocol to use.

The only difference between XML-RPC and JSON-RPC is that the latter uses a JSON payload instead of an XML payload.

JSON2
-----

The Json2 appears with Odoo version 19.0, and requires every method to be called with named parameters.
If the method is called with positional arguments, the library will try to introspect the method
and convert the positional arguments into named parameters. This introspection is done only once per model.
Introspection means a server call, which can slow down the first method call for a given model. Using named parameters
is recommended for performance reasons.

With this new `/json/2/` endpoint, this library is less useful than before, but makes it easy to move older scripts
to the new endpoint.

Compatibility
-------------

- XML-RPC: OpenERP version 6.1 and superior

- JSON-RPC: Odoo version 8.0 and superior

- JSON2: Odoo version 19.0 and superior

SSL Communication
-----------------

The Odoo Client Library supports both XML-RPC and JSON-RPC over SSL. The difference is that it uses
the HTTPS protocol, which means that the communication is encrypted. This is useful when you want to
communicate with an Odoo server over the internet, as it prevents eavesdropping and man-in-the-middle attacks.
To use XML-RPC over SSL, you can specify the protocol when creating the connection: ::

    connection = odoolib.get_connection(hostname="localhost", protocol="xmlrpcs", ...)

the possible values for the protocol parameter are:
- `xmlrpc`: standard XML-RPC over HTTP (Odoo version 6.1 to 19.0)
- `xmlrpcs`: XML-RPC over HTTPS (Odoo version 6.1 to 19.0)
- `jsonrpc`: standard JSON-RPC over HTTP (Odoo version 8.0 to 19.0)
- `jsonrpcs`: JSON-RPC over HTTPS (Odoo version 8.0 to 19.0)
- `json2`: JSON2 over HTTP (Odoo version 19.0 and superior)
- `json2s`: JSON2 over HTTPS (Odoo version 19.0 and superior)

