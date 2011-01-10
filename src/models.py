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

from google.appengine.api import users
from google.appengine.ext import db

import datetime
import logging

class UserProfile(db.Model):
    user = db.UserProperty()
    delicious_login = db.StringProperty()


class Link(db.Model):
    """
    Represents a URL that was bookmarked

    Maybe we look it up via the hash_property attribute (specially if we decide to turn it into a Long)
    """
    #href = db.LinkProperty()
    # Maybe hash_property and meta belong here. We'll see with enough (more than one post per URL) data
    @property
    def href(self):
        return self.key().name()



class Post(db.Model):
    """
    Represents a bookmark
    """
    posted_by = db.UserProperty()
    link = db.ReferenceProperty(Link)
    description = db.TextProperty()
    hash_property = db.StringProperty() # shouldn't call it "hash" or nasty things may happen
    # So far, hash_property seems to be a straighforward MD5 of the URL, but we'll confirm that in due time
    time = db.DateTimeProperty(auto_now_add = True)
    tags = db.ListProperty(str)
    extended = db.StringProperty()
    meta = db.StringProperty()
    restricted = db.BooleanProperty(default = False) # The special-meaning "restricted" tag lives here

    def add_tag(self, tagname):
        tag = db.Category(tagname)
        if tagname == 'restricted':
            raise ValueError('"restricted" tag should not be used as an ordinary tag')
        else:
            logging.debug('adding tag ' + tag + ' for post ' + self.link.href)
            t = Tag.get_or_insert(tagname)
            pt = PostTag.all().filter('post =', self).filter('parent =', t).get()
            if pt:
                logging.debug('Post ' + self.key().name() + ' already had tag ' + tagname)
            else:
                pt = PostTag(post = self, tag = t, parent = t)
                pt.put()
        return pt


class Tag(db.Model):
    """ 
    A tag. A Post can have as many tags as wanted

    Wondering if we can have no property beyond the key name (that's the tag name)
    """
    tagname = db.CategoryProperty()


class PostTag(db.Model):
    """
    The many-to-many relationship between tags and posts makes easy to find posts

    A tag is always the parent - keeps the tag relationships close in the datastore
    """
    post = db.ReferenceProperty(Post)
    tag = db.ReferenceProperty(Tag)
    

# Entities used for reporting and building homes

# They should be updated by cron-jobs at the end of the day, but may be updated 
# during the day so we can have some data


class TagPopularity(db.Model):
    """
    The number of posts that refer to a given tag on a given date 
    """
    tagname = db.CharProperty()
    date = db.DateProperty()
    number_of_posts = db.IntegerProperty()


class LinkPopularity(db.Model):
    """
    The number of posts that point to a given URL on a given date
    """
    link = db.ReferenceProperty(Link)
    date = db.DateProperty()
    number_of_posts = db.IntegerProperty()
