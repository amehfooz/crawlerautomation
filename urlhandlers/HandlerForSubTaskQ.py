'''
Created on Jan 10, 2014
@author: primeuser=Hari
'''
import webapp2
import traceback
import pickle
from utilities.logger import logThis, AEL_LEVEL_INFO, AEL_LEVEL_DEBUG,\
    AEL_LEVEL_CRITICAL
from constants.constants import SUBTASK_WEBREQ_PICKLED_TASKOBJ
from Tasks.AndroidCrawler import AndroidCrawler
from google.appengine.api import taskqueue
from constants.constants import dbG

class HandlerForSubTaskQ(webapp2.RequestHandler):
    def post(self):
        try:
            logThis(AEL_LEVEL_INFO, 'SUBTASK:START') 
            
            ac = AndroidCrawler(self.request.get('url'))
            
            logThis(AEL_LEVEL_INFO, str(ac.isdone()) )

            # Retry if task didn't succeed
            if ac.isdone() == False and ac.retry() == True:
                taskqueue.add(queue_name=GAEQ_FOR_SUBTASK,name=self.request.get('url'),
                              params={'url': self.request.get('url')} )
            elif ac.isdone() == True:
                print "TASK DONE"
                dbG.updateStatus([self.request.get('url')])

        #POST EXCEPT 
        except:
            logThis(AEL_LEVEL_CRITICAL, "EXP on HandlerForSubTaskQ-" + traceback.format_exc())
                        
app = webapp2.WSGIApplication([('/_ah/queue/subTaskQ', HandlerForSubTaskQ)
                   ], debug=True)