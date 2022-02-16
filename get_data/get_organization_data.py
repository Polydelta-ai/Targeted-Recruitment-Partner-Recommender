import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import sys

data_dictionary = {
    'org_name': [],
    'org_url': [], 
    'state':[],
    'city':[], 
    'zip':[], 
    'bio':[], 
    'member_count':[], 
    'staff_count':[], 
    'year_founded':[], 
    'budget':[],
    'type':[]
    }

# Base Url that list all orgs on each page
state_codes = [ 'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
           'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
           'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
           'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
           'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
# page will just increment each time until no more results.
# For each org on the base link visit their directory page
    # on the page extract the info and create a dictionary to end up with a csv in the end.
    # {org_name: [], state:[], zip:[], bio:[],member_count:[], staff_count:[],year_founded:[],budget:[],type:[]}
for state_code in state_codes:
    page_no = 1
    start = time.time()
    while page_no > 0:
        base_url = 'https://directoryofassociations.com/browse.asp?dp='+str(page_no)+'&n=&s='+state_code+'&c=&z=&t1=&g=&m='
        page = requests.get(base_url)
        soup = BeautifulSoup(page.content, "html.parser") #from the page text I need to return the td href=view...
        page_results = soup.find_all("tr", class_="") # get all the search results on a page
        print(f'current state {state_code}, current page {page_no}')
        if page_results:
            for page_result in page_results:
                # then with that href value build the link to the directory page https://directoryofassociations.com/ + href value
                
                org_href = page_result.find('a')['href']
                org_name = page_result.find('a').find('strong').text
                data_dictionary['org_name'].append(org_name)

                org_dir_url = 'https://directoryofassociations.com/' + org_href
                org_dir_page = requests.get(org_dir_url)
                org_dir_soup = BeautifulSoup(org_dir_page.content, "html.parser")

                org_url = org_dir_soup.find('div', class_='jumbotron').find('h2').text
                data_dictionary['org_url'].append(org_url)

                #Get address block
                org_address = org_dir_soup.find('div', class_='jumbotron').find('p')

                org_address_locality = org_address.find('span',itemprop='locality').text
                data_dictionary['city'].append(org_address_locality)

                org_address_region = org_address.find('span',itemprop='region').text# don't need to scrape since we loop based on state code..
                data_dictionary['state'].append(state_code)

                org_address_zip = org_address.find('span',itemprop='postal-code').text
                data_dictionary['zip'].append(org_address_zip)

                org_bio = org_dir_soup.find('div', class_='col-md-12').find('p').text
                data_dictionary['bio'].append(org_bio)

                org_info_summary = org_dir_soup.find_all('div', class_='row')[1].find_all('span')
                try:
                    data_dictionary['member_count'].append(org_info_summary[0].text)
                except:
                    data_dictionary['member_count'].append('')

                try:
                    data_dictionary['year_founded'].append(org_info_summary[1].text)
                except:
                    data_dictionary['year_founded'].append('')
                
                try:
                    data_dictionary['staff_count'].append(org_info_summary[2].text)
                except:
                    data_dictionary['staff_count'].append('')
                
                try:
                    data_dictionary['budget'].append(org_info_summary[3].text)
                except:
                    data_dictionary['budget'].append('')
                
                try:
                    data_dictionary['type'].append(org_info_summary[5].text)
                except:
                    data_dictionary['type'].append('')
            page_no+=1
            pd.DataFrame(data_dictionary).to_csv('data/'+state_code+'_organization_data.csv',index=False)
            
        else:
            # reached end of search results reset page_no
            end = time.time()
            print(f'Scraping {state_code} took {(end-start)/60.} minutes.')
            break
    

    
