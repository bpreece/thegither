from google.appengine.api import users
from google.appengine.datastore.datastore_query import Cursor

import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2

class Board(ndb.Model):
   owner_id = ndb.StringProperty(indexed=True)
   timestamp = ndb.DateTimeProperty(auto_now_add=True)
   board_title = ndb.StringProperty(indexed=True)
   have_label = ndb.StringProperty()
   want_label = ndb.StringProperty()
   published = ndb.BooleanProperty()
   open_to_posts = ndb.BooleanProperty(default=True)
   anonymous_permission = ndb.StringProperty() # one of 'read-write', 'read-only', or 'no-access'
   description = ndb.TextProperty()

   def is_readable_by_user(self, user):
      return (users.is_current_user_admin() or
            self.published)

   def is_writable_by_user(self, user):
      return (users.is_current_user_admin() or
            (user != None and user.user_id() == self.owner_id))

   def is_postable_by_user(self, user):
      return (users.is_current_user_admin() or
            (user != None and self.open));

   @staticmethod
   def query_all(count):
      # returns (results, cursor, more)
      return Board.query().order(Board.timestamp).fetch_page(count)

   @staticmethod
   def query_all_next(start, count):
      # returns (results, cursor, more)
      return Board.query().order(Board.timestamp).fetch_page(count, start_cursor=Cursor(urlsafe=start))

   @staticmethod
   def query_by_owner(owner, count):
      # returns (results, cursor, more)
      return Board.query(Board.owner_id == owner).order(Board.timestamp).fetch_page(count)

   @staticmethod
   def query_next_by_owner(owner, start, count):
      # returns (results, cursor, more)
      query = Board.query(Board.owner_id == owner).order(Board.timestamp)
      return query.fetch_page(count, start_cursor=Cursor(urlsafe=start))

   @staticmethod
   def query_by_id(id):
      return ndb.Key(urlsafe=id).get()


class Posting(ndb.Model):
   board_id = ndb.StringProperty(indexed=True)
   poster = ndb.StringProperty(indexed=True)
   timestamp = ndb.DateTimeProperty(auto_now_add=True)
   type = ndb.StringProperty() # one of 'have' or 'want'
   summary = ndb.StringProperty()
   information = ndb.StringProperty()
   published = ndb.BooleanProperty()
   open_to_responses = ndb.BooleanProperty(default=True)

   def is_readable_by_user(self, user):
      return (users.is_current_user_admin() or
            (user != None and user.user_id() == self.poster) or
            (self.published and Board.query_by_id(self.board_id).published))

   def is_writable_by_user(self, user):
      return (users.is_current_user_admin() or
            (user != None and user.user_id() == self.poster))

   def is_respondable_by_user(self, user):
      return (users.is_current_user_admin() or
            (user != None and self.open));

   @staticmethod
   def query_published_by_board(board, count):
      # returns (results, cursor, more, count)
      query = Posting.query(
         Posting.board_id == board, 
         Posting.published == True
      ).order(Posting.timestamp)
      return query.fetch_page(count)

   @staticmethod
   def query_next_published_by_board(board, start):
      # returns (results, cursor, more, count)
      query = Posting.query(
         Posting.board_id == board, 
         Posting.published == True
      ).order(Posting.timestamp)
      return query.fetch_page(count, start_cursor = Cursor(urlsafe=start))

   @staticmethod
   def query_by_board(board, count):
      # returns (results, cursor, more)
      return Posting.query(Posting.board_id == board).order(Posting.timestamp).fetch_page(count)

   @staticmethod
   def query_next_by_board(board, start, count):
      # returns (results, cursor, more)
      query = Posting.query(Posting.board_id == board).order(Posting.timestamp)
      return query.fetch_page(count, start_cursor = Cursor(urlsafe=start))

   @staticmethod
   def query_by_poster(poster, count):
      # returns (results, cursor, more)
      return Posting.query(Posting.poster == poster).order(Posting.timestamp).fetch_page(count)

   @staticmethod
   def query_next_by_poster(poster, start, count):
      # returns (results, cursor, more)
      query = Posting.query(Posting.poster == poster).order(Posting.timestamp)
      return query.fetch_page(count, start_cursor = Cursor(urlsafe=start))

   @staticmethod
   def query_by_id(id):
      return ndb.Key(urlsafe=id).get()

class Response(ndb.Model):
   board_id = ndb.StringProperty(indexed=True)
   post_id = ndb.StringProperty(indexed=True)
   responder = ndb.StringProperty(indexed=True)
   responder_name = ndb.StringProperty(indexed=True)
   responder_email = ndb.StringProperty(indexed=True)
   timestamp = ndb.DateTimeProperty(auto_now_add=True)
   message = ndb.StringProperty()

   @staticmethod
   def query_by_post(post, count):
      # returns (results, cursor, more)
      return Response.query(Response.post_id == post).order(Response.timestamp).fetch_page(count)

   @staticmethod
   def query_next_by_post(post, start, count):
      # returns (results, cursor, more)
      query =Response.query(Response.post_id == post).order(Response.timestamp)
      return query.fetch_page(count, start_cursor = Cursor(urlsafe=start))

   @staticmethod
   def query_by_id(id):
      return ndb.Key(urlsafe=id).get()

