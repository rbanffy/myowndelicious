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

import logging

# We are fine with importing something called models but importing the inhards of GAE would create too strong a coupling
from models import *


def ordinary_tags(taglist):
    return [t.lower() for t in taglist if t != 'restricted']

def import_a_post(user, post):
    #logging.debug('storing post ' + post['link'] + ' from ' + user)
    # Get the Link that corresponds to this URL
    link = Link.get_or_insert(post['link'])
    # if there already exists a post, get it, if not, create one
    p = Post.all().filter('link =', link).filter('posted_by =', user).get()
    if p:
        # Already a post for this link and this user
        # TODO: we'll have to remove all PostTags that have no corresponding tags in this post - we are reimporting a post
        pass
    else:
        # We'll have to make a post
        p = Post(posted_by = user,
                 link = link,
                 description = post['description'],
                 hash_property = post['hash'],
                 tags = ordinary_tags(post['tag'].split(' ')),
                 extended = post['extended'],
                 meta = post['meta'],
                 restricted = 'restricted' in post['tag'].split(' '))
        p.put()
            
    for tagname in ordinary_tags(post['tag']):
        p.add_tag(tagname)
        
    # Find each tag in the tags property and find/add a PostTag for each
    # Add a LinkTag for each tag that's neither a for: tag nor the "restricted"

    return p

def import_posts(user, posts):
    """
    This will import posts (provided as a list of dictionaries), add "ordinary" tags and, perhaps, if we decide so, treat "for:" tags independently
    """
    for post in posts:
        import_a_post(user, post)

