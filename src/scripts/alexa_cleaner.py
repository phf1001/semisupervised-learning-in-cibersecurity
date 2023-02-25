# pushd src/scripts && python3 alexa_cleaner.py && popd

import requests
from html import unescape
from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException
import csv
import os
import sys
src_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.append(src_path)
from phishing_fvg.phishing_utils import get_alexa_sites, get_data_path


if __name__ == '__main__':
    working_urls = []
    urls = get_alexa_sites()

    for url in urls:

        for protocol in ['https://', 'http://']:
            try:
                url = protocol + url
                request_content = requests.get(url, headers={
                                            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'},
                                            timeout=15,
                                            ).content
                html = unescape(request_content.decode("utf-8", errors='ignore'))
                soup = BeautifulSoup(html, "lxml")
                [s.decompose() for s in soup("script")]

                if soup.body is not None:
                    body_text = soup.body.get_text()

                    if detect(body_text) in ['es', 'en']:
                        print(url)
                        working_urls.append([url])

            except (requests.exceptions.RequestException, LangDetectException):
                pass

    output_file = get_data_path() + os.path.sep + 'alexa_filtered_urls.csv'
    with open(output_file, mode='w') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)

        for url in working_urls:
            writer.writerow(url)

    f.close()
