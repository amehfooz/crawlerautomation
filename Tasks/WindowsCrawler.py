import requests
import pyquery
import json
import codecs
import itertools
import re
import requests, pyquery, json

offline = 0

class BaseCrawler(object):
    
    def check(self):
        if not self.result['name']:
            with open('failedpage.html', 'w', encoding='utf8') as f:
                f.write(self.pq.html())
            raise Exception('Received an incorrect page, please check failedpage.html')

    def __init__(self, url):
        if not offline:
            self.pq = pyquery.PyQuery(url)
        else:
            with open('temp.html', 'r', encoding='utf8') as f:
                html = f.read()
            self.pq = pyquery.PyQuery(html)
        self.result = {}


class WindowsCrawler(BaseCrawler):
    retries = {}
    def isdone(self):
        return self.done

    def retry(self):
        print self.retries[self.url]

        if self.retries[self.url] > 0:
            self.retries[self.url] -= 1
            return True
        return False

    @staticmethod
    def __get_reviews(app_id, num_pages=-1):
        reviews = []
        for page in itertools.count():
            url = 'https://www.microsoft.com/en-us/store/webapi/reviews?language=en-us&market=us&productId='+app_id+'&channelId=reviews&skipItems='+str(page*25)+'&pageSize=25'
            html = requests.get(url)
            js = json.loads(html.text)['Items']
            if not js:
                return reviews
            for review in js:
                extracted_data = {}
                extracted_data['authorname'] = review['UserName']
                extracted_data['text'] = review['ReviewText']
                extracted_data['rating'] = review['Rating']['AverageRating']
                extracted_data['title'] = review['Title']
                extracted_data['date'] = review['SubmittedDateTimeFormatted']
                reviews.append(extracted_data)
            
            if page == num_pages:
                return reviews

    def __init__(self, url, num_reviews=5):
        # set num_reviews to -1 to scrape everything
        super(WindowsCrawler, self).__init__(url)
        self.done = False
        self.url = url
        
        if url not in self.retries:
            self.retries[url] = 3

        self.result['name'] = self.pq('#page-title').text()
        self.check()
        self.result['store'] = 'Microsoft Store'
        self.result['price'] = self.pq('.header-sub').text()[1:]
        self.result['app_id'] = url.rsplit('/')[-1].upper()
        self.result['storeurl'] = url
        self.result['category'] = self.pq('[itemprop="\\"category\\""]').children().eq(0).text()
        self.result['content_rating'] = self.pq('dt:contains("Age rating")').next().children().eq(0).text()
        self.result['icon'] = 'https:'+self.pq('.cli_image').eq(0).attr('src')
        self.result['screenshots'] = ['https:'+x.attr('src').split('?')[0] for x in self.pq('img[alt="Screenshot"]').items()]
        self.result['description'] = self.pq('p.srv_description').text()
        self.result['permissions'] = [x.text() for x in self.pq('dt:contains("Capabilities")').next().children().eq(0).children().items()]
        self.result['developer'] = self.pq('dt:contains("Publisher")').next().children().eq(0).text()
        self.result['devlink'] = self.pq('a[data-bi-name="Support Uri"]').attr('href')
        self.result['rating'] = self.pq('div[itemprop="ratingValue"]').text()+' - '+self.pq('div[itemprop="ratingCount"]').text()
        
        if not offline:
            if num_reviews > 0:
                self.result['reviews'] = self.__get_reviews(self.result['app_id'], num_reviews)
            else:
                self.result['reviews'] = self.__get_reviews(self.result['app_id'])
        else:
            self.result['reviews'] = []
        self.result['languages'] = [x.text() for x in self.pq('dt:contains("Supported languages")').next().children().eq(0).children().items()]

        rows = []

        rows =  [
        {
        'Name': str(self.result['name']),'Store': str(self.result['store']), 'Price': self.result['price'],
        'App_Id':str(self.result['app_id']),'Store_Url':str(self.result['storeurl']),'Category':str(self.result['category']) , 
        'Icon': str(self.result['icon']), 'Screenshots': str(self.result['screenshots']), 'Description' :self.result['description'], 
        'Developer': str(self.result['developer']), 'contentRating': str(self.result['content_rating']) ,'Reviews': str(self.result['reviews']) ,
        'DevLink': str(self.result['devlink']), 'Rating' : str(self.result['rating']), 'Languages' : self.result['languages'], 'Permissions' : self.result['permissions']
        }
        ]

        service_account = 'naveed@apps-1149.iam.gserviceaccount.com'# Service account email       
        json_key = 'sevice_key.json'# JSON key provided by Google
        project_id = 'apps-1149'

        # Inserting data into table.
        client = get_client(project_id, json_key_file=json_key, readonly=False)
        self.done = client.push_rows('Temp', 'WindowsTest', rows, 'id')