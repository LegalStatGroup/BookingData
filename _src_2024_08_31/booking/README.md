# Local Crime News Scrape

This is booking data for approximately 143 agencies state-wide. Includes arrest statutes, arresting agency and race.

This involves two steps: (1) Get a list of all arrest records. (2) Get the details of each record.

## (1) Get a list of all arrest records.  

There are two ways to do this (a search or a iterate through all records).  Seach can be by city or agency (or name).  I started with city (before discovering agency).  Preference is by agency.  The only place completed is San Jose City.  Will need to go back and check San Jose agencies at the end.

This is the very slow part because all results are generated on the server or involve a redirect.  I've used two strategies: scrape with python and scrpe with the webscraper extension.  Since additional threads don't speed this up, I'm mostly using the scraper so that i have machines for individual records.


I'm using two methods.  
### 1. Create a list of links to visit for async requests

    ├── a. Get a list of all results in the database from https://www.localcrimenews.com/welcome/citylist
    │       └── cityList_sync.py
    │           └──> [citiesList.json, citiesResultCount.json, citiesResultCount.csv]
    │       └── agencyList_async.py
    │           └──> [citiesList.json, citiesResultCount.json, citiesResultCount.csv]
    │    
    ├── b. For each city, get the number of records and the number of pages
    │       └── cityScrape.py
    │           ├──> city_result.text
    │           └──> cities_counts.json
    └── c. Calculate county totals to prioritize
            └── cityScrape.py
                └──> cities_counts.csv

### Notes:

1. There are cities in the results that do not have a city page, which I cannot explain. I'm gonna assume, since they show up in results, these cities will show up in results?
2. I'm going to prioritize the counties with the most records to scrape in counties of interest.
3. There are three ways to async scrape this data:

   a. Using City Pages

   1. Scrape all pages from each city, get a list of records
      > > > df['total_pages'].sum() = 822,915
   2. Scrape each record for details from the links on each city page
      > > > df['total_records'].sum() = 16,446,169
      > > > So we don't get every record with this method

   16446169 + 882915 = 17,329,084 record calls

   b. Scrape each record individually by iterating through the pages

   LA City is the most records (and thus probably the most frequent reporting). They also seem to have been in the dataset since the beginning (see wayback)
   Very recent record: 'https://www.localcrimenews.com/welcome/detail/88554001/yazmin-a-amaya-gonzalez-arrest.html'
   Very early record: 'https://www.localcrimenews.com/welcome/detail/59070097/fernando-jimenez-arrest.html'
   88554001 - 59070097 = 29,483,904 record calls
   Thats nearly twice method 1, but get every record
   Databse reports 18,842,489 arrests. So 63.9% of requests should return a record (not bad)

4. Seeing last results frome each city requires registration (sela@g, TrN1!)

**Try method 2 and if it's too slow, move to method 1.**


## (2) Get the details of each record.

**Webscraper or PY CSV ──> List of links to get (sometimes kept in raw HTML, sometimes single text file) ──> Individual Records (sometimes kept in raw HTML, sometimes single text file)**


SanJose (City): {
   "Search Results": {
      "method": "Both,
      "naming": "data/cities/SanJose/san-jose_{dddd}.html"
      "records": 152
   },
   "List of Links": {
      "method": "PY",
      "naming": "data/cities/SanJose/SanJose_links_to_scrape.txt"
      'records': 1
   },
   "Individual Records": {
      "method": "PY",
      "naming": "{UID}.html (deleted)"
      "records": 320000
   }
   "Record Cleaning": {
      "method": "CleanRecords.py",
      "naming": ["data/cities/SanJose/sanJose_fullArrests_{ddd}.csv", "data/cities/SanJose/sanJose_previousArrests_{ddd}.csv]
      "records": [33,33]
   }
}
   Webscraper + Python CSV done, about 320k individual records done
SanBernardino (City) Webscraper done
Butte (Sheriff) Webscraper done

