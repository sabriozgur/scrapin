#!/usr/bin/python3
from urllib.parse import urlparse
from urllib.request import urlopen, Request
import sys
from googlesearch import search 
from bs4 import BeautifulSoup
import argparse
import ssl
ssl.match_hostname = lambda cert, hostname: True

def search_keyword(args):
    return search(args.keyword, tld="com", num=10, stop=10, pause=0, user_agent=args.user_agent, country="country" + args.country)
    
def extract_domain_from_url(url):
    url_base = urlparse(url).netloc
    if url_base.startswith("www"):
        return '.'.join(url_base.split('.')[1:])
    else:
        return url_base

def find_external_links(url, domain, user_agent):
    external_links = []
    try:
        request = Request(url, headers={'User-Agent': user_agent})
        html = urlopen(request).read()
    except:
        print("Error accessing url:%s" % url)
        return []

    soup = BeautifulSoup(html, features="html.parser")
    links = soup.find_all('a')
    for tag in links:
        link = tag.get('href',None)
        if link is not None:
            external_links.append(link)
    return filter_external_links(external_links, domain)

def filter_external_links(urls, domain):
    external_links = []

    for url in urls:
        extracted_domain = extract_domain_from_url(url)
        if url.startswith("http") and not extracted_domain.endswith(domain):
            external_links.append(url)
    return external_links

def print_results(external_links, link_flag):
    for domain, links in external_links.items():
        print(domain, len(links))
        if link_flag:
            for link in links:
                try:
                    print(link)
                except:
                    print("hello")
                    pass #some urls contain non printable characters, we skip printing them

if __name__ == "__main__":
    # Create the parser
    argument_parser = argparse.ArgumentParser(description='Return external link count of given keys google search result urls')

# Add the arguments
    argument_parser.add_argument('keyword', 
            metavar='keyword', 
            type=str,
            help='search keyword')

    argument_parser.add_argument('--domain',
            metavar='domain_count',
            type=int,
            choices=range(1,6),
            default=2,
            help='unique domain count to be returned')

    argument_parser.add_argument('--country',
            metavar='country_code',
            type=str,
            default="TR",
            help='two character country code')
    
    argument_parser.add_argument('--user-agent',
            metavar='user_agent',
            type=str,
            default="Mozilla/5.0 (Linux; Android 7.0; SM-G610M Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Mobile Safari/537.36",
            help='http user agent string')

    argument_parser.add_argument("--print-links", 
            help="print links with counts", 
            action = "store_true")

    args = argument_parser.parse_args()

    response = search_keyword(args)

    domains = {}
    for result in response:
        domain = extract_domain_from_url(result)
        if domain not in domains:
            domains[domain] = result
        if len(domains.keys()) >= args.domain:
            break
    
    external_links = {}
    for domain, url in domains.items():
        external_links_of_domain = find_external_links(url, domain, args.user_agent)
        external_links[domain] = external_links_of_domain
    
    print_results(external_links, args.print_links)


