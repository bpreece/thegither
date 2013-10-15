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
The front Thegither page
"""
class MainBoard(webapp2.RequestHandler):

   """
   Process an HTTP GET request
   """
   def get(self):

      # Fetch the board from the datastore

      template_values = {
         'body_class': 'main',
      }

      # Get the user making the query, and set the template values accordingly

      user = users.get_current_user()
      if user:
         template_values.update({
            'user': user,
            'is_admin': users.is_current_user_admin(),
            'sign_off_url': users.create_logout_url('/'),
         })
      else:
         template_values.update({
            'sign_on_url': users.create_login_url(self.request.uri),
         })

      # Now display the page

      template = JINJA_ENVIRONMENT.get_template('template/main.html')
      self.response.write(template.render(template_values))



application = webapp2.WSGIApplication([
   ('/', MainBoard)
   ], debug=True)

