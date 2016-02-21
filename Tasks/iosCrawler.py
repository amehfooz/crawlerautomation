import requests
import pyquery
import json
import codecs
import itertools
import re
from iosCrawler import requests, pyquery, json

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

    def __init__(self, url):
        #super().__init__(url)
        super(IOsCrawler, self).__init__(url)
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
        print self.result['languages'] + "\n"
        print self.result['updated']+ "\n"
        print self.result['version_history']+ "\n"
        print self.result['version']+ "\n"
        print self.result['name']+ " \n"
        print self.check()
        print self.result['store']+ " \n"
        print self.result['price']+ " \n"
        print self.result['app_id']+ " \n"
        print self.result['storeurl']+ " \n"
        print self.result['category']+ " \n"
        print self.result['content_rating']+ " \n"
        print self.result['icon']+ " \n"
        print self.result['screenshots']
        print self.result['description'] + " \n"
        print self.result['developer'] + " \n"
        print temp
        print self.result['current_version_rating']+ " \n"
        print self.result['rating']+ " \n"
        print self.result['reviews']
        print extracted_data['authorname'] + " \n"
        print extracted_data['rating'] + " \n" 
        print extracted_data['title']+ " \n " 
        print extracted_data['text']+ "\n"
        print self.result['reviews']  
offline=0
url = "https://itunes.apple.com/us/app/pop-the-lock/id979100082?mt=8&v0=WWW-NAUS-ITSTOP100-FREEAPPS&l=en&ign-mpt=uo%3D4"
IOsCrawler(url)
offline=0
count = 0

'''
from bigquery import get_client
# Insert data into table.
rows =  [
    {'id': 'NzAzYmRiA','one': 'ein', 'two': 'zwei'},
    {'id': 'NzAzYmRiB', 'one': 'uno', 'two': 'dos'},
    {'id': 'NzAzYmRiC', 'one': 'Aik', 'two': 'Dooo'} 
]
inserted = client.push_rows('Temp', 'TestingPython', rows, 'id')'''