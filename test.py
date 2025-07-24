# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) Stephane Wirtel
# Copyright (C) 2011 Nicolas Vanhoren
# Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>)
# Copyright (C) 2018 Odoo s.a. (<http://odoo.com>).
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
# 
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
##############################################################################

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
