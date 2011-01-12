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
This library holds helper functions that know about what the application does but 
are decoupled from the implementation details - the goal is that it should be 
directly reusabe under Django
"""

import logging
from md5 import md5

from models import *

def ordinary_tags(taglist):
    """
    Returns a list of tagnames that have no special meaning

    Currently, the only one I have identified is the "restricted" tag.
    """
    return [t.lower() for t in taglist if t != 'restricted']


def import_a_post(user, post):
    logging.debug('storing post ' + post['link'] + ' from ' + user.nickname() + ' with tags "' + post['tag'] + '"')
    # Get the Link that corresponds to this URL
    link = Link.all().filter('hash_property =', post['hash']).get()
    if link:
        pass
    else:
        link = Link(href = post['link'], hash_property = post['hash'])
        link.put()
    # if there already exists a post, get it, if not, create one
    p = Post.all().filter('link =', link).filter('posted_by =', user).get()
    if p:
        # Already a post for this link and this user
        # We have to remove all PostTags that have no corresponding tags in this post - we are reimporting a post

        tags_to_delete = [ pt.tag.key().name() for pt in PostTag.all().filter('post =', p) 
                           if pt.tag.key().name() not in p.tags ]

        for tagname in tags_to_delete:
            logging.debug('should get rid of PostTag for post %s and tag %s' % (pt.tag.key().name(), pt.post.link.href))
 
    else:
        # We'll make a new post and add required Tag and PostTag objects
        p = Post(posted_by = user,
                 link = link,
                 description = post['description'],
                 hash_property = post['hash'],
                 tags = ordinary_tags(post['tag'].split(' ')),
                 extended = post['extended'],
                 meta = post['meta'],
                 restricted = 'restricted' in post['tag'].split(' '))
        p.put()
            
    if post['tag']:
        for tagname in ordinary_tags(post['tag'].split(' ')):
            p.add_tag(tagname)
        
    return p


def import_posts(user, posts):
    """
    This will import posts (provided as a list of dictionaries), add "ordinary" tags and, perhaps, if we decide so, treat "for:" tags independently
    """
    for post in posts:
        import_a_post(user, post)
