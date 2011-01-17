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
import itertools 

from forms import *
from models import *

import delicious_tools 
import myowndelicious_tools



def batches(iterable, batch_size):
    """
    Breaks up an iterable into batches
    """
    i = iter(iterable)
    while True:
        bi = itertools.islice(i, batch_size)
        yield itertools.chain([bi.next()], bi)



class MainHandler(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            login_logout_line = '%s <a href="%s">logout</a>' % (users.get_current_user(), users.create_logout_url(self.request.uri))
        else:
            login_logout_line = '<a href="%s">login</a>' % users.create_login_url(self.request.uri)

        template_values = {'user': user,
                           'login_logout_line': login_logout_line}

        if user:
            up = UserProfile.get_by_key_name(user.user_id())
            template_values['incoming'] = DeliciousMessage.incoming(recipient = up)
            template_values['posts'] = Post.all().filter('posted_by =', user).order('-time').fetch(10)
        else:
            template_values['posts'] = (post for post in Post.all().filter('link in', Link.most_popular(10)))


        path = os.path.join(os.path.dirname(__file__), 'templates/main.html')
        self.response.out.write(template.render(path, template_values))


class PasteImportHandler(webapp.RequestHandler):
    """
    Deals with pasted XML

    We want it for testing and we may remove it in the future, or turn it into
    something better/that makes sense
    """

    def get(self):
        user = users.get_current_user()
        
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        else:
            f = BookmarksXMLImportForm()
            template_values = {'form': f,
                               'login_logout_line': '%s <a href="%s">logout</a>' % (users.get_current_user(), users.create_logout_url(self.request.uri)) }
            path = os.path.join(os.path.dirname(__file__), 'templates/simple_form.html')
            self.response.out.write(template.render(path, template_values))

    def post(self):
        user = users.get_current_user()
        
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        else:
            f = BookmarksXMLUploadImportForm(self.request)
            if f.is_valid():

                # import sys
                # for attr in ('stdin', 'stdout', 'stderr'):
                #     setattr(sys, attr, getattr(sys, '__%s__' % attr))
                # import pdb
                # pdb.set_trace()

                logging.debug('importing a request')
                xml_string = self.request.get('xml_data')
                xml = delicious_tools.DeliciousXML(xml_string)

                # Update the delicious_login property of the user profile
                up = UserProfile.get_or_insert(user.user_id())
                if up.delicious_login != None and up.delicious_login != xml.delicious_login:
                    # We have to decide what we do here
                    raise ValueError('delicious_login already set and different from file being imported')
                else:
                    up.delicious_login = xml.delicious_login
                    up.put()
                    up.collect_mail()

                posts = xml.posts

                for batch in batches(posts, 50):
                    logging.debug('importing a batch of posts')
                    myowndelicious_tools.import_posts(user, batch)
                    # TODO: It would be nice to dispatch one worker per batch here
                    # for post in posts:
                    #     taskqueue.Task(url='/worker/import_single', 
                    #                    method = 'POST',
                    #                    params={'user': account.username,
                    #                            'service': 'twitter'}).add('stats')



                message = '<ol>' + '\n'.join([ '<li>' + post['link'] + '</li>' for post in posts ]) + '</ol>'
            else:
                message = f.errors

            template_values = {'message': message}
            path = os.path.join(os.path.dirname(__file__), 'templates/simple_message.html')
            self.response.out.write(template.render(path, template_values))




class UploadImportHandler(webapp.RequestHandler):
    """
    Deals with uploaded XML
    """

    def get(self):
        user = users.get_current_user()
        
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        else:

            # import sys
            # for attr in ('stdin', 'stdout', 'stderr'):
            #     setattr(sys, attr, getattr(sys, '__%s__' % attr))
            # import pdb
            # pdb.set_trace()

            f = BookmarksXMLUploadImportForm()
            template_values = {'form': f,
                               'login_logout_line': '%s <a href="%s">logout</a>' % (users.get_current_user(), users.create_logout_url(self.request.uri)) }
            path = os.path.join(os.path.dirname(__file__), 'templates/simple_form.html')
            self.response.out.write(template.render(path, template_values))


    def post(self):
        user = users.get_current_user()
        
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        else:
            f = BookmarksXMLUploadImportForm(self.request)
            if f.is_valid():

                # import sys
                # for attr in ('stdin', 'stdout', 'stderr'):
                #     setattr(sys, attr, getattr(sys, '__%s__' % attr))
                # import pdb
                # pdb.set_trace()

                logging.debug('importing a request')
                xml_string = self.request.get('xml_data')
                xml = delicious_tools.DeliciousXML(xml_string)

                # Update the delicious_login property of the user profile
                up = UserProfile.get_or_insert(user.user_id())
                if up.delicious_login != None and up.delicious_login != xml.delicious_login:
                    # We have to decide what we do here
                    raise ValueError('delicious_login already set and different from file being imported')
                else:
                    up.delicious_login = xml.delicious_login
                    up.put()
                    up.collect_mail()

                posts = xml.posts

                for batch in batches(posts, 50):
                    logging.debug('importing a batch of posts')
                    myowndelicious_tools.import_posts(user, batch)
                    # TODO: It would be nice to dispatch one worker per batch here
                    # for post in posts:
                    #     taskqueue.Task(url='/worker/import_single', 
                    #                    method = 'POST',
                    #                    params={'user': account.username,
                    #                            'service': 'twitter'}).add('stats')



                message = '<ol>' + '\n'.join([ '<li>' + post['link'] + '</li>' for post in posts ]) + '</ol>'
            else:
                message = f.errors

            template_values = {'message': message}
            path = os.path.join(os.path.dirname(__file__), 'templates/simple_message.html')
            self.response.out.write(template.render(path, template_values))


def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/import_paste.html', PasteImportHandler),
                                          ('/import_upload.html', UploadImportHandler),],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
