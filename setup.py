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

from distutils.core import setup
import os.path


setup(name='odoo-client-lib',
      version='1.2.0',
      description='Odoo Client Library allows to easily interact with Odoo in Python.',
      author='Nicolas Vanhoren',
      author_email='',
      url='',
      packages=["odoolib"],
      install_requires=[
          'requests',
      ],
      long_description="See the home page for any information: https://github.com/odoo/odoo-client-lib .",
      keywords="openerp library com communication rpc xml-rpc net-rpc xmlrpc python client lib web service",
      license="BSD",
      classifiers=[
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python",
          ],
     )
