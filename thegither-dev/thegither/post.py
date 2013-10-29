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


RESPONSES_PER_QUERY = 20


"""
A page to display a board posting
"""
class Post(webapp2.RequestHandler):

   """
   Proces an HTTP GET request
   """
   def get(self):

      # Validate the request parameters.  The query needs to include an ID for
      # the posting.

      id = self.request.get('id')
      if not id:
         self.error(404)
         self.response.out.write('<div class="user-message">The page you\'re looking for does not exist.</div>')
         return

      # Fetch the posting from the datastore, and the board that the posting
      # belongs to

      try:
         post = model.Posting.query_by_id(id)
         board = model.Board.query_by_id(post.board_id)
      except Exception:
         self.error(404)
         self.response.out.write('<div class="user-message">The page you\'re looking for does not exist.</div>')
         return

      # set the basic values for the HTML template

      template_values = {
         'post': post,
         'post_id': id,
         'board': board,
         'board_id': post.board_id,
         'body_class': 'post',
         'page_title': board.board_title,
         'labels': { 'have': board.have_label, 'want': board.want_label },
      }

      user = users.get_current_user()
      if user:
         template_values.update({
            'user': user,
            'sign_off_url': users.create_logout_url('/'),
         })
      else:
         template_values.update({
            'sign_on_url': users.create_login_url(self.request.uri),
         })

      id = self.request.get('id')
      if id:
         post = model.Posting.query_by_id(id)
         board = model.Board.query_by_id(post.board_id)

      # Check that the posting is published

      if not post.is_readable_by_user(user):
         self.error(404)
         self.response.out.write('<div class="user-message">The page you\'re looking for does not exist.</div>')
         return

      responses, cursor, more = model.Response.query_by_post(id, RESPONSES_PER_QUERY)
      if responses:
         template_values.update({
            'responses': responses,
         })

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

      # If this page is displayed as the result of updating the posting, then
      # there will a query paramater 'm', and we need to display a 
      # confirmation to the user.

      m = self.request.get('m')
      if m:
         template_values.update({
            'message': 'Your response has been sent to the poster.',
         })

      # Now display the page

      template = JINJA_ENVIRONMENT.get_template('template/post.html')
      self.response.write(template.render(template_values))


   """
   Process an HTTP POST request.  This will be a user posting a response to
   this post.
   """
   def post(self):

      # The user must be signed on to respond to this posting

      user = users.get_current_user()
      if not user:
         self.redirect(users.create_login_url(self.request.uri))
         return

      # Fetch the posting from the datastore, and the board that the posting
      # belongs to

      id = self.request.get('post-id')
      if not id:
         self.error(404)
         self.response.out.write('<div class="user-message">The page you\'re looking for does not exist.</div>')
         return

      try:
         post = model.Posting.query_by_id(id)
      except Exception:
         self.error(404)
         self.response.out.write('<div class="user-message">The page you\'re looking for does not exist.</div>')
         return

      # Create a new response and write it to the datastore

      response = model.Response(board_id = post.board_id, post_id = post.key.urlsafe())
      response.responder = user.user_id()
      response.responder_name = user.nickname()
      response.responder_email = user.email()
      response.message = self.request.get('response-text')
      response_key = response.put().urlsafe()

      # Now display the posting

      self.redirect('/post?id={}&m=1'.format(id))


application = webapp2.WSGIApplication([
   ('/post', Post)
   ], debug=True)

