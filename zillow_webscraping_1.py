# -*- coding: utf-8 -*-
"""Zillow_Webscraping_1.ipynb

**Webscraping of Zillow Housing data**
"""

from bs4 import BeautifulSoup as soup
import requests
import os
import json
import urllib
import pandas as pd
import numpy as np  # Handle missing data as np.nan/None
import datetime
from datetime import datetime
import re             # import the regular expressions library to search strings
import pytz # Helps retrieve timezone
# import seaborn as sns
# import matplotlib.pyplot as plt

# Pick city (default is Austin, TX)
city = 'Chicago'

if city == 'Austin':
    url_c = 'https://www.zillow.com/homes/Austin,-TX_rb/'
    # referer_value = 'https://www.zillow.com/austin-tx/?searchQueryState=%7B%22pagination'
elif city == 'New York':
    url_c = 'https://www.zillow.com/homes/New-York_rb/'
    # referer_value = 'https://www.zillow.com/homes/New-York_rb/?searchQueryState=%7B%22pagination'
elif city == 'Atlanta':
    url_c = 'https://www.zillow.com/homes/Atlanta,-GA_rb/'
    # referer_value = 'https://www.zillow.com/homes/Atlanta,-GA_rb/?searchQueryState=%7B%22pagination'
elif city == 'Los Angeles':
    url_c = 'https://www.zillow.com/homes/Los-Angeles,-CA_rb/'
elif city == 'Chicago':
    url_c = 'https://www.zillow.com/homes/Chicago,-IL_rb/'
elif city == 'Miami':
    url_c = 'https://www.zillow.com/homes/Miami,-FL_rb/'
elif city == 'Seattle':
    url_c = 'https://www.zillow.com/homes/Seattle,-WA_rb/'
elif city == 'Boston':
    url_c = 'https://www.zillow.com/homes/Boston,-MA_rb/'
elif city == 'Las Vegas':
    url_c = 'https://www.zillow.com/homes/Las-Vegas,-NV_rb/'
elif city == 'Washington DC':
    url_c = 'https://www.zillow.com/homes/Washington,-DC_rb/'
else: # default city
    url_c = 'https://www.zillow.com/homes/Austin,-TX_rb/'

# Dictionary for City & State
c_s = {'Atlanta': 'GA', 'Austin': 'TX', 'Boston': 'MA', 'Chicago': 'IL', 'Las Vegas': 'NV',
       'Los Angeles': 'CA', 'Miami': 'FL', 'New York': 'NY', 'Seattle': 'WA', 'Washington': 'DC'}
       
# Display message
if city in c_s.keys():
    print("Crawling real-estate listings data from Zillow for " + city + ", " + c_s[city])
    print("URL: " + url_c + "\n")
else:
    city = 'Austin'
    print("Crawling data from Zillow for " + city + ", " + c_s[city])
    print("URL: " + url_c + "\n")
    
# Header for get requests
header = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}

# Extract data for the first n pages
n = 20 # number of pages
zillow_pages = [requests.get(url=url_c + f"{i}_p/", headers=header) for i in range(1,n+1)]
print(zillow_pages) # Get the status code/response for each page
#-------------------------------------------------------------------------------

# Initialize an empty list to hold parsed HTML data using BeautifulSoup
bsobj = []

# Iterate through all pages and pass each page to BeautifulSoup
for j in range(0, len(zillow_pages)):
    bsobj.append(soup(zillow_pages[j].text, 'html.parser'))

#--------------------------------------------------------------------------------

#1. Get price of listings
def home_price(pages, soup):
    """
    Returns a list of all home prices per page
    """
    price_list = []

    # for each page
    for k in range(0,len(pages)): 
        # Get house prices on each page
        for price in soup[k].findAll('div', {'class':'list-card-price'}):
            home_cost = price.text
            # Drop the 'K' character which represents 1,000s
            if home_cost.__contains__('K'):
                home_cost = home_cost.replace("K",",000")
            elif home_cost.__contains__('+'): # drop the '+' towards the end
                home_cost = home_cost.strip("+")

            price_list.append(home_cost) # Push next house cost to the list

    return price_list
#-------------------------------------------------------------------------------

#2. Get the addresses
def home_address(pages, soup):
    """
    Returns a list of home addresses in each page
    """
    address_list = []

    # for each page
    for k in range(0,len(zillow_pages)):
        # Get addresses of homes on each page
        for adr in bsobj[k].findAll('address', {'class':'list-card-addr'}):
            # Store entire address string (Address + APT/UNIT, City, State Zipcode)
            add_details = adr.text;

            # Find the 1st comma and drop the city, state and zip code
            n = add_details.find(',')
            address_list.append(add_details[:n]) # Insert addresses into the list
      
    return address_list
#-------------------------------------------------------------------------------

#3. Extract state and city
def city_state(pages, soup):
    """
    Return separate lists for city and state
    """
    city_list = list()
    state_list = []

    # for each page
    for k in range(0, len(pages)):
        # Get city & state on each page
        for adr in soup[k].findAll('address', {'class':'list-card-addr'}):
            # Store entire address string (Address + APT/UNIT, City, State Zipcode)
            home_details = adr.text

            # Get the index of the comma after the house address
            m = home_details.find(',')

            # Search the listing details for city and state abreviation (City, ST)
            x = re.findall('[A-Z\sa-z]+\,\s[A-Z]+', home_details[m:])

            # If there are multiple matching strings drop the ones after the City, State
            if len(x) > 1:
                x.pop()

            if len(x) == 1:
                city_state_str = x[0]

                # Break up string to list separate city and state separately
                state = city_state_str[-2:]

                # Search for the 1st comma in this string and get the city
                n = city_state_str.find(',')
                city = city_state_str[:n].strip()

            else: # Handling missing data for later cleaning
                state = np.nan
                city = np.nan

            # Store in a list
            city_list.append(city)
            state_list.append(state)

    return city_list, state_list
#-------------------------------------------------------------------------------

#4. Get the Zip Code value
def zip_code(pages, soup):
    """
    Gets the Zip Codes of real-estate listings per page
    """
    zip_code = list()

    # Loop each page
    for k in range(0, len(pages)):
        # Get zip codes of home listings on each page
        for add in soup[k].findAll('address', {'class':'list-card-addr'}):
            home_details = add.text

            # Get the index of the comma after the house address
            m = home_details.find(',')

            # Search the listing details for 5 consecutive digits (0-9)
            x = re.findall('\s[0-9]+', home_details[m:])

            # Hold the string of formatted data and Zipcode is 5-digits
            if len(x) == 1:
                zip_code_str = x[0]

                # Compensate for the extra whitespace characters
                zip_code.append(zip_code_str.strip())

            else: # Handle missing data
                zip_code_str = np.nan
                zip_code.append(zip_code_str)

    return zip_code
#-------------------------------------------------------------------------------

#5. Get the number of beds
def bed_count(pages, soup):
    """
    For loop for # of bedrooms in each real-estate listing on each page
    """
    bed_count = []

    # for each page
    for k in range(0, len(pages)):
        # Get number of bedrooms per home in each page
        for bed in soup[k].findAll('ul', {'class':'list-card-details'}):
            # Extract the beds text: '# bds'/'# bd'
            bds = bed.findAll('abbr', {'class': "list-card-label"})
            # Get the bedroom, bathroom and area data
            num_bds = bed.findAll('li', {'class': ""})

            # Store the data for beds (index: 0)
            bds_data = num_bds[0].text

            # Use 'bd' since it's a substring of 'bds'
            if bds_data.__contains__('bd'):
                bed_count.append(bds_data[0])
            else: # Handle missing data
                bed_count.append(np.nan)

    return bed_count
#-------------------------------------------------------------------------------

#6. Get the number of baths
def bath_count(pages, soup):
    """
    For loop for # of bathrooms in each real-estate listing on each page
    """
    bath_count = []

    # Loop each page
    for k in range(0, len(pages)):
        # Get number of bathrooms per home in each page
        for bath in soup[k].findAll('ul', {'class':'list-card-details'}):
            # Extract the baths text: '# ba'
            ba = bath.findAll('abbr', {'class': "list-card-label"})
            # Get the bedroom, bathroom and area data
            num_ba = bath.findAll('li', {'class': ""})

            # Check HTML string in list as bedroom data could be missing
            if len(num_ba) != 1:
                ba_data = num_ba[1].text
            else:
                ba_data = '-' # bathroom data is not available

            if ba_data.__contains__('ba'): # Check for the 'ba' string
                bath_count.append(ba_data[0])
            else: # Handle missing data
                bath_count.append(np.nan)

    return bath_count
#-------------------------------------------------------------------------------

#7. Get the number of area of housing space
def area_sqft(pages, soup):
    """
    Returns the square foot area of each real-estate listing
    """
    area_sqft = []

    # loop each page
    for k in range(0, len(pages)):
        # Get the square footage of each house/apartment on each page
        for area in soup[k].findAll('ul',{'class': 'list-card-details'}):
            # Extract the square foot text: ' sqft'
            area_sq = area.findAll('abbr', {'class': "list-card-label"})
            # Get the bedroom, bathroom and area data
            num_sq = area.findAll('li', {'class': ""})

            # Check HTML string in list as bedroom & bathroom data could be missing
            if 0 < len(num_sq) <= 3: # contains at most all 3 criteria data
                sq_data = num_sq[-1].text
            else:
                sq_data = np.nan # bathroom data is not available

            # Verify if string contains 'sqft'
            if sq_data.__contains__(' sqft lo'): # Check for extraneous 'lo'
                area_sqft.append(sq_data.strip(' sqft lo'))
            elif sq_data.__contains__(' sqft'):
                area_sqft.append(sq_data.strip(' sqft'))
            else:
                area_sqft.append(np.nan)

    return area_sqft
#-------------------------------------------------------------------------------

#8. Get the status of the home/apartment listings
def home_status(pages, soup):
    """
    For loop for status of the home listings in each page
    """
    home_status = list()

    # loop each page
    for k in range(0, len(pages)): 
        # Get house status from each page
        for status in soup[k].findAll('li',{'class':'list-card-statusText'}):
          # Access the status field
          home_stat = status.text

          # Remove the extra '- ' characters that come with each record
          home_status.append(home_stat.strip('- '))

    return home_status
#-------------------------------------------------------------------------------

#9. Get the geographical coordinates of listings
def lat_long(pages, soup):
    """
    Returns the location of homes on each page: (latitude, longitude)
    """
    house_lat = []
    house_lon = []

    # loop each page
    for k in range(0, len(pages)): 
        # Get geographic location from each page
        for loc in soup[k].findAll('script', {'type': 'application/ld+json'}):
            # Information is stored in JSON string format; store it as an object (dict)
            loc_info = json.loads(loc.text)
            # Ignore multiple details in the extracted HTML file such as 'Events'
            if loc_info['@type'] == 'SingleFamilyResidence':
                # Get the position data
                if list(loc_info.keys()).__contains__("geo"): # missing data
                    geo_loc = loc_info["geo"]

                    if len(geo_loc.keys()) > 2:
                        # Get the latitude and longitude digits
                        lat_ = geo_loc["latitude"]
                        lon_ = geo_loc["longitude"]
                        # Append values to list
                        house_lat.append(lat_)
                        house_lon.append(lon_)
                    # If the keys are less than the expected 4: '@type', '@context', 'geo', & 'url'
                    else:
                        lat_ = np.nan
                        lon_ = np.nan
                        # Push result
                        house_lat.append(lat_)
                        house_lon.append(lon_)
                else: # If there's no "geo" tag
                    lat_ = np.nan
                    lon_ = np.nan
                    # Add result to list
                    house_lat.append(lat_)
                    house_lon.append(lon_)

    return house_lat, house_lon
#-------------------------------------------------------------------------------

#10. Get the listing ID of the home listings
def listing_id(pages, soup):
    """
    Returns the unique ID number for each listing uploaded to Zillow's database
    """
    listing_id = []
    listing_url = list() # need to check IDs versus zpids on URLs

    # loop each page
    for k in range(0, len(pages)): 
        # Access the given article tag wich holds the IDs
        for id in soup[k].findAll('article', {'class':"list-card list-card-additional-attribution list-card-additional-attribution-space list-card_not-saved"}):
            # Get the text and store it
            id_zpid = str(id['id'])

            # Strip the preceding 'zpid_'
            id_str = id_zpid.strip('zpid_')

            # Store in a list
            listing_id.append(id_str)

    for k in range(0, len(pages)):
        # Get geographic location from each page
        for loc in soup[k].findAll('script', {'type': 'application/ld+json'}):
            # Information is stored in JSON string format; store it as an object (dict)
            loc_info = json.loads(loc.text)

            # Ignore multiple details in the extracted HTML file such as 'Events'
            if loc_info['@type'] == 'SingleFamilyResidence':
                # Access the 'url' key in the dictionary
                list_url = loc_info['url']

                # Store all URLs in a list
                listing_url.append(list_url)

    # Empty string to hold valid non-duplicate ID values
    valid_listing_id = []

    for i in range(0, len(listing_url)): # loop each url
        for j in range(0, len(listing_id)): # loop each id
            if listing_url[i].__contains__(listing_id[j]): # Check URL contains ID
                valid_listing_id.append(listing_id[j]) # Store valid IDs

    return valid_listing_id
#-------------------------------------------------------------------------------

#11. Get time listing was made to Zillow
def listing_time(pages, soup):
    """
    Returns the time the real-estate listing was added to Zillow's website
    """
    list_time = []
    count = 0
    # loop each page
    for k in range(0, len(pages)): 
        # Get the time listing was published to Zillow from each page
        for time in soup[k].findAll('div', {'class':'list-card-variable-text list-card-img-overlay'}):
            # Get the text and store it
            time_str = time.text
            list_time.append(time_str)
    return list_time
# ------------------------------------------------------------------------------

#12. Get the listing URL
def listing_url(pages, soup):
    """
    Returns the URL for each of the Zillow's real-estate listings which allows
    for visualization (i.e. real-life photos) of the home/apartment
    """
    listing_url = []
    # loop each page
    for k in range(0, len(pages)): 
        # Get geographic location from each page
        for loc in soup[k].findAll('script', {'type': 'application/ld+json'}):
            # Information is stored in JSON string format; store it as an object (dict)
            loc_info = json.loads(loc.text)

            # Ignore multiple details in the extracted HTML file such as 'Events'
            if loc_info['@type'] == 'SingleFamilyResidence':
                # Access the 'url' key in the dictionary
                list_url = loc_info['url']

                # Store all URLs in a list
                listing_url.append(list_url)
                
    return listing_url
# -------------------------------------------------------------------------------

#13. Get the date and time data was scraped
def dateTimeScrape(pages, soup):
    """
    Returns the date and time data was scraped from Zillow
    """
    dt = []
    # Assign timezone
    tz_NY = pytz.timezone('America/New_York')
    datetime_local = datetime.now(tz_NY)

    date_time = datetime_local.strftime("%m-%d-%Y_%H:%M:%S")
    dt = [date_time] * len(home_address(pages, soup))
    
    return dt
#--------------------------------------------------------------------------------

#14. Write data to equivalent CSV and JSON files
def to_file(dataTable):
    """
    Writes the pandas Housing DataFrame object to both CSV and JSON files
    """
    # Assign timezone
    tz_NY = pytz.timezone('America/New_York')
    datetime_local = datetime.now(tz_NY)

    '''Code to create file directory if copied to an EC2 instance'''
    data_folder = 'zillow_crawled_data'
    if not os.path.isdir(data_folder):
        os.makedirs(data_folder)

    # Get the current date & time
    current_time = datetime_local.strftime("%m_%d_%Y__%H_%M_%S")

    # Create the CSV & JSON files of raw data 
    filename_csv = os.path.join(data_folder,'raw_housing_data_' + city.lower().replace(" ","_") + '_{0}.csv'.format(current_time))
    filename_json = os.path.join(data_folder,'raw_housing_data_' + city.lower().replace(" ","_") + '_{0}.json'.format(current_time))

    print("CSV file of data:", filename_csv)
    print("JSON file of data:", filename_json)

    # Write the data frame to the above files
    dataTable.to_csv(filename_csv, index=False, encoding="utf-8")
    dataTable.to_json(filename_json)
    
    return None
#-----------------------------------------------------------------------------

# Call the functions to get the housing data
if __name__ == "__main__":
    price = home_price(zillow_pages, bsobj)
    address = home_address(zillow_pages, bsobj)
    cityState = city_state(zillow_pages, bsobj)
    zipCode = zip_code(zillow_pages, bsobj)
    bedNum = bed_count(zillow_pages, bsobj)
    bathNum = bath_count(zillow_pages, bsobj)
    area = area_sqft(zillow_pages, bsobj)
    location = lat_long(zillow_pages, bsobj)
    homeStat = home_status(zillow_pages, bsobj)
    listURL = listing_url(zillow_pages, bsobj)
    dateTime = dateTimeScrape(zillow_pages, bsobj)
# #     if len(listing_id(zillow_pages, bsobj)) == len(address): # drop if # of IDs is incomplete
    listID = listing_id(zillow_pages, bsobj)
#     if len(listing_time(zillow_pages, bsobj)) == len(address): # drop if # of times is incomplete
    listTime = listing_time(zillow_pages, bsobj)
    
#-----------------------------------------------------------------------------
# For debugging purposes
print(len(price))
print(len(address))
print(len(cityState[0]))
print(len(cityState[1]))
print(len(zipCode))
print(len(bedNum))
print(len(bathNum))
print(len(area))
print(len(location[0]))
print(len(homeStat))
print(len(listURL))
print(len(listID))
print(len(listTime))

#-----------------------------------------------------------------------------
# Create a dictionary for the Housing Data
Housing_data = {
    'address_street': address,
    'city': cityState[0],
    'state': cityState[1],
    'zip_code': zipCode,
    'price': price,
    'beds': bedNum,
    'baths': bathNum,
    'area_sq_ft': area,
    'latitude': location[0],
    'longitude': location[1],
    'status_text': homeStat,
    'list_url': listURL,
    'date_scraped' : dateTime
}
# Store extracted data in a DataFrame
df = pd.DataFrame.from_dict(Housing_data)

# If listing IDs and times are of the same length then
if len(listID) == len(address):
    df['listing_id'] = listID
    
if len(listTime) == len(address):
    df['listing_time'] = listTime
#-----------------------------------------------------------------------------

# Store DataFrame to CSV & JSON files
if __name__ == "__main__":
        to_file(df)