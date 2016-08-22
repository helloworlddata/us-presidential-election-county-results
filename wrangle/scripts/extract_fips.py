"""
Given one of the election CSV files, creates a simple CSV list of
FIPS code to human-readable name
"""

import argparse
import csv
from csv import DictReader
from loggy import loggy
from pathlib import Path
from sys import stdout
csv.field_size_limit(100000000)
LOGGY = loggy("extract_fips")



if __name__ == '__main__':
    parser = argparse.ArgumentParser("Reads election data CSV and converts to standardized columns")
    parser.add_argument('infile', type=argparse.FileType('r'), help="File to read from")

    args = parser.parse_args()

    LOGGY.info("Reading: %s" % args.infile.name)

    csvout = csv.writer(stdout)
    uniquepairs = set([(row['FIPS'], row['COUNTY'], row['STATE']) for row in DictReader(args.infile)])
    for row in sorted(list(uniquepairs), key=lambda x: x[0]):
        fips, county, state = row
        if state == 'AK':
            # need to change 02010 to AKL10
            fips = 'AKL' + fips[3:]
        csvout.writerow([fips, county])


