import os
import sys
from downloader.usenix import UsenixDowloader
from downloader.acm import ACMDowloader
from downloader import session

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "Usage: {} {}".format(sys.argv[0], "<url file>")
        sys.exit(-1)

    ud = UsenixDowloader(session=session, path="usenix")
    ad = ACMDowloader(session=session, path="acm")
    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print "{} not exist.".format(filepath)
    else:
        with open(filepath, "r") as fin:
            for url in fin.xreadlines():
                if url.strip() is "" or url.startswith("#"):
                    continue
                if "acm.org" in url:
                    ad.parse(url)
                elif "usenix.org" in url:
                    ud.parse(url)
