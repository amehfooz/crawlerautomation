import sys
sys.path.insert(0, 'libs')

import webapp2

from google.appengine.api import taskqueue
from AndroidCrawler import AndroidCrawler

class CrawlHandler(webapp2.RequestHandler):
    def post(self):
        taskqueue.add(url='/worker')
        
        self.redirect('/')
        
class CrawlWorker(webapp2.RequestHandler):
    def post(self): 
        @ndb.transactional
        def update_app():
            print 'Task Pushed'
            AndroidCrawler('https://play.google.com/store/apps/details?id=com.snapchat.android')

        update_app()
        
app = webapp2.WSGIApplication([
    ('/', CrawlHandler)], debug = True)