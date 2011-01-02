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


class ImportHandler(webapp.RequestHandler):
    """
    Asynchronously imports a given XML for a given user
    """

    def get(self):
        user = users.get_current_user()
        
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        else:
            f = BookmarksXMLImportForm()
            template_values = {'form': f}
            path = os.path.join(os.path.dirname(__file__), 'templates/simple_form.html')
            self.response.out.write(template.render(path, template_values))

    def post(self):
        logging.debug('importing a request')

        user = users.get_current_user()

        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        else:
            # f = BookmarksXMLImportForm(self.request)
            # We cannot validate this form in the dev_appserver - f.is_valid() just hangs
            logging.debug('got the form')
            # We also cannot use the form data, so we must go directly to the request data
            xml_string = self.request.POST['xml_field']
            logging.debug('our xml has %d' % len(xml_string))
            posts = delicious_tools.posts(xml_string)
            myowndelicious_tools.import_posts(user, posts)
            message = '<ol>' + '\n'.join([ '<li>' + post['link'] + '</li>\n' for post in posts ]) + '</ol>'

            template_values = {'message': message}
            path = os.path.join(os.path.dirname(__file__), 'templates/simple_message.html')
            self.response.out.write(template.render(path, template_values))
