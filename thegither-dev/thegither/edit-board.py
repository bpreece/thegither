
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


"""
A page to edit the attributes of a new or existing board
"""
class EditBoard(webapp2.RequestHandler):

   """
   Process an HTTP GET request
   """
   def get(self):

      # The user must be signed on to view this page

      user = users.get_current_user()
      if not user:
         self.redirect(users.create_login_url(self.request.uri))
         return

      # set the basic values for the HTML template

      template_values = {
         'user': user,
         'sign_off_url': users.create_logout_url('/'),
         'body_class': 'edit-board',
         'page_title': 'New Board',
      }

      # Validate the query parameters.  If the query string in the URL includes
      # an ID, then we're editing an existing board;  otherwise we're creating
      # a new board.

      id = self.request.get('id')
      if id:

         # Fetch the board from the datastore

         try:
            board = ndb.Key(urlsafe=id).get()
         except Exception:
            self.error(404)
            self.response.out.write('<div class="user-message">The board you\'re looking for does not exist.</div>')
            return

         # Verify that the user has permission to edit the board

         if not board.is_writable_by_user(user):
            self.redirect('/board?id={}'.format(id))
            return

         # Set the boards properties, and provide the values needed to
         # pre-populate the form fields

         template_values.update({
            'page_title': board.board_title,
            'owner_id': board.owner_id,
            'board_id': id,
            'board_title': board.board_title,
            'have_label': board.have_label,
            'want_label': board.want_label,
            'published': 'checked' if board.published else '',
            'closed': '' if board.open_to_posts else 'checked',
            'description': board.description,
         })

      # Now display the page

      template = JINJA_ENVIRONMENT.get_template('template/edit-board.html')
      self.response.write(template.render(template_values))


   """
   Process an HTTP POST request
   """
   def post(self):

      user = users.get_current_user()
      id = self.request.get('id')

      # The user must be signed on to post this data

      if not user:
         if id:
            self.redirect('/board?id={}'.format(id))
         else:
            self.error(404)
            self.response.out.write('<div class="user-message">The page you\'re looking for does not exist.</div>')
         return

      if id: # The user must own an existing board to edit it, or must be administrator

         board = ndb.Key(urlsafe=id).get()
         if not (board.owner_id == user.user_id() or users.is_current_user_admin()):
            self.error(404)
            self.response.out.write('<div class="user-message">The page you\'re looking for does not exist.</div>')
            return

      else: # Create a new board and assign it to the user

         board = model.Board()
         board.owner_id = user.user_id()

      # Apply the values from the form to the datastore

      board.board_title = self.request.get('title-field', 'Provide a title for this post board')
      board.have_label = self.request.get('have-label-field', 'HAVE')
      board.want_label = self.request.get('want-label-field', 'WANT')
      board.published = True if self.request.get('publish-checkbox') else False
      board.open_to_posts = False if self.request.get('closed-checkbox') else True;
      board.description = self.request.get('description-field', 'Provide a description')
      urlsafe_key = board.put().urlsafe()

      # Now show the contents of the updated board

      self.redirect('/board?id={}'.format(urlsafe_key))


application = webapp2.WSGIApplication([
   ('/edit-board', EditBoard)
   ], debug=True)

