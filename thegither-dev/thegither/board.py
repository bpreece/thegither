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


"""
A page to display a list of all boards which have been created.
"""
class Boards(webapp2.RequestHandler):

   """
   Process an HTML GET request
   """
   def get(self):

      # only the site admin is allowed to access this page

      if not users.is_current_user_admin():
         self.redirect('/')
         return
      user = users.get_current_user()

      # set the basic values for the HTML template

      template_values = {
         'body_class': 'boards',
         'page_title': 'All Boards',
         'is_admin': users.is_current_user_admin(),
         'user': user,
         'sign_off_url': users.create_logout_url('/'),
      }

      # Fetch the next 20 boards from the datastore.  The 'x' field in the
      # URL's query string indicates an offset into the datastore.

      start = self.request.get('x')
      if start:
         boards, cursor, more = model.Board.query_all_next(start, BOARDS_PER_QUERY)
      else:
         boards, cursor, more = model.Board.query_all(BOARDS_PER_QUERY)
      template_values.update({
         'boards': boards,
      })

      # If there are still more boards to query, the template needs to add a
      # 'more' button

      if more:
         template_values.update({
            'x': cursor.urlsafe(),
         })

      # Now sho the page

      template = JINJA_ENVIRONMENT.get_template('template/boards.html')
      self.response.write(template.render(template_values))


"""
A page to display all the postings in a single board
"""
class Board(webapp2.RequestHandler):

   """
   Process an HTML GET request
   """
   def get(self):

      # Validate the request parameters.  The query needs to include an ID for
      # the board.

      id = self.request.get('id')
      if not id:
         self.error(404)
         self.response.out.write('<div class="user-message">The page you\'re looking for does not exist.</div>')
         return

      # Fetch the board from the datastore

      try:
         board = model.Board.query_by_id(id)
      except Exception:
         self.error(404)
         self.response.out.write('<div class="user-message">The page you\'re looking for does not exist.</div>')
         return

      # set the basic values for the HTML template

      template_values = {
         'body_class': 'board',
         'board': board,
         'board_id': id,
         'page_title': board.board_title,
         'labels': { 'have': board.have_label, 'want': board.want_label },
      }

      # Get the user making the query, and set the template values accordingly

      user = users.get_current_user()
      if user:
         template_values.update({
            'user': user,
            'sign_off_url': users.create_logout_url('/'),
            'can_write': board.is_writable_by_user(user),
         })
      else:
         template_values.update({
            'sign_on_url': users.create_login_url(self.request.uri),
         })

      # Fetch the next 20 posts from the datastore.  The 'x' field in the
      # URL's query string indicates an offset into the datastore.

      start = self.request.get('x')
      if start:
         posts, cursor, more = model.Posting.query_next_published_by_board(id, start, BOARDS_PER_QUERY)
      else:
         posts, cursor, more = model.Posting.query_published_by_board(id, BOARDS_PER_QUERY)

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

      template = JINJA_ENVIRONMENT.get_template('template/board.html')
      self.response.write(template.render(template_values))


application = webapp2.WSGIApplication([
   ('/boards', Boards),
   ('/board', Board)
   ], debug=True)

