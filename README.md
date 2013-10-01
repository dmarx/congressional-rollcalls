# Congressional Rollcalls Scraper

## Overview

This repo consists of a sqlite database of congressional rollcalls scraped from
the THOMAS database: http://thomas.loc.gov/home/rollcallvotes.html

THOMAS goes back to 1990, but the HTML changed in 2003 so the database only
goes back that far for now. Also, this is only congressional rollcalls: I 
haven't scraped the senate yet. 

In addition to the rollcall votes, the database includes some basic details on 
each bill, specifically the bill's sponsorand asociated "subject" tags.

## Database

The .db file is too large for github (172 MB) so I'm currently hosting it on 
Google Drive: 

https://docs.google.com/file/d/0B3O2JrGmy0OKVldkTDZDR3l4TzQ/edit?usp=sharing

Last scraped the morning of 10/1/2013 (date of government shutdown), approximately 6am.

The schema is based on the organization of the data as presented by THOMAS, and
is not normalized. I'll probably ETL to a more compact architecture in the near
future, at which time it's possible I'll be able to host it here.

Check the file simple_db.sql for the general schema. It should be pretty 
self-explanatory.

## Scraper Usage

```
import scrape_roll_calls as s
s.run_once() # Will prompt user to input year to start scraping at. 
             # Works backwards from that year.
```

My intention is to update this tool in the futures so it will monitor new votes
periodically much like the NYT roll call live updated data graphic: 
http://politics.nytimes.com/congress/votes/113/house/1/502

At present, it only dumps to the database after scraping a full year's worth of
votes.

## Requirements

BeautifulSoup4

## License

The voting records are public domain so obviously do what you want with the 
database. Not mine to license. Feel free to do what you want with the code as 
well. Consider the lack of a license file in this repo as an invitation to use 
my code however you like.