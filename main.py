#!/usr/bin/python3
from urllib.parse import urlparse
from urllib.request import urlopen, Request
import sys
from googlesearch import search 
from bs4 import BeautifulSoup
import argparse
import ssl
from collections import defaultdict

ssl.match_hostname = lambda cert, hostname: True

def search_keyword(args):
    return search(args.keyword, tld="com", num=args.results, stop=args.results, pause=0, user_agent=args.user_agent, country="country" + args.country)
    
def extract_domain_from_url(url):
    url_base = urlparse(url).netloc
    if url_base.startswith("www"):
        return '.'.join(url_base.split('.')[1:])
    else:
        return url_base

def find_external_links(url, user_agent):
    base_domain = extract_domain_from_url(url)
    external_links = defaultdict(list)
    try:
        request = Request(url, headers={'User-Agent': user_agent})
        html = urlopen(request).read()
    except:
        print("Error accessing url:%s" % url)
        return external_links

    soup = BeautifulSoup(html, features="html.parser")
    links = soup.find_all('a')
    for tag in links:
        link = tag.get('href',None)
        if link is not None:
            external_domain = extract_domain_from_url(link)
            if should_add_link(link, base_domain, external_domain):
                external_links[external_domain].append(link)
    return external_links


def should_add_link(url, base_domain, external_domain):
    if url.startswith("http") and not external_domain.endswith(base_domain):
        return True
    return False

def print_results(results, args):
    if len(results.keys()) == 0:
        print("Nothing found :/")
    for url, domains in results.items():
        link_count = sum([len(domain) for domain in domains.values()])
        domain_count = len(domains.keys())
        print("URL:{:<50s} DOMAIN COUNT:{:<20d} LINK_COUNT:{:<20d}".format(url, domain_count, link_count))  
        if args.print_domains:
            for domain, external_links in domains.items():
                print("DOMAIN:{:<50s} LINK_COUNT: {:<20d}".format(domain, len(external_links)))
                
        elif args.print_all:
            for domain, external_links in domains.items():
                print("DOMAIN:{:<50s} LINK_COUNT: {:<20d}".format(domain, len(external_links)))
                print(*external_links, sep='\n')
            
def configure_argument_parser():
    argument_parser = argparse.ArgumentParser(description='Return external link count of given keys google search result urls')
    argument_parser.add_argument('keyword', 
            metavar='keyword', 
            type=str,
            help='search keyword')

    argument_parser.add_argument('--results',
            metavar='results',
            type=int,
            choices=range(1,20),
            default=2,
            help='number of results to be returned')

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

    argument_parser.add_argument("--print-domains", 
            help="print links with counts", 
            action = "store_true")

    argument_parser.add_argument("--print-all", 
            help="print full tree", 
            action = "store_true")
    return argument_parser

if __name__ == "__main__":
    
    argument_parser = configure_argument_parser()
    args = argument_parser.parse_args()

    response = search_keyword(args)

    results = {}
    for url in response:
        external_links_of_url = find_external_links(url, args.user_agent)
        results[url] = external_links_of_url
    print_results(results, args)



