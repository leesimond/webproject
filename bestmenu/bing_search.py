import json
import urllib.request, urllib.parse, urllib.error
from bestmenu.bing_key import *

def run_query(search_terms):
    root_url = 'https://api.datamarket.azure.com/Bing/Search/'
    source = 'Web'

    results_per_page = 10
    offset = 0

    query = "'{0}'".format(search_terms)
    query = urllib.parse.quote(query)

    search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(
            root_url,
            source,
            results_per_page,
            offset,
            query)

    username = ''

    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, search_url, username, BING_API_KEY)

    results = []

    try:
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        opener = urllib.request.build_opener(handler)
        urllib.request.install_opener(opener)

        response = urllib.request.urlopen(search_url).read().decode('utf-8')

        json_response = json.loads(response)

        for result in json_response['d']['results']:
            results.append({
            'title': result['Title'],
            'link': result['Url'],
            'summary': result['Description']})

    except urllib.error.URLError as e:
        print("Error when querying the Bing API: ", e)
    
    return results

def main():
    query = input('Enter search query: ')
    run_query(query)

if __name__ == '__main__':
    main()
