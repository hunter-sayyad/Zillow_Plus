# Zillow_Plus
Zillow Housing Data Web Scraping
Overview

This project aims to scrape real-estate listings data from Zillow for a specified city and state. The code utilizes Python and the BeautifulSoup library to extract information such as home prices, addresses, number of bedrooms, bathrooms, area in square feet, geographic coordinates, listing IDs, and listing URLs.

Prerequisites

To run the code, you will need the following:

Python 3.x (https://www.python.org/downloads/)
BeautifulSoup (https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
Pandas (https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html)
Other necessary libraries (numpy, datetime, re, pytz)
Getting Started

Clone the repository to your local machine:

Copy code
git clone https://github.com/your_username/zillow-housing-scraper.git
Navigate to the project directory:

Copy code
cd zillow-housing-scraper
Install the required libraries using pip:

Copy code
pip install beautifulsoup4 pandas
Open the zillow_webscraping_1.py file and set the desired city by modifying the city variable.

Run the Python script:


Copy code
python zillow_webscraping_1.py
Crawling Data

The script will crawl Zillow's website for the specified city and state, extracting real-estate listings data for a set number of pages. It will display the status code for each page to indicate whether the request was successful (200).

Output

The extracted data will be stored in a pandas DataFrame and written to CSV and JSON files in the zillow_crawled_data folder. Each file will have a timestamp in its name, reflecting when the data was scraped.

Legal and Ethical Considerations

Please note that web scraping may be subject to legal restrictions and the terms of service of the website being scraped. Ensure compliance with these terms and obtain permission if required. Respect the website's data usage policies and avoid excessive or aggressive scraping.

Contributing

Contributions to the project are welcome! If you have any suggestions, improvements, or bug fixes, feel free to submit a pull request.

License

This project is licensed under the MIT License.

Disclaimer

This project is intended for educational and personal use only. The author does not take responsibility for any misuse or violation of the Zillow website's terms of service. Use the script responsibly and at your own risk.

If you have any questions or feedback, feel free to reach out to the project maintainer.

Happy scraping!
