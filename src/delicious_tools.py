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

import sys
reload(sys); sys.setdefaultencoding('utf-8')

from xml.dom import minidom # import parse, parseString

def posts(xml_string):
    """
    Returns all posts as a series of dictionaries
    """
    posts = []
    for node in minidom.parseString(xml_string).getElementsByTagName('post'):
        posts.append({'link': node.getAttribute('href'),
                      'description': node.getAttribute('description')})
    return posts
