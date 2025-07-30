"""
Some unit tests. They assume there is an Odoo server running on localhost, on the default port
with a database named 'test' and a user 'admin' with password 'admin'. Should create an API key for json2 tests.
"""

import os
import odoolib
import unittest
from httpx import ConnectError

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        pass
    
    def _conn(self, protocol):
        password = "admin"
        if protocol == "json2":
            password = os.environ.get("JSON2_API_KEY", "")
            if not password:
                raise ValueError("Environment variable 'JSON2_API_KEY' is not set.")
        return odoolib.get_connection(hostname="localhost", protocol=protocol, 
                                         database="test", login="admin", password=password)

    def _get_protocols(self):
        return ["xmlrpc", "jsonrpc", "json2"]
        
    def _check_installed_language(self, connection, language):
        lang_ids = connection.get_model("res.lang").search(['&', ('code', '=', language), '|', ('active', '=', True), ('active', '=', False)])
        res = connection.get_model("base.language.install").create({'lang_ids': [(6, 0, lang_ids)], 'overwrite': False})
        connection.get_model("base.language.install").lang_install(res)
        
    def test_simple(self):
        for protocol in self._get_protocols():
            connection = self._conn(protocol)
            
            res = connection.get_model("res.users").read(1)

            self.assertEqual(res['id'], 1)
        
    def test_user_context(self):
        for protocol in self._get_protocols():
            connection = self._conn(protocol)
            
            connection.get_user_context()
        
        
    def test_multi_languages(self):
        for protocol in self._get_protocols():
            connection = self._conn(protocol)
            country_model = connection.get_model('res.country')
            
            self._check_installed_language(connection, "en_US")
            self._check_installed_language(connection, "fr_BE")
            ctx_en = {'lang': "en_US"}
            ctx_fr = {'lang': "fr_BE"}
            
            be_id = country_model.search([('code', '=', 'BE')])[0]
            
            be_en = country_model.search_read([('code', '=', 'BE')], ['name',], context=ctx_en)
            self.assertEqual(be_en[0]['id'], be_id)
            self.assertEqual(be_en[0]['name'], "Belgium")
            
            be_fr = country_model.search_read([('code', '=', 'BE')], ['name',], context=ctx_fr)
            self.assertEqual(be_fr[0]['id'], be_id)
            self.assertEqual(be_fr[0]['name'], "Belgique")

    def test_search_count(self):
        for protocol in self._get_protocols():
            connection = self._conn(protocol)
            country_model = connection.get_model('res.country')
            
            de_country_ids = country_model.search([('name', 'ilike', 'de')])
            de_country_count = country_model.search_count([('name', 'ilike', 'de')])
            
            self.assertEqual(de_country_count, len(de_country_ids))
            
    def _ssl_connection(self):
        connection = self._conn("jsonrpcs")
        connection.get_model("res.users").read(1)
        
    def test_ensure_s_require_ssl(self):
        self.assertRaises(ConnectError, self._ssl_connection)
        
         
if __name__ == '__main__':
    unittest.main()
