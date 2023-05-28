
from http.client import REQUESTED_RANGE_NOT_SATISFIABLE
import json
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime

required_city="Bangalore"
location_url='https://locator-service.api.bbci.co.uk/locations?'+urlencode({
    'api_key': 'AGbFAKx58hyjQScCXIYrxuEwJh2W2cmv',
    's': required_city,
    'stack': 'aws',
    'locale': 'en',
    'filter': 'international',
    'place-types': 'settlement,airport,district',
    'order': 'importance',
    'a': 'true',
    'format': 'json'
})
location_url

result=requests.get(location_url).json()

url='https://www.bbc.com/weather/'+result['response']['results']['results'][0]['id']
response=requests.get(url)

soup=BeautifulSoup(response.content,'html.parser')

daily_high_values = soup.find_all('span', attrs={'class': 'wr-day-temperature__high-value'})
daily_low_values  = soup.find_all('span', attrs={'class': 'wr-day-temperature__low-value'})
daily_summary = soup.find('div', attrs={'class': 'wr-day-summary'})

daily_high_values_list=[daily_high_values[i].text.strip().split()[0] for i in range(len(daily_high_values))]
daily_low_values_list=[daily_low_values[i].text.strip().split()[0] for i in range(len(daily_low_values))]

daily_summary_list=re.findall('[a-zA-Z][^A-Z]*',daily_summary.text)

datelist=pd.date_range(datetime.today(),periods=len(daily_high_values)).tolist()

datelist=[datelist[i].date().strftime('%y-%m-%d') for i in range(len(datelist))]

zipped=zip(datelist, daily_high_values_list, daily_low_values_list, daily_summary_list)
df=pd.DataFrame(list(zipped),columns=['Date','High','Low','Summary'])

df.High = df.High.replace('\°','',regex=True).astype(float)
df.Low  = df.Low.replace('\°','',regex=True).astype(float)

location = soup.find('h1', attrs={'id':'wr-location-name-id'})

filename_csv = location.text.split()[0]+'.csv'
df.to_csv(filename_csv, index=None)


