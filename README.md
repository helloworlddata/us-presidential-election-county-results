# Presidential General Election Results by County

This repo contains U.S. presidential election results __by county__ for the years 2004, 2008, and 2012. This data comes from the National Atlas of the United States / U.S. Geological Survey and was published on Data.gov.

(Note: I think the FIPS for 2012 are off. Will email Data.gov about it)

(Update: here's a gist to reproduce the discrepancies https://gist.github.com/dannguyen/2de0fcd2ba3100b4698cd5af6ae61754)

This repo is part of a larger data collection project so I haven't finished writing my notes and methodology, or even double-checked the data. But the data from Data.gov is pretty straightforward, with 2012 having slightly different fieldnames. The scripts in this repo show how I reconciled the 3 datasets into one CSV:

[data/us-presidential-election-county-results-2004-through-2012.csv](data/us-presidential-election-county-results-2004-through-2012.csv)

Here's a sample small enough to browse on Github's site:

[data/samples/new-hampshire-counties.csv](data/samples/new-hampshire-counties.csv)

I've added a few conveniences for data analysis. Besides the raw vote count and percentages/totals for Republican, Democratic, and "Other", I created columns for `winner`, `runnerup`, `pct_winner`, and `margin_winner_over_runnerup`, to make it easy to write concise queries, such as listing the top 10 counties with over 10,000 votes, in which the 2008 winning candidate's party was different than in 2004, ranked by the total change in margin of victory (in percentage points):


```
|--------+-------------------+--------+--------------|
|  state | county            | winner | totes_swing  |
|--------+-------------------+--------+--------------|
|  GA    | Rockdale County   | dem    | 31.1         |
|  IN    | Tippecanoe County | dem    | 30.8         |
|  TX    | Cameron County    | dem    | 29.9         |
|  IL    | Kendall County    | dem    | 29.6         |
|  VA    | Harrisonburg City | dem    | 29.4         |
|  IN    | Delaware County   | dem    | 28.8         |
|  TX    | Val Verde County  | dem    | 28.4         |
|  ND    | Cass County       | dem    | 27.5         |
|  KY    | Floyd County      | rep    | 26.5         |
|  IN    | Madison County    | dem    | 25.9         |
|--------+-------------------+--------+--------------|
```


If you're too tired to point-and-click download it and import into SQL, here's an example using **curl** and [**csvkit**](https://csvkit.readthedocs.io/en/540/) from the command-line:


```sh
  
curl \
      https://raw.githubusercontent.com/dataofnote/us-presidential-election-county-results/master/data/us-presidential-election-county-results-2004-through-2012.csv \
  | csvsql --query \
      "SELECT y2008.state, y2008.county, 
              y2008.winner,
             ROUND(y2004.margin_winner_over_runnerup + 
                   y2008.margin_winner_over_runnerup, 1) AS totes_swing
      FROM 
          (SELECT * FROM stdin WHERE year = 2004) AS y2004  
      INNER JOIN 
          (SELECT * FROM stdin WHERE year = 2008) AS y2008
          ON y2004.fips = y2008.fips
      WHERE 
        y2004.winner != y2008.winner
        AND y2008.vote_total > 10000
      ORDER BY 
        totes_swing DESC
      LIMIT 10;" \
  | csvlook
```






## Caveats

TK obv.

There seems to be errors in the 2012 data. They may have come from my scripts. But I think they may be in the source data. For example, querying for all counties that switched from 2004 to 2008, but __then switched back in 2012__, ranked by the cumulative swing in percentage points for the victor in 2008 and 2012:


```
|--------+-------+-------------------------+--------+--------------|
|  fips  | state | county                  | winner | totes_swing  |
|--------+-------+-------------------------+--------+--------------|
|  51683 | VA    | Manassas City           | rep    | 104.2        |
|  AKL08 | AK    | Legislative District 08 | rep    | 45.5         |
|  37117 | NC    | Mcdowell                | rep    | 36.4         |
|  17117 | IL    | Marshall                | rep    | 24.1         |
|  49035 | UT    | Salt Lake               | rep    | 20.4         |
|  42047 | PA    | Elk                     | rep    | 20.3         |
|  17115 | IL    | Marion                  | rep    | 20.2         |
|  49043 | UT    | Summit                  | rep    | 20.0         |
|  42021 | PA    | Cambria                 | rep    | 18.7         |
|  26027 | MI    | Cass                    | rep    | 17.8         |
|--------+-------+-------------------------+--------+--------------|
```

I think the Manassas City contains a faulty data point in its 2012 entry, which may be related to how Manassas City didn't really exist in 2004. As for that Alaskan district, as I mention in the caveats, the votes are counted by legislative district, which may have been redrawn.

As for "Mcdowell" county in North Carolina, it seems to have been given the wrong FIPS. Its FIPS should be 37111, not 37117. Marshall County also has a FIPS error. And probably the rest of them, too.

TK: Will email Data.gov about this.


Here's the query I ran:


~~~sh

curl https://raw.githubusercontent.com/dataofnote/us-presidential-election-county-results/master/data/us-presidential-election-county-results-2004-through-2012.csv \
    | csvsql --query \
      "SELECT y2012.fips, y2012.state, y2012.county, 
              y2012.winner,
             ROUND(y2012.margin_winner_over_runnerup + 
                   y2008.margin_winner_over_runnerup, 1) AS totes_swing
      FROM 
          (SELECT * FROM stdin WHERE year = 2004) AS y2004  
      INNER JOIN 
          (SELECT * FROM stdin WHERE year = 2008) AS y2008
          ON y2004.fips = y2008.fips
      INNER JOIN 
          (SELECT * FROM stdin WHERE year = 2012) AS y2012
          ON y2004.fips = y2012.fips 
             AND y2004.winner = y2012.winner
      WHERE       
        y2004.winner != y2008.winner
        AND y2008.vote_total > 10000
      ORDER BY 
        totes_swing DESC
      LIMIT 10;"   \
    | csvlook
~~~






The other big caveat is what I mentioned above; for Alaska, votes aren't tabulated by county, but by legislative district (which may have been redistricted over time). The `fips` column has a non-FIPS value to make that obvious (e.g. `AKL05`). 


### Shapefiles


The shapefile data from the USGS has been stripped in the downloadable files before, since (non-LFS) Github doesn't allow for files 100MB+. But it's pretty straightforward to join them up with the USGS data, which is linked to below. Or you could clone this repo and attempt to run the [Rakefile](Rakefile), which has been 100% tested to work on my personal laptop and whatever the f--k I have installed.


Below are the URLs to the Data.gov pages and the field names.

## 2004

http://catalog.data.gov/dataset/2004-presidential-general-election-county-results-direct-download

      1: OBJECTID
      2: AREA
      3: PERIMETER
      4: EL2004P020
      5: STATE
      6: COUNTY
      7: FIPS
      8: STATE_FIPS
      9: VOTE_DEM
     10: VOTE_REP
     11: VOTE_OTH
     12: PERCENT_DE
     13: PERCENT_RE
     14: PERCENT_OT
     15: SYMBOL_COD
     16: TOTAL_VOTE



## 2008

https://catalog.data.gov/dataset/2008-presidential-general-election-county-results-direct-download

      1: OBJECTID
      2: AREA
      3: PERIMETER
      4: EL2004P020
      5: STATE
      6: COUNTY
      7: FIPS
      8: STATE_FIPS
      9: VOTE_DEM
     10: VOTE_REP
     11: VOTE_OTH
     12: PERCENT_DE
     13: PERCENT_RE
     14: PERCENT_OT
     15: SYMBOL_COD
     16: TOTAL_VOTE


## 2012


https://catalog.data.gov/dataset/presidential-general-election-results-2012-direct-download


      1: STATE
      2: STATE_FIPS
      3: COUNTY
      4: FIPS
      5: OBAMA
      6: ROMNEY
      7: OTHERS
      8: TTL_VT
      9: PCT_OBM
     10: PCT_ROM
     11: PCT_OTHR
     12: WINNER
     13: PCT_WNR
     14: group


