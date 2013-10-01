'''
 download vote data from http://clerk.house.gov/evs/2013/index.asp
 
 Questions to investigate:
 * Who are the most active/inactive representatives? By vote? By days active?
 * Are there any "followers?" Look for reps who don't always vote, but when they
 * do their vote falls in line with another rep
 * How do reps cluster? Are there any reps who are difficult to categorize?
 * Can we build a predictive model that can infer how each rep will vote based on
 # how the other reps voted?
    * Collaborative Filter / Naive Bayes
    * Features:
        * sponsor state
        * sponsor party
        * bill categories

    TO DO:        
    * wrap all GET requests in try/except handlers
    * Convert code to use 'requests' just for fun?
    * build database dump procedures
''' 

# Main URL, will need to page through old roll calls
#URL = http://clerk.house.gov/evs/2013/index.asp

from urllib2 import urlopen
from xml.dom import minidom
from time import sleep
from db_api import flush_rollcall

#try:
#    from BeautifulSoup import BeautifulSoup ### Code actually breaks on bs3, minidom can't handle html entities
#except:
from bs4 import BeautifulSoup

def rollURL(rollcall, year):
    ch = len(str(rollcall))
    x = (3-ch)
    if x > 0:
        rollcall = '0'*x + str(rollcall)    
    return "http://clerk.house.gov/evs/{YEAR}/roll{ROLLCALL}.xml".format(YEAR=year, ROLLCALL=rollcall)

def yearURL(year, page):
    return "http://clerk.house.gov/evs/{YEAR}/ROLL_{PAGE}00.asp".format(YEAR=year, PAGE=page)
    
URL = "http://clerk.house.gov/evs/2013/roll398.xml"

def scrape_rollcall(rc_num, yr=2013):
    """
    Scrape voting records from the congressional clerks office, 
    by roll call.
    """
    response_text = GET_url(rollURL(rc_num, yr))
    xmldoc = minidom.parseString(response_text)
    recorded_votes = xmldoc.getElementsByTagName('recorded-vote')
    votes = []
    for rv in recorded_votes:
        legislator = rv.getElementsByTagName('legislator')[0]
        vote = rv.getElementsByTagName('vote')[0].firstChild.data
        
        party = legislator.attributes['party'].value
        lname = legislator.attributes['unaccented-name'].value
        state = legislator.attributes['state'].value
        id    = legislator.attributes['name-id'].value
        votes.append([id, lname, state, party, vote])
    return votes

def scrape_bill_details(bill_url):
    """Scrapes details page for specific peice of legislation"""
    #pass
    response = GET_url(bill_url)
    soup = BeautifulSoup(response)
    def extract(tag, SOUP=soup):
        try:
            out = [sub['content'] for sub in SOUP.findAll('meta', {'name':tag})]
        except:
            out=None
        return out
    results = {}
    results['subjects'] = extract('dc.subject')
    results['title'] = extract('dc.title')
    results['sponsor'] = extract('dc.creator')
    results['date'] = extract('dc.date')
    results['descr'] = extract('dc.description')
    return results

def scrape_record(rc_num, yr, bill_url):
    """ 
    Scrapes congressional voting records and associated details pages for bills,
    dumps to a database.
    """
    votes = scrape_rollcall(rc_num, yr)
    if bill_url:
        details = scrape_bill_details(bill_url)
        result = [votes, details]
    else:
        result = [votes]
    ## need to push stuff to a database in here. ##
    #flush_rollcall(db_push, rc_num, yr) 
        # this is really where the dump should be
        # but I stoopidly coded it based on the output datatype of scraping a full year
    return result

def GET_url(URL, multiplier=2):
    """simple wrapper for GET requests to provide exponential backoff"""
    successful = False
    backoff=1
    while not successful:
        try:
            response = urlopen(URL).read()
            successful=True
        except Exception, e:
            print e
            print "backing off for %d" % backoff
            sleep(backoff)
            backoff*=multiplier
    return response

def scrape_year(year):
    """Scrapes all records associated with a given year."""
    # I need a better "fail" test than this
    failtext = (u'\n\tOffice of the Clerk of the U.S. House of Representatives - 404\n'
               ,'\r\n\tOffice of the Clerk of the U.S. House of Representatives - 404\r\n')
    page=0
    rolls_year = {}
    while True:
        URL = yearURL(year, page)
        print URL
        response = GET_url(URL)        
        soup = BeautifulSoup(response)
        print soup.title.getText()
        if soup.title.getText() in failtext or page>1000:
            break
        
        records=soup.findAll('tr')[1:] # skip header row.
        ##record_map={0:'roll',1:'date',2:'issue',3:'question',4:'result',5:'title'}        
        for ix, r in enumerate(records):            
            rec = minidom.parseString(str(r))
            fields = rec.getElementsByTagName('td')
            
            #billurl = fields[0].firstChild.attributes['href']
            rc_num  = fields[0].firstChild.firstChild.nodeValue
            date    = fields[1].firstChild.firstChild.nodeValue # I think we'll get a better date string out of the rollcall xml. This is "DD-Mmm" format
            print year, page, ix, rc_num
            print fields[2].toxml()
            try:
                billDetailsURL = fields[2].getElementsByTagName('a')[0].attributes['href'].nodeValue
                issue   = fields[2].getElementsByTagName('a')[0].firstChild.nodeValue # exs: "JOURNAL", "H RES 146"
            except IndexError:
                billDetailsURL = None
                try:
                    issue   = fields[2].getElementsByTagName('font')[0].firstChild.nodeValue # exs: "JOURNAL", "H RES 146"
                except AttributeError:
                    issue = None
            try:
                question = fields[3].firstChild.firstChild.nodeValue
            except AttributeError:
                question = None
            try:
                result = fields[4].firstChild.firstChild.nodeValue
            except AttributeError:
                result = None
            try:
                descr = fields[5].firstChild.firstChild.nodeValue
            except AttributeError:
                descr = None
            
            rolls_year[rc_num] = {'date':date, 'issue':issue, 'question':question, 'result':result, 'description':descr}
            # write to database 
            ############# <--- need to add DB dump code
            # scrape roll call and bill details
            result = scrape_record(rc_num, year, billDetailsURL)
            rolls_year[rc_num]['votes'] = result[0]
            try:
                rolls_year[rc_num].update(result[1])
            except IndexError:
                pass
            except TypeError:
                pass
        page+=1
    # this is sort of a weird place to put this, but I coded it up based
    # on the output of scrpaing a full year
    for rc in rolls_year.keys():
        flush_rollcall(rolls_year[rc],int(rc), year)
    return rolls_year

def run_once():
    """
    Scrapes all available roll calls from 1990 to present to build
    a database of historical roll calls. I recommend running this 
    when congress is not in session. 
    """
    # After building the historical database, an RSS reading script 
    # should be set up to track legislative activities as they happen. 
    # Alternatively, I could reparameterize this script to scrape every
    # few minutes and stop when it's hit a roll call it's seen before
    # (which I suppose is basically what an RSS reader will be doing 
    # anyway). In any event, the preference would be for near-live
    # data updates for visualization purposes.
    year = int(raw_input("Current Year: "))
    results = {}
    while year > 1989:
        results[year] = scrape_year(year)
        year -= 1
    return results