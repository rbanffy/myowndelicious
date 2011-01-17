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
    """
    Properties associated with a user. The key is the user.user_id
    """
    delicious_login = db.StringProperty()

    def user_id(self):
        return self.key().name()

    def collect_mail(self):
        """
        Collects all posts with a for: tag for this user's delicious_login
        """
        tag = Tag.get_or_insert('for:' + self.delicious_login)
        [pt.post for pt in PostTag.all().filter('tag =', tag)]
            
        

class Link(db.Model):
    """
    Represents a URL that was bookmarked

    Maybe we look it up via the hash_property attribute (specially if we decide to turn it into a Long)
    """
    href = db.TextProperty(required = True) # LinkProperty is limited to 500 chars
    hash_property = db.StringProperty(required = True) # shouldn't call it "hash" or nasty things may happen
    description = db.TextProperty() # To be filled (cannot trust whatever was imported)
    to_be_filled = db.BooleanProperty(default = False) # Set to True when auto-description gets generated


    @classmethod
    def most_popular(cls, how_many = 10):
        """
        FIXME: This is a dummy class method
        """
        return Link.all()[:how_many]


class Post(db.Model):
    """
    Represents a bookmark
    """
    posted_by = db.UserProperty(required = True)
    link = db.ReferenceProperty(Link)
    description = db.TextProperty()
    # So far, hash_property seems to be a straighforward MD5 of the URL, but we'll confirm that in due time
    time = db.DateTimeProperty(auto_now_add = True)
    tags = db.ListProperty(str)
    extended = db.StringProperty()
    meta = db.StringProperty()
    restricted = db.BooleanProperty(default = False) # The special-meaning "restricted" tag lives here

    def add_tag(self, tagname):
        """
        Add a tag named "tagname" to this post
        """
        if tagname == 'restricted':
            raise ValueError('"restricted" tag should not be used as an ordinary tag')
        else:
            logging.debug('adding tag ' + tagname + ' for post ' + self.link.href)
            t = Tag.get_or_insert(tagname)
            pt = PostTag.all().filter('post =', self).filter('parent =', t).get()
            if pt:
                logging.debug('Post ' + self.key().name() + ' already had tag ' + tagname)
            else:
                pt = PostTag(post = self, tag = t, parent = t)
                pt.put()

            # Treat for:* tags
            if tagname.startswith('for:'):
                recipient_login = tagname[4:]
                recipient = UserProfile.all().filter('delicious_login =', recipient_login).get()
                if recipient:
                    # We only add the message if the recipient already exists
                    logging.debug('adding link %s to %s' % (self.description, recipient_login))
                    dm = DeliciousMessage.all().filter('sender =', self.posted_by)\
                        .filter('recipient =', recipient_login)\
                        .filter('post =', self).get()
                    if not dm:
                        DeliciousMessage(sender = self.posted_by,
                                         recipient_login = tagname[4:],
                                         post = self,
                                         dated = self.time).put()
                else:
                    logging.debug('recipient %s does not currently exist in the datastore' % recipient_login)
        return pt


class Tag(db.Model):
    """ 
    A tag. A Post can have as many tags as wanted

    Wondering if we can have no property beyond the key name (that's the tag name)
    """
    #tagname = db.CategoryProperty(required = True)
    pass

    @classmethod
    def most_popular(cls, how_many = 10):
        """
        FIXME: This is a dummy class method
        """
        return Tag.all()[:how_many]


class PostTag(db.Model):
    """
    The many-to-many relationship between tags and posts makes easy to find posts

    A tag is always the parent - keeps the tag relationships close in the datastore
    """
    post = db.ReferenceProperty(Post, required = True)
    tag = db.ReferenceProperty(Tag, required = True)


class DeliciousMessage(db.Model):
    """
    Represents the bookmarks with "for:*" tags
    """
    sender = db.ReferenceProperty(UserProfile, collection_name = 'posts_sent', required = True)
    recipient = db.ReferenceProperty(UserProfile, collection_name = 'posts_received', required = True)
    post = db.ReferenceProperty(Post, required = True)
    seen = db.BooleanProperty(default = True)
    dated = db.DateTimeProperty(required = True)
    
    @classmethod
    def incoming(cls, recipient, how_many = 10):
        """
        Returns all incoming messages of a given user
        """
        return DeliciousMessage.all().filter('recipient =', recipient)


# Entities used for reporting and building homes

# They should be updated by cron-jobs at the end of the day, but may be updated 
# during the day so we can have some data


class TagPopularity(db.Model):
    """
    The number of posts that refer to a given tag on a given date 

    Used for "popular tags" boxes
    """
    tag = db.ReferenceProperty(Tag, required = True)
    date = db.DateProperty(required = True)
    number_of_posts = db.IntegerProperty(required = True, default = 0)


class LinkPopularity(db.Model):
    """
    The number of posts that point to a given URL on a given date

    Used for "popular links" boxes
    """
    link = db.ReferenceProperty(Link, required = True)
    date = db.DateProperty(required = True)
    number_of_posts = db.IntegerProperty(required = True, default = 0)


class UserActivity(db.Model):
    """
    The number of posts for a given user on a given date
    
    Used for "most active" boxes
    """
    user = db.UserProperty(required = True)
    date = db.DateProperty(required = True)
    number_of_posts = db.IntegerProperty(required = True, default = 0)   
    
