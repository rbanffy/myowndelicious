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
from google.appengine.api.labs import taskqueue
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


class SingleImportHandler(webapp.RequestHandler):
    """
    Asynchronously imports a given XML for a given user
    """

    def get(self):
        """
        Useful for testing
        """
        raise NotImplementedError

    def post(self):
        """
        Imports a single post

        username is the user's login
        post is the post in JSON format
        """
        logging.debug('importing a request in a worker')

        # import sys
        # for attr in ('stdin', 'stdout', 'stderr'):
        #     setattr(sys, attr, getattr(sys, '__%s__' % attr))
        # import pdb
        # pdb.set_trace()

        user = self.request.POST.get('username')
        post = self.request.POST.get('post')
        myowndelicious_tools.import_single(user, post)


application = webapp.WSGIApplication(
                                     [('/worker/import_single', SingleImportHandler), ],
                                     debug = True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
