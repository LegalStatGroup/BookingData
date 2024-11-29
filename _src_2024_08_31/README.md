# Local Crime News Scrape

This is booking data for approximately 143 agencies state-wide. Includes arrest statutes, arresting agency and race.

This involves two steps:

1. Get a list of all agencies and number of results by piggybacking on the exploited keys. This part requires a password. ──>

   ```
   "ScrapeTEMPLATE\src\agencies\agencyResultCount.json" :

   "SanJose (City)": {
      "Search Results": {
      "method": "Both,
      "naming": "data/cities/SanJose/san-jose*{UID}.html"
      "records": 152
         },
   ```

List of links to get (sometimes kept in raw HTML, sometimes single text file) ──>

```
"naming": "data/cities/SanJose/all_links.txt" : [
   https://www.localcrimenews.com/welcome/detail/24399162/cortland-quilling-arrest.html
   https://www.localcrimenews.com/welcome/detail/24526935/khanh-do-arrest.html
   https://www.localcrimenews.com/welcome/detail/24526944/long-bui-arrest.html
   ]
```

2. Got to each agency and run through every page getting the UID URLS ──>
   List of links to get (sometimes kept in raw HTML, sometimes single text file) ──>
   Scrape Individual Records (sometimes kept in raw HTML, sometimes single text file)

## (1) Get a list of all arrest records for async requests.

There are two ways to do this (a search or a iterate through all records). Seach can be by city or agency (or name). I started with city (before discovering agency). Best method seems to be by agency.

This is the very slow part because all results are generated on the server or involve a redirect. I've used two strategies: scrape with python and scrape with the webscraper extension. Since additional threads don't speed this up, I'm mostly using the scraper so that I have machines for individual records.

## (2) Get the details of each record with async requests and UIDs.

"Record Cleaning": {
"method": "CleanRecords.py",
"naming": ["data/cities/SanJose/sanJose_fullArrests*{ddd}.csv", "data/cities/SanJose/sanJose*previousArrests*{ddd}.csv]
"records": [33,33]
}
}
Webscraper + Python CSV done, about 320k individual records done
SanBernardino (City) Webscraper done
Butte (Sheriff) Webscraper done

### Notes:

1. There are cities in the results that do not have a city page, which I cannot explain. I'm gonna assume, since they show up in results?

2. I'm going to prioritize the counties with the most records to scrape in counties of interest.

3. There are three ways to async scrape this data:

   1. Scrape all pages returned from each city or agency result list, then scrape each record individually.
      > > > df['total_pages'].sum() = 822,915
      > > > Since not every city has a page, this might mean we don't get every record with queries
      > > > df['total_records'].sum() = 16,446,169
      > > > This is gonna take a really long time, and is much more likely to throw errors.

   16446169 + 882915 = 17,329,084 record calls 2. Scrape each record individually by iterating through the page UIDs.

   > > > This is gonna take a really long time, but is more likely to get every record.
   > > > LA City is the most records (and thus probably the most frequent reporting). They also seem to have been in the dataset since the beginning (see wayback) {Very recent record: 'https://www.localcrimenews.com/welcome/detail/88554001/yazmin-a-amaya-gonzalez-arrest.html' Very early record: 'https://www.localcrimenews.com/welcome/detail/59070097/fernando-jimenez-arrest.html'}

   df['total_records'].sum() = 88554001 - 59070097 = 18,842,489
   88554001 - 59070097 = 29,483,904 record calls
   Thats a bunch more records, but get every record
   Databse reports 18,842,489 arrests. So 63.9% of requests should return a record (not bad)

   > > > UPDATE: It throws a bad connection very frequently, making this method also unreliable. I'm going to try the first method and see if it's faster.

4. Seeing last results frome each city requires registration (sela@g, TrN1!)

## (2) Get the details of each record.

he only place completed is San Jose City. Will need to go back and check San Jose agencies at the end.

├── 1. Get a list of all results in the database
│ By City: https://www.localcrimenews.com/welcome/citylist
│ └── "cityList_sync.py": "Code to scrape city result pages"
│ ├──> "cityList.json": ""List of cioty result listing urls" ,
│ ├──> "cities.json": "City names"
│ ├──> "citiesResultCount.json": "City URLS and count of retruned results"
│ └──> "citiesResultCount.csv": "City URLS and count of retruned results"
│ By Agency: https://www.localcrimenews.com/welcome/agencylist
│ └── "agencyList_async.py" : "Code to scrape agency result pages"
│ ├──> "agencyList.csv" : "List of agency result listing urls"
│ ├──> "agencies.json" : "Agency names"
│ ├──> "agencyResultCount_sorted.json" : "Agency URLS and count of retruned results"
│ ├──> "agencyResultCount.json" : "Agency URLS and count of retruned results"
│ ├──> "agencyList_async.py" : "Code to scrape agency result pages"
│ └──> "agencyCrosswalk.xlsx" : "Crosswalk of agency names and URLs"
│
├── 2. For each agency, scrape all records pages
│ └── cityScrape.py
│ ├──> city_result.text
│ └──> cities_counts.json
└── c. Calculate county totals to prioritize
└── cityScrape.py
└──> cities_counts.csv
