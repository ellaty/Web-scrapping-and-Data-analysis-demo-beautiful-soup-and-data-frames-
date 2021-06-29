
#We are going to do our webscrapping demo using beautiful soup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import time
from datetime import datetime
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests


#define the numebr of pages to scrap

number_of_pages = 2

def scrap_page(number_of_pages):
#Define the user Agent, generally the browser that you are going to be using 
#we are also going to define some of  the parameters to use whole bypassing the dectectors 
#so we can be able to scrap the web site.
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

    #request the content and extract it in the content variable
    #r = requests.get('https://www.amazon.in/gp/bestsellers/books/ref=zg_bs_pg_'+str(number_of_pages)+'?ie=UTF8&pg='+str(number_of_pages), headers=headers)#, proxies=proxies)
    r = requests.get('https://www.amazon.com/gp/bestsellers/books/ref=bsm_nav_pill_print/ref=s9_acss_bw_cg_bsmpill_1c1_w?pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-1&pf_rd_r=JSFR919BB1373W4FETRV&pf_rd_t=101&pf_rd_p=65e3ce24-654c-43fb-a17b-86a554348820&pf_rd_i=16857165011'+str(number_of_pages)+'?ie=UTF8&pg='+str(number_of_pages), headers=headers)#, proxies=proxies)
    content = r.content

    #store the content in a beautiful soup variable
    soup = BeautifulSoup(content)

    #print(soup)

    #declare an array to contain your data
    all_details = []

    #loop through the div that has the information that we are lloking for, access it by its class variable
    for info in soup.findAll ('div', attrs={'class':'a-section a-spacing-none aok-relative'}):
        #print(info)
        #print("***********************************************")
        #we are doing the same thing on an the attributews under this div so we can extract the info we need
        name_container = info.find('span',attrs={'class':'zg-text-center-align'}) 
        name = name_container.find_all('img', alt=True)
        #print(name)
        #print("***********************************************")
        #finding all of the other attributes

        author = info.find('a', attrs={'class':'a-size-small a-link-child'})
        rating = info.find('span', attrs={'class':'a-icon-alt'})
        users_rated = info.find('a', attrs={'class':'a-size-small a-link-normal'})
        price = info.find('span', attrs={'class':'p13n-sc-price'})

        #create an array that is going to contain information about a given book
        book_info =[]

        if name_container is not None:
            book_info.append(name[0]['alt'])
        else:
            book_info.append("unknown-product")

        #Now going to the author 
        #Sometimes you have to dig dipper
        if author is not None:
            #print(author.text)
            book_info.append(author.text)
        elif author is None:
            author = info.find('span', attrs={'class':'a-size-small a-color-base'})
            if author is not None:
                book_info.append(author.text)
            else:    
                book_info.append('0')

        #get the ratings info
        if rating is not None:
            #print(rating.text)
            book_info.append(rating.text)
        else:
            book_info.append('-1')

        #get the number of the users that rated it
        if users_rated is not None:
            book_info.append(users_rated.text)
        else:
            book_info.append('0')   

        #get the price
        if price is not None:
            #print(price.text)
            book_info.append(price.text)
        else:
            book_info.append('0')

        #add all the our book info to the array that is going to contain all the books
        all_details.append(book_info)
    #print("8888888888888888888888888888888888888")
    #print(all_details)
    #print("8888888888888888888888888888888888888")

    return all_details

#we are going to save our data on a csv file
results = []
for i in range(1, number_of_pages+1):
    results.append(scrap_page(i))
#we are going to flatten our dflist result, so we can make a data frame out of it
flatten = lambda l: [item for sublist in l for item in sublist]
#make a dataframe out of our flattenedList.
df = pd.DataFrame(flatten(results),columns=['Book Name','Author','Rating','Customers_Rated', 'Price'])
#printing our dataframe on the console
print("8888888888888888888888888888888888888")
print(df)
print("8888888888888888888888888888888888888")
df.to_csv('amazon_products.csv', index=False, encoding='utf-8')

#in the next session we are going to do further data analysis on this data we have

data_frame = pd.read_csv("amazon_products.csv")
#look at the dimensions , how many columns and rows do you have
df.shape
print(df.shape)

#extract only the number from the rating column
df['Rating'] = df['Rating'].apply(lambda x: x.split()[0])
# turn the values of the rating column into numbers 
df['Rating'] = pd.to_numeric(df['Rating'])
#from the price colum remove the dollar sign by replacing it with an empty string
df["Price"] = df["Price"].str.replace('$', '')
#save the price as float values
df['Price'] = df['Price'].astype(float)

#remove commas from the values of the number of customers, and turn the new values into numbers
df["Customers_Rated"] = df["Customers_Rated"].str.replace(',', '')
df['Customers_Rated'] = pd.to_numeric(df['Customers_Rated'], errors='ignore')
print(df["Customers_Rated"])

#replace the zero values in our dataframe by Nan so we can be able to drop them later
df.replace(str(0), np.nan, inplace=True)
df.replace(0, np.nan, inplace=True)

#drop the NaNs so we end up with clean data
df = df.dropna()

#now that we have this information, we can sort by ratings (so we see the most liked book)
#and get the first ten columns
sorted_data = df.sort_values(["Rating"], axis=0, ascending=False)[:10]
print(sorted_data)
#show the whole thing on a graph
sorted_data.plot(x ='Book Name', y='Price', kind = 'bar')
plt.show()
