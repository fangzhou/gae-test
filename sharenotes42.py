import cgi
import datetime
import os
import urllib
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from time import gmtime, strftime
from datetime import datetime

class SNote(db.Model):
    """Models a note entry which include these fields: creator, shared_viewer, content, date."""
    creator = db.UserProperty()
    shared_viewer = db.StringProperty(multiline=False)
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)


class MainPage(webapp.RequestHandler):
    def get(self):

        if users.get_current_user():
            current_username = users.get_current_user().nickname()
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            snotes = db.GqlQuery("SELECT * FROM SNote WHERE shared_viewer = :1 ORDER BY date DESC", current_username)
            mynotes = db.GqlQuery("SELECT * FROM SNote WHERE creator = :1 ORDER BY date DESC", users.get_current_user())
            login_flag = 1
        else:
            url = users.create_login_url(self.request.url)
            url_linktext = 'Login'
            snotes = []
            mynotes = []
            login_flag = 0

        template_values = {
            'login_flag': login_flag,
            'mynotes': mynotes,
            'snotes': snotes,
            'url': url,
            'url_linktext': url_linktext,
            }

        path = os.path.join(os.path.dirname(__file__), 'index.html')

        # Render the page
        self.response.out.write(template.render(path, template_values))


class Notes(webapp.RequestHandler):
    def post(self):
        note = SNote()

        if users.get_current_user():
            note.creator = users.get_current_user()

        note.content = self.request.get('content')
        note.shared_viewer = self.request.get('shared_viewer')
        note.date = datetime.now()
        note.put()
        self.redirect('/?' + urllib.urlencode({'notes_user': note.creator}))


application = webapp.WSGIApplication([('/', MainPage), ('/sign', Notes)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
