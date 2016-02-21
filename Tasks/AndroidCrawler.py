# pip install pyopenssl --target=libs
# pip install pyquery --target=libs
# pip install requests --target=libs
# pip install google-apy-client-python --target=libs

import requests
import pyquery
import json
import codecs
import itertools
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from bigquery import get_client
#from androidCrawler import requests, pyquery, json
 

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

class AndroidCrawler(BaseCrawler):

    @staticmethod
    def __get_permissions(app_id):
        techurl = 'https://play.google.com/store/xhr/getdoc?authuser=0&hl=en'
 
        html = requests.post(techurl, data={'ids': app_id,'xhr': 1}).text

        try:
            data = json.loads(html[4:]
                              .replace(',,', ',0,')
                              .replace(',,', ',0,')
                              .replace('[,', '[0,')
            )
        except:
            print(html)
            exit(1)

        perms = []
        # magic begins
        data = data[0][2][0]
        data = next(x for x in data if isinstance(x, dict))
        data = data['42656262'][1]
        for perm in data[0]:
            if not perm[1]:
                perms.append('In-app purchases')
            else:
                for x in perm[1]:
                    perms.append(x[0])
        for perm in data[1][0][1]:
            perms.append(perm[0])
        # magic ends
        return perms

    @staticmethod
    def __get_reviews(app_id, num_pages=112):
        if num_pages > 112:
            num_pages = 112  # Google Play only returns 112 pages of reviews (0 through 111)
        reviews = []
        for page in range(num_pages):
            html = requests.post('https://play.google.com/store/getreviews?authuser=0&hl=en', data={
                'id': app_id,
                'reviewType': 0,
                'pageNum': page,
            })
           # with open(html.text, 'r', encoding='utf8') as f:
            #    s = f.read()
            #pq = pyquery.PyQuery(s)
            s = codecs.decode(html.text, 'unicode_escape').encode('utf8').decode()
            pq = pyquery.PyQuery(s)

            for review in pq('div.single-review').items():
                extracted_data = {}
                extracted_data['date'] = review.find('span.review-date').text()
                extracted_data['authorname'] = review.find('span.author-name').text()
                extracted_data['rating'] = review.find('div.tiny-star').attr('aria-label')
                extracted_data['title'] = review.find('span.review-title').text()
                extracted_data['text'] = review.find('div.review-body:not(span)').children().remove().end().text()
                reviews.append(extracted_data)

        return reviews
    def isdone(self):
        return self.done

    def retry(self):
        if self.ret > 0:
            self.ret -= 1
            return True
        return False

    def __init__(self, url, num_reviews=5):
        # set num_reviews to -1 to scrape everything
        #super().__init__(url)
        super(AndroidCrawler, self).__init__(url)
        self.done = False
        self.ret = 3

        self.result['name'] = self.pq('.document-title').text()
        self.check()
        self.result['store'] = 'Google Play'
        price = self.pq('span[itemprop="offers"] [itemprop="price"]').attr('content')
        if price == '0':
            price = 'Free'
        self.result['price'] = price
        self.result['app_id'] = url.split('id=')[1].split('&')[0]
        self.result['storeurl'] = url
        category = self.pq('a.document-subtitle.category')
        if category.length == 2:
            subcategory = category.eq(1).text()
        elif category.length == 1:
            subcategory = ''
        else:
            raise Exception('Something wrong with categories')
        self.result['category'] = category.eq(0).text()
        self.result['subcategory'] = subcategory
        self.result['icon'] = self.pq('.cover-container').children().attr('src')
        self.result['screenshots'] = [x.attr('src') for x in self.pq('.screenshot').items()]
        self.result['description'] = self.pq('.id-app-orig-desc').text()
        self.result['description'] = self.pq('div[itemprop="description"]').text()
        
        
        
        #print self.result['description'] 
        print "kam ban gya he "
        self.result['downloads'] = self.pq('div[itemprop="numDownloads"]').text()
        if not offline:
            self.result['permissions'] = self.__get_permissions(self.result['app_id'])
        else:
            self.result['permissions'] = []

        self.result['developer'] = self.pq('.primary').text()
        self.result['contentRating'] = self.pq('.meta-info.contains-text-link > .content').eq(0).text()
        try:
            self.result['developerWebsite'] = self.pq('.dev-link').attr('href').split('q=')[1].split('&')[0]
        except:
            self.result['developerWebsite'] = 'Nothing'
        siblings = self.pq('.dev-link')
        found = siblings.eq(1).text()
        
        if siblings.eq(2).text() == 'Privacy Policy' :
            self.result['DeveloperPrivacyPolicy'] = siblings.eq(2).attr('href')
            self.result['physicalAddress']=self.pq('div.content.physical-address').text()
        else :  
            self.result['physicalAddress']=self.pq('div.content.physical-address').text()
            self.result['DeveloperPrivacyPolicy']="Not Given"
        self.result['whatsNew'] = self.pq('div.recent-change').text()
        self.result['developerEmail'] = found
        
        if not offline:
            print "Getting Reviews"
            if num_reviews > 0:
                self.result['reviews'] = self.__get_reviews(self.result['app_id'], num_reviews)
            else:
                self.result['reviews'] = self.__get_reviews(self.result['app_id'])
        else:
            self.result['reviews'] = []
        self.result['version'] = self.pq('div[itemprop="softwareVersion"]').text()
        self.result['updated'] = self.pq('div[itemprop="datePublished"]').text()

        try:
            self.result['rating'] = self.pq('div[itemprop="ratingValue"]').text()+' - '+self.pq('div[itemprop="ratingCount"]').text()
        except:
            self.result['rating'] = '0'
        self.result['installations'] = self.pq('div[itemprop="numDownloads"]').text()
        self.result['LastUpdateDate'] = self.pq('div[itemprop="datePublished"]').text()
        self.result['AppSize'] = self.pq('div[itemprop="fileSize"]').text()
        self.result['MinimumOSVersion'] = self.pq('div[itemprop="operatingSystems"]').text()
        
        #self.result['contentRating'] = self.pq('div[itemprop="contentRating"]').text()
        ratingReason = self.pq('.meta-info.contains-text-link > .content').eq(1).text()
        if (ratingReason == 'Learn more'):
            self.result['RatingReason'] = ''
        else:
            self.result['RatingReason'] = ratingReason

        ratingText = self.pq('div[itemprop="aggregateRating"]').text().split(' ')
        self.result['ratingValue'] = ratingText[0]
        self.result['ratingCount'] = ratingText[1]
        #print self.result['AppSize']
        #print self.result['LastUpdateDate']
        #print self.result['installations']
        #print self.result['MinimumOSVersion']
        #print  self.result['contentRating'] 
        #print self.result['developerWebsite']
        #print self.result['developerEmail']
        #print self.result['physicalAddress']
        #print self.result['whatsNew']
        
        isfree = False 
        if self.result['price'] == 0:
            isfree=True 

        project_id = 'apps-1149'
        new_reviews= []
        new_reviews = self.result['reviews']
        #print new_reviews[1]['date']

        service_account = 'naveed@apps-1149.iam.gserviceaccount.com'# Service account email       
        json_key = 'sevice_key.json'# JSON key provided by Google


        # Inserting data into table.
        client = get_client(project_id, json_key_file=json_key, readonly=False)
        
        price = str(self.result['price'])
        if price == "Free":
            price_in_rupees = 0
        else :
            price_in_rupees= float(price[2:])
       
        
        rows = []

        try:
            rows =  [
            {
            'Name': str(self.result['name']),'Store': str(self.result['store']), 'Price': price_in_rupees, 'IsFree': isfree ,
            'App_Id':str(self.result['app_id']),'Store_Url':str(self.result['storeurl']),'Category':str(self.result['category']) , 
            'subCategory':str(self.result['subcategory']) , 'Icon': str(self.result['icon']), 'Screenshots': str(self.result['screenshots']), 
            'Description' :self.result['description'], 'Downloads':str(self.result['downloads']), 'Permissions': str(self.result['permissions']), 
            'Developer': str(self.result['developer']), 'contentRating': str(self.result['contentRating']) , 
            'developerWebsite': str(self.result['developerWebsite']) ,'Reviews': str(self.result['reviews']) ,'reviewDate':str(new_reviews[0]['date']) ,
            'reviewTitle': str(new_reviews[1]['title']) , 
            'reviewTexts' :str(new_reviews[1]['text']), 'Version' : str(self.result['version']),'Updates': str(self.result['updated']), 'Rating' : str(self.result['rating']), 
            'appSize':self.result['AppSize'], 'lastUpdateDate': self.result['LastUpdateDate'] , 'installations': self.result['installations'], 
            'MinimumOSVersion': self.result['MinimumOSVersion'], 'developerEmail': self.result['developerEmail'], 'whatsNew': self.result['whatsNew'],
            'physicalAddress': self.result['physicalAddress'], 'RatingReason' : self.result['ratingReason'], 'RatingCount' : self.result['ratingCount'],
            'RatingValue' : self.result['ratingValue']
            }
            ]
        except:
            rows =  [
            {
            'Name': str(self.result['name']),'Store': str(self.result['store']), 'Price': price_in_rupees, 'IsFree': isfree ,
            'App_Id':str(self.result['app_id']),'Store_Url':str(self.result['storeurl']),'Category':str(self.result['category']) , 
            'subCategory':str(self.result['subcategory']) , 'Icon': str(self.result['icon']), 'Screenshots': str(self.result['screenshots']), 
            'Description' :self.result['description'], 'Downloads':str(self.result['downloads']), 'Permissions': str(self.result['permissions']), 
            'Developer': str(self.result['developer']), 'contentRating': str(self.result['contentRating']), 
            'developerWebsite': str(self.result['developerWebsite']) ,'Reviews': str(self.result['reviews']), 
            'Version' : str(self.result['version']),'Updates': str(self.result['updated']), 'Rating' : str(self.result['rating']), 
            'appSize':self.result['AppSize'], 'lastUpdateDate': self.result['LastUpdateDate'] , 'installations': self.result['installations'], 
            'MinimumOSVersion': self.result['MinimumOSVersion'], 'developerEmail': self.result['developerEmail'], 'whatsNew': self.result['whatsNew'],
            'physicalAddress': self.result['physicalAddress']
            }
            ]

        self.done = client.push_rows('Temp', 'AndroidTest', rows, 'id')

#print "success"