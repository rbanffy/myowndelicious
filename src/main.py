#!/usr/bin/env python
# -*- coding:utf-8 -*-

# This file is part of "My Own Delicious".
#
# "My Own Delicious" is free software: you can redistribute it and/or modify it
# under the terms of the Affero GNU General Public License as published by the
#  Free Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
# "My Own Delicious" is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
# FITNESS FOR A PARTICULAR PURPOSE.  See the Affero GNU General Public License 
# for more details.
#
# You should have received a copy of the Affero GNU General Public License along 
# with "My Own Delicious".  If not, see <http://www.gnu.org/licenses/>.

from google.appengine.api import oauth
from google.appengine.api import urlfetch
from google.appengine.api import users 
from google.appengine.api import xmpp
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import run_wsgi_app

from django.utils import simplejson

import datetime
import os
import random
import logging

from forms import *
import delicious_tools 
import myowndelicious_tools

class MainHandler(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'templates/main.html')
        self.response.out.write(template.render(path, template_values))


class AsynchronousImportHandler(webapp.RequestHandler):
    """
    Deals with pasted XML

    We want it for testing and we may remove it in the future, or turn it into
    something better/that makes sense
    """

    def post(self, user, xml_string):
        logging.debug('Asynchronously importing a request')

        logging.debug('our xml has %d' % len(xml_string))
        posts = delicious_tools.posts(xml_string)
        myowndelicious_tools.import_posts(user, posts)


