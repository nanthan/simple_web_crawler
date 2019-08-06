import requests
import os
import codecs
from urllib.parse import urljoin
from urllib.parse import urlparse

seed_url = 'https://www.ku.ac.th/web2012/'
frontier_q = [seed_url]
visited_q = []

# @param 'links' is a list of extracted links to be stored in the queue


def enqueue(links):
    global frontier_q
    for link in links:
        if link not in frontier_q and link not in visited_q:
            frontier_q.append(link)

# FIFO queue


def dequeue():
    global frontier_q
    current_url = frontier_q[0]
    frontier_q = frontier_q[1:]
    print('{:d} left in queue'.format(len(frontier_q)))
    return current_url


def get_page(url):
    headers = {
        'User-Agent': 'webcrawler-01',
        'From': '<contact_email>'
    }
    text = ''
    try:
        r = requests.get(url, headers=headers, timeout=2)
        text = r.text
    except(KeyboardInterrupt, SystemExit):
        raise
    except:
        print('GET PAGE ERROR!')
    return text.lower()


def link_parser(raw_html):
    urls = []
    pattern_start = '<a href="'
    pattern_end = '"'
    index = 0
    length = len(raw_html)
    while index < length:
        start = raw_html.find(pattern_start, index)
        if start > 0:
            start = start + len(pattern_start)
            end = raw_html.find(pattern_end, start)
            link = raw_html[start:end]
            if len(link) > 0:
                if link not in urls:
                    urls.append(link)
            index = end
        else:
            break
    return urls


def save_file(raw_html, current_url):
    # Create (sub)directories with the 0o755 permission
    # @param 'exist_ok' is True for no exception if the target directory already exists
    base_path = './html/'
    url_parse = urlparse(current_url)
    host = base_path + url_parse[1]  # netloc
    path = url_parse[2]  # path
    abs_path_file = host + path
    abs_path = abs_path_file[:abs_path_file.rfind("/")]
    file_name = abs_path_file[abs_path_file.rfind("/"):]
    os.makedirs(abs_path, 0o755, exist_ok=True)

    # Write content into a file
    if file_name == '/':  # when not have a path of a file, suppose that file is index.html
        abs_path_file = abs_path + '/index.html'
    f = codecs.open(abs_path_file, 'w', 'utf-8')
    f.write(raw_html)
    f.close()


#--- main process ---#
max_number = 10000
for i in range(max_number):
    if (len(frontier_q) == 0):
        break
    current_url = dequeue()
    print('#{:05d} current_url: {:s}'.format(i+1, current_url))
    visited_q.append(current_url)
    raw_html = get_page(current_url)
    if raw_html != '':  # check have body from get_page before process below
        save_file(raw_html, current_url)
        extracted_links = link_parser(raw_html)
        for j in range(len(extracted_links)):
            extracted_links[j] = urljoin(current_url, extracted_links[j])
        url_ok = []
        for link in extracted_links:
            if ('http://' in link or 'https://' in link) and ('ku.ac.th' in link) and ('htm' in link):
                url_ok.append(link)
        enqueue(url_ok)
