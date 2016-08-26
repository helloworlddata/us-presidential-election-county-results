import argparse
import csv
from csv import DictReader, DictWriter
from loggy import loggy
from pathlib import Path
from sys import stdout
csv.field_size_limit(100000000)
LOGGY = loggy("collate")

COLLATED_HEADERS = [
    'year',
    'state', 'county', 'fips',
    'vote_rep', 'vote_dem', 'vote_oth', 'vote_total',
    'pct_rep', 'pct_dem', 'pct_oth',
    'winner', 'runnerup',
    'pct_winner', 'margin_winner_over_runnerup']

YEARS = ['2004', '2008', '2012']


def collate_year_file(year, infile, fipsfile, omit_wkt):
    fipslookup = dict(list(csv.reader(fipsfile )))
    data = {}
    for r in DictReader(infile):
        row = {k: v.strip() for k, v in r.items()}
        d = {'year': year}
        d['state'] = row['STATE']
        if d['state'] == 'AK':  # Alaska doesn't have counties, just legislative districts
            d['fips'] = 'AKL' + row['FIPS'][3:]
        else:
            d['fips'] = row['FIPS']
        d['county'] = row['COUNTY']

         # screw this:
#        d['county'] = fipslookup.get(d['fips']) or row['COUNTY']

        if year in ['2004', '2008']:
            d['vote_total'] = int(float(row['TOTAL_VOTE'])) if row['TOTAL_VOTE'] else None
            d['vote_dem'] =   int(float(row['VOTE_DEM']))if row['VOTE_DEM'] else None
            d['vote_rep'] =   int(float(row['VOTE_REP']))if row['VOTE_REP'] else None
            d['vote_oth'] =   int(float(row['VOTE_OTH']))if row['VOTE_OTH'] else None
            d['pct_dem'] = round(float(row['PERCENT_DE']), 2) if row['PERCENT_DE'] else None
            d['pct_rep'] = round(float(row['PERCENT_RE']), 2) if row['PERCENT_RE'] else None
            d['pct_oth'] = round(float(row['PERCENT_OT']), 2) if row['PERCENT_OT'] else None

        elif year == '2012':
            d['vote_total'] = int(float(row['TTL_VT'])) if row['TTL_VT'] else None
            d['vote_dem'] =   int(float(row['OBAMA']))  if row['OBAMA'] else None
            d['vote_rep'] =   int(float(row['ROMNEY'])) if row['ROMNEY'] else None
            d['vote_oth'] =   int(float(row['OTHERS'])) if row['OTHERS'] else None
            d['pct_dem'] = round(float(row['PCT_OBM']) , 2) if row['PCT_OBM'] else None
            d['pct_rep'] = round(float(row['PCT_ROM']) , 2) if row['PCT_ROM'] else None
            d['pct_oth'] = round(float(row['PCT_OTHR']), 2) if row['PCT_OTHR'] else None


        # apparently when multiple rows exist, their vote total is set to None?
        if d['vote_total']:

            standings = [(k[4:], d[k]) for k in ['pct_dem', 'pct_rep', 'pct_oth'] if d[k]]
            # some geographies are empty...
            if standings:
                standings.sort(key=lambda x: x[1], reverse=True)
                d['winner'] = standings[0][0]
                d['runnerup'] = standings[1][0]
                d['pct_winner'] = standings[0][1]
                d['margin_winner_over_runnerup'] = round(standings[0][1] - standings[1][1], 2)

            if not omit_wkt:
                d['wkt'] = row['WKT']

            # So some files have multiple results for the same FIPS
            # because of the way multi-shapefiles need to be attached...
            xd = data.get(d['fips'])
            if xd:
                if d['vote_total'] == xd['vote_total']:
                    # already recorded
                    pass
                else:
                    raise TypeError("Unexpected differences: \n%s\n%s" % (d, xd))
            else:
                data[d['fips']] = d

    datavals = sorted(list(data.values()), key=lambda x: (x['year'], x['fips']))
    return datavals


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Reads election data CSV and converts to standardized columns")
    parser.add_argument('year', type=str, help="Year to download from: %s" % ','.join(YEARS))
    parser.add_argument('infile', type=argparse.FileType('r'), help="File to read from")
    parser.add_argument('fipsfile', type=argparse.FileType('r'), help="File with standardized fips lookups")
    parser.add_argument('--omit-wkt',  action='store_true', help="Leave out the WKT geodata")

    args = parser.parse_args()
    year = args.year
    if year not in YEARS:
        raise IOError("Year must be within: %s" % YEARS)

    LOGGY.info("Reading: %s" % args.infile.name)

    headers = COLLATED_HEADERS if args.omit_wkt else COLLATED_HEADERS + ['wkt']
    csvout = DictWriter(stdout, fieldnames=headers)
    csvout.writeheader()

    for row in collate_year_file(year, args.infile, args.fipsfile, args.omit_wkt):
        csvout.writerow(row)


