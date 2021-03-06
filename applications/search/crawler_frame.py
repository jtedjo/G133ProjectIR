import logging
from datamodel.search.JtedjoEthandsJdkang2_datamodel import JtedjoEthandsJdkang2Link, OneJtedjoEthandsJdkang2UnProcessedLink
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Producer, GetterSetter, Getter
from lxml import html,etree
import re, os
from time import time
from uuid import uuid4

from urlparse import urlparse, parse_qs, urljoin
from uuid import uuid4

# Additional Imports 
import bs4
import django
from django.conf import settings
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import tldextract
from datetime import datetime

settings.configure(DEBUG=True)
django.setup()

logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"

subdomainDictionary = dict() #keeps track how many links belongs to a particular subdomain have been checked/entered
count_link = 0 #current count of longest outlink
mostOutLinkURL = "" #current URL with most outlink

CALENDAR_REGEX = "^.*(c|C)alendar.*$"
WICS_REGEX = "^.*?afg.*$"
REPEAT_REGEX = "^.*?(/.+?/).*?\1.*$|^.*?/(.+?/)\2.*$"
EXTRA_DIRS_REGEX = "^.*(/misc|/sites|/all|/themes|/modules|/profiles|/css|/field|/node|/theme){3}.*$"

@Producer(JtedjoEthandsJdkang2Link)
@GetterSetter(OneJtedjoEthandsJdkang2UnProcessedLink)
class CrawlerFrame(IApplication):
    app_id = "JtedjoEthandsJdkang2"

    def __init__(self, frame):
        self.app_id = "JtedjoEthandsJdkang2"
        self.frame = frame
        self.starttime = time()


    def initialize(self):
        self.count = 0
        links = self.frame.get_new(OneJtedjoEthandsJdkang2UnProcessedLink)
        if len(links) > 0:
            print "Resuming from the previous state."
            self.download_links(links)
        else:
            l = JtedjoEthandsJdkang2Link("http://www.ics.uci.edu/")
            print l.full_url
            self.frame.add(l)

    def update(self):
        unprocessed_links = self.frame.get_new(OneJtedjoEthandsJdkang2UnProcessedLink)
        if unprocessed_links:
            self.download_links(unprocessed_links)

    def download_links(self, unprocessed_links):
        for link in unprocessed_links:
            print "Got a link to download:", link.full_url
            downloaded = link.download()
            links = extract_next_links(downloaded)
            for l in links:
                if is_valid(l):
                    self.frame.add(JtedjoEthandsJdkang2Link(l))

    def shutdown(self):
        global subdomainDictionary
        global count_link
        global mostOutLinkURL

        # writing the particular subdomains number of associated links
        file =open("subdomain.txt", "a+")
        for urlSubdomain in subdomainDictionary:
            file.write("subdomain name: "+ urlSubdomain +" subdomain count :%d" % subdomainDictionary.get(urlSubdomain))
        file.close()

        file2 = open("mostOutlink.txt", "a+")
        file2.write("URL with most outlink :" + mostOutLinkUrl + " with number of :%d" %count_link)
        file2.close()


        print (
            "Time time spent this session: ",
            time() - self.starttime, " seconds.")

def extract_next_links(rawDataObj):
    outputLinks = []
    #outfile = open("../../output"+ str(datetime.now()) +".txt", "w")
    '''
    rawDataObj is an object of type UrlResponse declared at L20-30
    datamodel/search/server_datamodel.py
    the return of this function should be a list of urls in their absolute form
    Validation of link via is_valid function is done later (see line 42).
    It is not required to remove duplicates that have already been downloaded. 
    The frontier takes care of that.
    
    Suggested library: lxml
    '''

    global subdomainDictionary
    global count_link
    global mostOutLinkURL
    #Extract links and add them to outputLinks
    contentSoup = bs4.BeautifulSoup(rawDataObj.content, "lxml")
    #incase the url is redirected, need to use different baseURL for the join
    if rawDataObj.is_redirected and len(rawDataObj.final_url) > 0:
        baseUrl = rawDataObj.final_url
    else:
        baseUrl = rawDataObj.url
    outputLinks = [urljoin(baseUrl,link['href']) for link in contentSoup('a') if 'href' in link.attrs]
    numLinks = len(outputLinks)
    #Extract subdomain of raw url
    subdomain = tldextract.extract(rawDataObj.url)[0] #Index '0' refers to subdomain attribute of the returned tuple

    if subdomain in subdomainDictionary:
        subdomainDictionary[subdomain] += 1;
    else:
        subdomainDictionary[subdomain] = 1;

    if (count_link < numLinks):
        count_link = numLinks
        mostOutLinkURL = rawDataObj.url;

    #outfile.close()
    #print outputLinks
    #for link in outputLinks:
    #    print "\t"+link

    # writing the particular subdomains number of associated links
    # file =open("subdomain.txt", "a+")
    # file.write("subdomain name: "+ urlSubdomain +" subdomain count :%d" % subdomainDictionary.get(urlSubdomain))

    return outputLinks

def is_valid(url):
    #print url
    '''
    Function returns True or False based on whether the url has to be
    downloaded or not.
    Robot rules and duplication rules are checked separately.
    This is a great place to filter out crawler traps.
    '''
    val = URLValidator()
    parsed = urlparse(url)
    if parsed.scheme not in set(["http", "https"]):
        #print "Returned false in first if block in is_valid"
        return False
    #Check if the url leads to a calendar, self-repeating directories, or superfluous directories
    if(re.match(CALENDAR_REGEX, url) or re.match(REPEAT_REGEX, url) or re.match(EXTRA_DIRS_REGEX, url) or re.match(WICS_REGEX, url)):
        #print "Returned false in the second if block in is_valid"
        return False
    try:
        val(url)
        returnVal = ".ics.uci.edu" in parsed.hostname \
            and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
            + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
            + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
            + "|thmx|mso|arff|rtf|jar|csv"\
            + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())
        if (returnVal == True):
            print "\t"+url
        return returnVal

    except TypeError:
        print ("TypeError for ", parsed)
        return False
    except ValidationError, e:
        print(e)
        return False

