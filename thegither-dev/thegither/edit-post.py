
from google.appengine.api import users

import cgi
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
A page to edit the contents of a new or existing posting
"""
class EditPost(webapp2.RequestHandler):

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
         'body_class': 'edit-post',
         'page_title': 'New Post',
      }

      # Validate the query parameters.  If the query string in the URL includes
      # an ID, then we're editing an existing posting;  otherwise we're creating
      # a new posting.

      id = self.request.get('id')
      if id:

         # We're editing an existing posting; fetch the posting from the
         # datastore

         try:
            post = model.Posting.query_by_id(id)
         except Exception:
            self.error(404)
            self.response.out.write('<div class="user-message">The page you\'re looking for does not exist.</div>')
            return

         # Verify that the user has permission to edit the posting

         if not post.is_writable_by_user(user):
            self.redirect('/board?id={}'.format(id))
            return

         # Fetch the posting's board from the datastore and set the values
         # for the template to pre-populate the form fields.

         board = model.Board.query_by_id(post.board_id)
         template_values.update({
            'page_title': 'Edit Post',
            'post': post,
            'board': board,
            'board_id': post.board_id,
            'have_checked': 'checked' if post.type == 'have' else '',
            'want_checked': 'checked' if post.type == 'want' else '',
            'published': 'checked' if post.published else '',
            'closed': '' if post.open_to_responses else 'checked',
         })

      else:

         # We're creating a new posting.  The query string must have an ID for
         # the board that contains the posting.

         board_id = self.request.get('board-id')
         if not board_id:
            self.error(404)
            self.response.out.write('<div class="user-message">The page you\'re looking for does not exist.</div>')
            return

         # Fetch the board from the datastore

         try:
            board = model.Board.query_by_id(board_id)
         except Exception:
            self.error(404)
            self.response.out.write('<div class="user-message">The page you\'re looking for does not exist.</div>')
            return

         # Set the values for the template to pre-populate the form fields.

         template_values.update({
            'page_title': board.board_title,
            'board': board,
            'board_id': board_id,
            'have_checked': 'checked',
            'published': 'checked',
         })

      # Now display the form

      template = JINJA_ENVIRONMENT.get_template('template/edit-post.html')
      self.response.write(template.render(template_values))

   def post(self):

      user = users.get_current_user()

      id = self.request.get('id')
      board_id = self.request.get('board-id')
      if id:
         post = ndb.Key(urlsafe=id).get()
         if post.poster != user.user_id():
            self.redirect('/post?id={}'.format(id))
            return
      else:
         post = model.Posting(board_id = board_id)

      post.poster = user.user_id()
      post.type = self.request.get('post-type')
      post.summary = self.request.get('summary-field')
      post.information = self.request.get('information-field')
      post.published = True if self.request.get('published-checkbox') else False
      post.open_to_responses = False if self.request.get('closed-checkbox') else True;
      post.description = self.request.get('description')
      urlsafe_key = post.put().urlsafe()

      self.redirect('/post?id={}'.format(urlsafe_key))


application = webapp2.WSGIApplication([
   ('/edit-post', EditPost)
   ], debug=True)

