import argparse
from io import BytesIO
from loggy import loggy
from pathlib import Path
import requests
from sys import stdout
import tarfile

LOGGY = loggy('fetch_data')

SRC_URLS = {
    '2004': 'http://dds.cr.usgs.gov/pub/data/nationalatlas/elpo04p020_nt00334.tar.gz',
    '2008': 'http://dds.cr.usgs.gov/pub/data/nationalatlas/elpo08p020_nt00335.tar.gz',
    '2012': 'http://dds.cr.usgs.gov/pub/data/nationalatlas/elpo12p010g.shp_nt00887.tar.gz',
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Downloads and unpacks election data from usgs.gov")
    parser.add_argument('year', type=str, help="Year to download from: %s" % ','.join(SRC_URLS.keys()))
    parser.add_argument('extdir', type=str, help="Existing directory to extract to")
    args = parser.parse_args()
    year = args.year
    dest_dir = Path(args.extdir)
    if year not in SRC_URLS.keys():
        raise IOError("Year argument must be: %s" % ', '.join(SRC_URLS.keys()))
    elif not dest_dir.is_dir():
        raise IOError("%s must be an existing directory" % dest_dir)

    url = SRC_URLS[year]
    LOGGY.info("Downloading: %s" % url)
    resp = requests.get(url)
    with tarfile.open(fileobj=BytesIO(resp.content), mode='r:gz') as tfile:
        for f in tfile.getmembers():
            srcname = Path(f.name)
            destname = dest_dir / (year + ''.join(srcname.suffixes))
            LOGGY.info("Saving %s as %s" % (srcname, destname))
            tbytes = tfile.extractfile(f).read()
            destname.write_bytes(tbytes)

