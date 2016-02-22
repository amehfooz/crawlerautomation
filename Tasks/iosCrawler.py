import requests
import pyquery
import json
import codecs
import itertools
import re
import requests, pyquery, json
from bigquery import get_client


offline=0

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


class IOsCrawler(BaseCrawler):
    def isdone(self):
        return self.done

    def retry(self):
        print self.retries[self.url]

        if self.retries[self.url] > 0:
            self.retries[self.url] -= 1
            return True
        return False
        
    def __init__(self, url):
        #super().__init__(url)
        super(IOsCrawler, self).__init__(url)

        self.done = False
        self.url = url
        
        if url not in self.retries:
            self.retries[url] = 3

        pq = self.pq
        self.result['name'] = pq('h1').text()
        self.check()
        self.result['store'] = 'Apple App Store'
        self.result['price'] = pq('.price').text()
        self.result['app_id'] = re.search('/(id\d+)', url).group(1)
        self.result['storeurl'] = url
        self.result['category'] = pq('span[itemprop="applicationCategory"]').text()
        self.result['content_rating'] = pq('.app-rating').text()
        self.result['icon'] = pq('img.artwork').attr('src-swap')
        self.result['screenshots'] = [x.attr('src') for x in pq('img.portrait').items()]
        self.result['description'] = pq('p[itemprop="description"]').text()
        self.result['developer'] = pq('span[itemprop="name"]').text()
        temp = pq('div.rating[aria-label*="Ratings"]')
        self.result['current_version_rating'] = temp.eq(0).attr('aria-label')
        self.result['rating'] = temp.eq(1).attr('aria-label')
        self.result['reviews'] = []
        for review in pq('.customer-review').items():
            extracted_data = {}
            extracted_data['authorname'] = review.find('span.user-info').text().split(' ')[-1]
            extracted_data['rating'] = review.find('div.rating').attr('aria-label')
            extracted_data['title'] = review.find('span.customerReviewTitle').text()
            extracted_data['text'] = review.find('p.content').text()
            self.result['reviews'].append(extracted_data)
        self.result['version'] = pq('span[itemprop="softwareVersion"]').text()
        self.result['version_history'] = pq('div.product-review > p').eq(1).text()
        self.result['updated'] = pq('span[itemprop="datePublished"]').text()
        self.result['languages'] = pq('li.language').find('span').remove().end().text()
       
        rows = []

        rows =  [
        {
        'Name': str(self.result['name']),'Store': str(self.result['store']), 'Price': self.result['price'],
        'App_Id':str(self.result['app_id']),'Store_Url':str(self.result['storeurl']),'Category':str(self.result['category']) , 
        'Icon': str(self.result['icon']), 'Screenshots': str(self.result['screenshots']), 'Description' :self.result['description'], 
        'Developer': str(self.result['developer']), 'contentRating': str(self.result['content_rating']) ,'Reviews': str(self.result['reviews']) ,
        'Updated': str(self.result['updated']), 'Rating' : str(self.result['rating']), 'VersionHistory' : self.result['version_history'],
        'Languages' : self.result['languages'], 'CurrentVersionRating' : self.result['current_version_rating'], 'Version' : str(self.result['version'])
        }
        ]

        service_account = 'naveed@apps-1149.iam.gserviceaccount.com'# Service account email       
        json_key = 'sevice_key.json'# JSON key provided by Google


        # Inserting data into table.
        client = get_client(project_id, json_key_file=json_key, readonly=False)
        self.done = client.push_rows('Temp', 'AppStoreTest', rows, 'id')