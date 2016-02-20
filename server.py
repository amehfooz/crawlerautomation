import sys
import cgi
import datetime
import os
import webapp2
import traceback

from utilities.logger import logThis, AEL_LEVEL_CRITICAL

class MainPage(webapp2.RequestHandler):
    def get(self):
        try:    
            self.response.write('''
    <ul>
      <li><a href="#env">Environment Variables</a></li>
      <li><a href="#filesystem">File System</a></li>
      <li><a href="#request">Request Data</a></li>
    </ul>
    
    <hr noshade><h2 id="env">Environment Variables</h2><table>
    ''')
            keys = os.environ.keys()
            keys.sort()
            for k in keys:
                self.response.write('<tr><td valign="top"><code>%s</code></td>'
                                    '<td valign="top"><code>%s</code></td></tr>'
                                    % (cgi.escape(k),
                                       cgi.escape(str(os.environ[k]))))
            self.response.write('''
    </table>
    
    <hr noshade><h2 id="filesystem">File System</h2>
    <pre>''')
    
            for path, dirnames, filenames in os.walk('.'):
                for filename in filenames:
                    self.response.write(
                        cgi.escape(os.path.join(path, filename)) + '\n')
            self.response.write('''
    </pre>
    
    <hr noshade><h2 id="request">Request Data</h2>
    <pre>''')
            self.response.write(cgi.escape(sys.stdin.read()))
            self.response.write('</pre>')
    
            self.response.write('<hr noshade><p>The time is: %s</p>'
                                % str(datetime.datetime.now()))

        except:
            logThis(AEL_LEVEL_CRITICAL, "EXP on Maina\Page-" + traceback.format_exc())
            
#App to handle the default page 
app = webapp2.WSGIApplication([('/', MainPage)
                               ], debug=True)