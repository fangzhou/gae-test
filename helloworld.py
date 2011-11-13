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

class Greeting(db.Model):
    """Models an individual Guestbook entry with an author, content, and date."""
    author = db.UserProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)

def guestbook_key(guestbook_name=None):
    """Constructs a datastore key for a Guestbook entity with guestbook_name."""
    return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')

class MainPage(webapp.RequestHandler):
    def get(self):
        guestbook_name=self.request.get('guestbook_name')

        # Below two statement equals with db.GqlQuery() statement
        greetings_query = Greeting.all().ancestor(guestbook_key(guestbook_name)).order('-date')
        greetings = greetings_query.fetch(10)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.url)
            url_linktext = 'Login'

        template_values = {
            'greetings': greetings,
            'url': url,
            'url_linktext': url_linktext,
            }

        path = os.path.join(os.path.dirname(__file__), 'index.html')

        # Render the page
        self.response.out.write(template.render(path, template_values))

# class MainPage(webapp.RequestHandler):
#     def get(self):
#         self.response.out.write('<html><body>')
#         guestbook_name=self.request.get('guestbook_name')

#         greetings = db.GqlQuery("SELECT * "
#                                 "FROM Greeting "
#                                 "WHERE ANCESTOR IS :1 "
#                                 "ORDER BY date DESC LIMIT 10",
#                                 guestbook_key(guestbook_name))

#         for greeting in greetings:
#             if greeting.author:
#                 self.response.out.write('<b>%s</b> wrote at <i>%s</i>:' % greeting.author.nickname(), greeting.date.strftime("%a %b %d %Y  %H:%M "))
#             else:
#                 self.response.out.write('An anonymous person wrote at <i>%s</i>:' % greeting.date.strftime("%a %b %d %Y  %H:%M "))

#             self.response.out.write('<blockquote>%s</blockquote>' % cgi.escape(greeting.content))


#         self.response.out.write("""
#              <form action="/sign?%s" method="post">
#                <div><textarea name="content" rows="3" cols="60"></textarea></div>
#                <div><input type="submit" value="Sign Guestbook"></div>
#              </form>
#              <hr>
#              <form>Guestbook name: <input value="%s" name="guestbook_name">
#              <input type="submit" value="switch"></form>
#            </body>
#          </html>""" % (urllib.urlencode({'guestbook_name': guestbook_name}),
#                        cgi.escape(guestbook_name)))


class Guestbook(webapp.RequestHandler):
    def post(self):

        guestbook_name = self.request.get('guestbook_name')
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = users.get_current_user()

        greeting.content = self.request.get('content')
        greeting.date = datetime.now()
        greeting.put()
        self.redirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))

application = webapp.WSGIApplication([('/', MainPage), ('/sign', Guestbook)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
