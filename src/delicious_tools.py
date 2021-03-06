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

"""
This library holds helper functions that know about delicious but are decoupled 
from the application and should be easily reusable in any other program that deals
with delicious
"""

import datetime
import logging
import sys
reload(sys); sys.setdefaultencoding('utf-8')

from xml.dom import minidom # import parse, parseString


class DeliciousXML(object):

    def __init__(self, xml_string):
        self.posts = []
        doc = minidom.parseString(xml_string)

        self.delicious_login = doc.firstChild.getAttribute('user')

        for node in minidom.parseString(xml_string).getElementsByTagName('post'):
            self.posts.append({'link': node.getAttribute('href'),
                          'description': node.getAttribute('description'),
                          'hash': node.getAttribute('hash'), # We can check - this is the MD5 of the URL
                          'time': datetime.datetime.strptime(node.getAttribute('time'), '%Y-%m-%dT%H:%M:%SZ'),
                          'extended': node.getAttribute('extended'),
                          'tag': node.getAttribute('tag'),
                          'meta': node.getAttribute('meta')
                          })
            logging.debug('reading post ' + node.getAttribute('href'))


    
