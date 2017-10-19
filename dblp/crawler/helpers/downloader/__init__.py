import requests
import sys
import os
import re

ua = "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)"
session = requests.session()
session.headers = {
    'User-Agent': ua,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip, deflate',
}


def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()  # As suggested by Rom Ruben


def format_filename(name):
    return re.sub('[:,\'\!\@#\$\%\^&\*\(\)\/]', '', name.lower()).replace(' ', '_')


class DownloadHelper(object):

    def __init__(self, source, session, path, reload=False):
        self.source = source
        self.session = session
        self.path = path
        self.reload = reload
        if not os.path.exists(path):
            os.makedirs(path)

    def _get_filepath(self, filename):
        return os.path.join(self.path, filename)

    def download(self, url, filename):
        if url is None:
            print "url is none skip file: {}".format(filename)
            return None
        fp = self._get_filepath(filename)
        if os.path.exists(fp) and not self.reload:
            print "exist file: {}, skip donwload.".format(fp)
            return filename
        r = self.session.get(url, stream=True)
        total_length = int(r.headers['content-length'])
        print "downloading ", filename
        with open(fp, 'wb') as f:
            cnt = 0
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    cnt += 1024
                    progress(cnt, total_length,
                             "downloading from [%s]" % (self.source))
        print("")
        return filename

    def download_simple(self, title, pdf_url, slides_url=None, bib_text=None):
        if title is None:
            print "title is empty."
            return None
        if type(title) is list:
            if len(title) != 0:
                title = title[0].strip()
            else:
                print "title is empty."
                return None

        filename_prefix = format_filename(title)
        self.download(pdf_url, filename_prefix + ".pdf")
        self.download(slides_url, filename_prefix + "_slides.pdf")
        if bib_text and type(bib_text) is str:
            bibp = self._get_filepath(filename_prefix + '.bib')
            with open(bibp, 'w') as fout:
                fout.write(bib_text)

        return title

    def run(self, filepath):
        if not os.path.exists(filepath):
            print "{} not exist.".format(filepath)
        else:
            with open(filepath, "r") as fin:
                for url in fin.xreadlines():
                    if url.strip() is "" or url.startswith("#"):
                        continue
                    self.parse(url)

    def parse(self, url):
        raise NotImplementedError()
