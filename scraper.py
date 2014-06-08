import scraperwiki
import re
import smtplib
import lxml.html
import lxml.etree
import mechanize
import sys, traceback

#username = 'no_spam@geetricks.com'
#password = 'pass'
#server = 'mail.geetricks.com'
#sender = 'no_spam@geetricks.com'
#receivers = ['mooparmghor@gmail.com']
#message = ''

def getData(source):
    title = ''
    bookURL = ''
    ISBN = ''
    ISBN_13 = ''
    Publisher = ''
    Binding = ''
    Edition = ''
    DatePublished = ''
    AvailableQuantity = ''
    Price = ''
    Authors = ''
    source = source.replace('\r', '').replace('\n', '')
    source = source.replace('\n', '')
    matchObj = re.findall('<td\salign="left"\svalign="top">.+?</td>', source)
    for match in matchObj:
        if 'Publisher' in match:
            match = match.replace('\t','')
            matchObj2 = re.search('<a\shref="(.+?)"><strong>(.+?)</strong></a>', match)
            if matchObj2:
                bookURL = 'http://www.alibris.com' + matchObj2.group(1).strip() #------------------>2
                title = matchObj2.group(2).strip() #---------------------------------------------------->3
            matchObj3 = re.findall('<a\s.+?/isbn/.+?>(\d+)</a>', match)
            for isbnMatch in matchObj3:
                temp = isbnMatch.strip()
                if len(temp) == 13:
                    ISBN_13 = temp #-------------------------------------------------------------------->4
                else:
                    ISBN = temp #-------------------------------------------------------------------->5
            publisherMatcher = re.search('Publisher:</strong>(.+?)<strong>', match)
            if publisherMatcher:
                Publisher = publisherMatcher.group(1).strip()#-------------------------------------------------------------------->6
            bindingMatcher = re.search('Binding:</strong>(.+?)<strong>', match)
            if bindingMatcher:
                Binding = bindingMatcher.group(1).strip()#-------------------------------------------------------------------->7
            editionMatcher = re.search('Edition:</strong>(.+?)<strong>', match)
            if editionMatcher:
                Edition = editionMatcher.group(1).strip()#-------------------------------------------------------------------->8
            datePublishedMatcher = re.search('<strong>Date\spublished:</strong>(.+?)<strong>', match)
            if datePublishedMatcher:
                DatePublished = datePublishedMatcher.group(1).strip()#-------------------------------------------------------------------->9
            AvailableQuantityMatcher = re.search('<strong>Available\sqty:</strong><em>(.+?)</em>', match)
            if AvailableQuantityMatcher:
                AvailableQuantity = AvailableQuantityMatcher.group(1).strip()#----------------------------------------------->10
            priceMatcher = re.search('price:\s?<em>(.+?)</em></strong>', match)
            if priceMatcher:
                Price = priceMatcher.group(1).strip()#-------------------------------------------------------------------->11
            authorMatcher = re.search('<p>by(.+?)<', match)
            if authorMatcher:
                Authors = authorMatcher.group(1).strip()#-------------------------------------------------------------------->12
            data = {}
            data.update({'ISBN': ISBN, 'title': title,
                         'ISBN_13': ISBN_13, 'Publisher': Publisher, 'Binding': Binding,
                         'Edition': Edition, 'DatePublished': DatePublished, 'AvailableQuantity': AvailableQuantity,
                         'Price': Price,'Authors': Authors, 'bookURL': bookURL})
            scraperwiki.sqlite.save(unique_keys=['ISBN'], data=data)

#Prepare the browser
start_url = 'http://www.alibris.com/stores/nebbooks/search?qtopic=%22Qualifying+Textbooks%22&qprice=4.50&mtype=A&qpricehi=200&browse=1&noworks=1&matches=500&qsort=pr'
br = mechanize.Browser()
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
br.set_handle_robots(False)

#Get the first Page
br.open(start_url)
pageSource = br.response().read()
getData(pageSource)


#Scraping loop
nextUrl =''
while True:
    for ddd in br.links(text_regex='Next'):
        if 'href' in ddd.attrs[0]:
            nextUrl = 'http://www.alibris.com' + ddd.attrs[0][1]
            print nextUrl

    if nextUrl == '':
        break
    else:
        br.open(nextUrl)
        pageSource = br.response().read()
        nextUrl = ''
        getData(pageSource)

#After the end of the loop file the scraperwiki data here.

#if adsFound:
#    try:
#       smtpObj = smtplib.SMTP(server)
#       smtpObj.login(username, password)
#       smtpObj.sendmail(sender, receivers, message)
#       print "Successfully sent email"
#    except:
#       print "Error: unable to send email"
#       traceback.print_exc(file=sys.stdout)
