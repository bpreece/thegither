from google.appengine.api import users

import os
import urllib
import jinja2
import webapp2

import model

JINJA_ENVIRONMENT = jinja2.Environment(
   loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
   extensions=['jinja2.ext.autoescape'])

from google.appengine.ext import ndb
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.runtime import DeadlineExceededError


BOARDS_PER_QUERY = 20
POSTS_PER_QUERY = 20


"""
A page to display the boards which belong to the user
"""
class UserBoards(webapp2.RequestHandler):

   """
   Proces an HTML GET request
   """
   def get(self):

      # The user must be signed on to view this page.

      user = users.get_current_user()
      if not user:
         self.redirect(users.create_login_url(self.request.uri))
         return

      # Set the basic values for the HTML template

      template_values = {
         'user': user,
         'sign_off_url': users.create_logout_url('/'),
         'body_class': 'user-boards',
         'page_title': 'My Boards',
      }

      # Fetch the next 20 boards from the datastore.  The 'x' field in the
      # URL's query string indicates an offset into the datastore.

      start = self.request.get('x')
      if start:
         boards, cursor, more = model.Board.query_next_by_owner(user.user_id(), start, BOARDS_PER_QUERY)
      else:
         boards, cursor, more = model.Board.query_by_owner(user.user_id(), BOARDS_PER_QUERY)
      template_values.update({
         'boards': boards,
      })

      # If there are still more boards to query, the template needs to add a
      # 'more' button

      if more:
         template_values.update({
            'x': cursor.urlsafe(),
         })

      # Now display the page

      template = JINJA_ENVIRONMENT.get_template('template/user.html')
      self.response.write(template.render(template_values))


"""
A page to display a list of posts created by the user
"""
class UserPosts(webapp2.RequestHandler):

   """
   Process an HTML GET request
   """
   def get(self):

      # The user must be signed on to view this page.

      user = users.get_current_user()
      if not user:
         self.redirect(users.create_login_url(self.request.uri))
         return

      # Set the basic values for the HTML template

      template_values = {
         'user': user,
         'sign_off_url': users.create_logout_url('/'),
         'body_class': 'user-boards',
         'page_title': 'My Posts',
      }

      # Fetch the next 20 boards from the datastore.  The 'x' field in the
      # URL's query string indicates an offset into the datastore.

      start = self.request.get('x')
      if start:
         posts, cursor, more = model.Posting.query_next_by_poster(user.user_id(), start, POSTS_PER_QUERY)
      else:
         posts, cursor, more = model.Posting.query_by_poster(user.user_id(), POSTS_PER_QUERY)
      template_values.update({
         'posts': posts,
      })

      # If there are still more boards to query, the template needs to add a
      # 'more' button

      if more:
         template_values.update({
            'x': cursor.urlsafe(),
         })

      # Now display the page

      template = JINJA_ENVIRONMENT.get_template('template/user.html')
      self.response.write(template.render(template_values))


application = webapp2.WSGIApplication([
   ('/user-posts', UserPosts),
   ('/user-boards', UserBoards),
   ], debug=True)

