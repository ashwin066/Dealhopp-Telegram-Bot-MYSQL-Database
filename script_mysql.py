### Importing necessary libraries

import configparser  # pip install configparser
from telethon import TelegramClient, events  # pip install telethon
from datetime import datetime
import MySQLdb  # pip install mysqlclient
import requests
from bs4 import BeautifulSoup
import re

from urllib.parse import unquote
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import threading
import json
from datetime import timedelta


### Initializing Configuration
print("Initializing configuration...")
config = configparser.ConfigParser()
config.read("config.ini")

# Read values for Telethon and set session name
API_ID = config.get("default", "api_id")
API_HASH = config.get("default", "api_hash")
BOT_TOKEN = config.get("default", "bot_token")
session_name = "sessions/Bot"

# Read values for MySQLdb
HOSTNAME = config.get("default", "hostname")
USERNAME = config.get("default", "username")
PASSWORD = config.get("default", "password")
DATABASE = config.get("default", "database")

# Start the Client (telethon)
client = TelegramClient(session_name, API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# //extra functions
website_title_mapping = {
    "amazon": {"class": ["a-size-large a-spacing-none","a-unordered-list a-nostyle a-vertical a-spacing-medium"], "id": "title", "tag": "h1", "type": None,'name':None},
    "flipkart": {"class": "B_NuCI", "id": None, "tag": "span", "type": None,'name':None},
    "myntra": {"class": None, "id": None, "tag": "meta", "type": None, 'name': 'twitter:title' },
    "croma": {
        "class": None,
        "id": None,
        "tag": "meta", "type": None,'name':'title'
    },
    "tatacliq": {
        "class": "ProductDetailsMainCard__productName",
        "id": None,
        "tag": "h1",  "type": None,'name':None
    },
    "ajio": {
        "class": "prod-name",
        "id": None, 
        "tag": "h1",  "type": None,'name': None
    },
    # Add more websites and their corresponding class and id names as needed
}
website_description_mapping = {
    "amazon": {"class": "a-section a-spacing-medium a-spacing-top-small", "id": "feature-bullets", "tag": "div", "type": None,'name':None},
    "flipkart": {"class": "_2418kt", "id": None, "tag": "div", "type": None,'name':None},
    "myntra": {"class": None, "id": None, "tag": "meta", "type": None, 'name': 'keywords', },
    "croma": {
        "class": None,
        "id": None,
        "tag": "meta", "type": None,'name':'description'
    },
    "tatacliq": {
        "class": "Accordion__shortDescription",
        "id": None,
        "tag": "div",  "type": None,'name':None
    },
    "ajio": {
        "class": "prod-desc",
        "id": None, 
        "tag": "section",  "type": None,'name': None
    },
    # Add more websites and their corresponding class and id names as needed
}
website_img_mapping = {
    "amazon": {"class": ["a-dynamic-image","s-image"], "id": None, "tag": "img", "type": None,'name':None},
    "flipkart": {"class": "_396cs4 _2amPTt _3qGmMb", "id": None, "tag": "img", "type": None,'name':None},
    "myntra": {"class": "image-grid-image", "id": None, "tag": "div", "type": None, 'name': None, },
    "croma": {
        "class": "pdp_lzy_img",
        "id":None,
        "tag": "img", "type": None,'name':None
    },
    "tatacliq": {
        "class": "ProductGalleryDesktopUpdated__images",
        "id": None,
        "tag": "img",  "type": None,'name':None
    },
    "ajio": {
        "class": "rilrtl-lazy-img img-alignment zoom-cursor rilrtl-lazy-img-loaded",
        "id": None, 
        "tag": "img",  "type": None,'name': None
    },
    # Add more websites and their corresponding class and id names as needed
}
website_mrp_mapping = {
    "amazon": {"class": ["a-size-small a-color-secondary aok-align-center basisPrice","a-price a-text-price a-size-base"], "id": None, "tag": "span", "type": None,'name':None},
    "flipkart": {"class": "_3I9_wc _2p6lqe", "id": None, "tag": "div", "type": None,'name':None},
    "myntra": {"class": "pdp-mrp", "id": None, "tag": "span", "type": None, 'name': None, },
    "croma": {
        "class": "amount",
        "id": "old-price",
        "tag": "span", "type": None,'name':None
    },
    "tatacliq": {
        "class": "ProductDetailsMainCard__cancelPrice",
        "id": None,
        "tag": "span",  "type": None,'name':None
    },
    "ajio": {
        "class": "prod-cp",
        "id": None, 
        "tag": "span",  "type": None,'name': None
    },
    # Add more websites and their corresponding class and id names as needed
}
website_deal_price_mapping = {
    "amazon": {"class": ["a-price aok-align-center reinventPricePriceToPayMargin priceToPay","a-price a-text-price a-size-medium apexPriceToPay"], "id": None, "tag": "span", "type": None,'name':None},
    "flipkart": {"class": "_30jeq3 _16Jk6d", "id": None, "tag": "div", "type": None,'name':None},
    "myntra": {"class": "pdp-price", "id": None, "tag": "span", "type": None, 'name': None, },
    "croma": {
        "class": "amount",
        "id": "pdp-product-price",
        "tag": "span", "type": None,'name':None
    },
    "tatacliq": {
        "class": "ProductDetailsMainCard__price",
        "id": None,
        "tag": "div",  "type": None,'name':None
    },
    "ajio": {
        "class": "prod-sp",
        "id": None, 
        "tag": "div",  "type": None,'name': None
    },
    # Add more websites and their corresponding class and id names as needed
}

def extract_numerical_value(input_string):
    """
    Extracts the numerical value from a string.

    Parameters:
    - input_string (str): The input string containing a numerical value.

    Returns:
    - int: The extracted numerical value.
      Returns None if no numerical value is found.
    """
    # Use regex to extract the numerical part
    match = re.search(r'[\d,]+(\.\d+)?', input_string)

    # Check if a match is found
    if match:
        # Remove commas and convert to a float
        try:
            numerical_value = float(match.group().replace(',', ''))
            return numerical_value
        except Exception as e:
            print(f"Error: {e}")
            return input_string
       
    else:
        return input_string
    
async def get_link_preview(link, SENDER, tries):
    try:
        HEADERS = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        print('HTTP requests initializing...')
        # Use aiohttp for asynchronous HTTP requests
        response = requests.get( link , headers=HEADERS)  
        html_content =   response.text
        print('HTTP requests initialized')
        soup = BeautifulSoup(html_content, 'html.parser')

        finalUrl = response.url 
        print("final URL:" + finalUrl)

        website_name = finalUrl.split(".")[1]

        print("first attempt:" + website_name)

        title_attributes = website_title_mapping.get(website_name)
        description_attributes = website_description_mapping.get(website_name)
        img_attributes = website_img_mapping.get(website_name)
        mrp_attributes = website_mrp_mapping.get(website_name)
        deal_price_attributes = website_deal_price_mapping.get(website_name)
        
        
        if title_attributes is None:
            website_name = finalUrl.split(".")[2]
            print("second attempt:" + website_name)
            finalUrlDomainName = finalUrl.split(".")[0]
            if (
                finalUrlDomainName == "https://linkredirect"
                or finalUrlDomainName == "http://linkredirect"
            ):
                print("second attempt:" + website_name)
                finalUrl =  website_name + "." + finalUrl.split(".")[3]
                print (finalUrl)
                await get_link_preview(finalUrl, SENDER,0)
                return None

            title_attributes = website_title_mapping.get(
                website_name, {"class": "title", "id": "title", "tag": "span", "type": "text"}
            )
            description_attributes = website_description_mapping.get(
                website_name, {"class": "description", "id": "description", "tag": "span", "type": "text"}
            )
            img_attributes = website_img_mapping.get(
                website_name, {"class": "image", "id": "image", "tag": "span", "type": "text"}
            )
            mrp_attributes = website_mrp_mapping.get(
                website_name, {"class": "mrp", "id": "mrp", "tag": "span", "type": "text"}
            )
            deal_price_attributes = website_deal_price_mapping.get(
                website_name, {"class": "deal", "id": "deal", "tag": "span", "type": "text"}
            )                        
        # Use headless Chrome with selenium
        if website_name == "amazon" :
        #     options = Options()
        #     options.headless = True
        #     driver = webdriver.Chrome(options=options)
        #     driver.minimize_window()
        #     driver.get(finalUrl)

            
        #     # Wait for dynamic content to load if needed
        #     driver.implicitly_wait(1)

        #     # Get the page source after JavaScript execution
        #     html_content = driver.page_source
        #     driver.quit()

            soup = BeautifulSoup(html_content, 'lxml')
        elif website_name == "ajio" or  website_name == "tatacliq" or website_name == "myntra"  or website_name == "croma" :
                    options = Options()
                    options.headless = True
                    driver = webdriver.Chrome(options=options)
                    driver.minimize_window()
                    driver.get(finalUrl)

                    
                    # Wait for dynamic content to load if needed
                    driver.implicitly_wait(1)

                    # Get the page source after JavaScript execution
                    html_content = driver.page_source
                    driver.quit()
                    soup = BeautifulSoup(html_content, 'html.parser')
        else:
            soup = BeautifulSoup(response.text, 'html.parser')

        # title_tag = soup.find(
        #     title_attributes["tag"],
        #     attrs={"class": title_attributes["class"], "id": title_attributes["id"], "type": title_attributes["type"], 'name': title_attributes["name"]},
        # )
        
        # title_tag
        if isinstance(title_attributes["class"], list):
            for classname in title_attributes["class"]:
               title_tag = soup.find(
                                title_attributes["tag"],
                                attrs={"class": classname, "id": title_attributes["id"], "type": title_attributes["type"], 'name': title_attributes["name"]},
                            ) 
               if title_tag != None:
                   break
        else:
            title_tag = soup.find(
            title_attributes["tag"],
            attrs={"class": title_attributes["class"], "id": title_attributes["id"], "type": title_attributes["type"], 'name': title_attributes["name"]},
        )
        
        
        description_tag = soup.find(
            description_attributes["tag"],
            attrs={"class": description_attributes["class"], "id": description_attributes["id"], "type": description_attributes["type"], 'name': description_attributes["name"]},
        )  
        # img_tag = soup.find(
        #     img_attributes["tag"],
        #     attrs={"class": img_attributes["class"], "id": img_attributes["id"], "type": img_attributes["type"], 'name': img_attributes["name"]},
        # )
        
        #img_tag
        if isinstance(img_attributes["class"], list):
            for classname in img_attributes["class"]:
               img_tag = soup.find(
                                img_attributes["tag"],
                                attrs={"class": classname, "id": img_attributes["id"], "type": img_attributes["type"], 'name': img_attributes["name"]},
                            ) 
               if img_tag != None:
                   break
        else:
            img_tag = soup.find(
            img_attributes["tag"],
            attrs={"class": img_attributes["class"], "id": img_attributes["id"], "type": img_attributes["type"], 'name': img_attributes["name"]},
        )
                
        # mrp_tag = soup.find(
        #     mrp_attributes["tag"],
        #     attrs={"class": mrp_attributes["class"], "id": mrp_attributes["id"], "type": mrp_attributes["type"], 'name': mrp_attributes["name"]},
        # )      
        
        #mrp_tag
        if isinstance(mrp_attributes["class"], list):
            for classname in mrp_attributes["class"]:
               mrp_tag = soup.find(
                                mrp_attributes["tag"],
                                attrs={"class": classname, "id": mrp_attributes["id"], "type": mrp_attributes["type"], 'name': mrp_attributes["name"]},
                            ) 
               if mrp_tag != None:
                   break
        else:
            mrp_tag = soup.find(
            mrp_attributes["tag"],
            attrs={"class": mrp_attributes["class"], "id": mrp_attributes["id"], "type": mrp_attributes["type"], 'name': mrp_attributes["name"]},
        )
            
        #deal_price_tag    
        if    isinstance(deal_price_attributes["class"], list):
            for classname in deal_price_attributes["class"]:
               print("hi im inside for loop deal price")
               deal_price_tag = soup.find(
                                deal_price_attributes["tag"],
                                attrs={"class": classname, "id": deal_price_attributes["id"], "type": deal_price_attributes["type"], 'name': deal_price_attributes["name"]},
                            ) 
               if deal_price_tag != None:
                   break
        else:
            deal_price_tag = soup.find(
            deal_price_attributes["tag"],
            attrs={"class": deal_price_attributes["class"], "id": deal_price_attributes["id"], "type": deal_price_attributes["type"], 'name': deal_price_attributes["name"]},
        )            
                                
        # deal_price_tag = soup.find(
        #     deal_price_attributes["tag"],
        #     attrs={"class": deal_price_attributes["class"], "id": deal_price_attributes["id"], "type": deal_price_attributes["type"], 'name': deal_price_attributes["name"]},
        # )        
               
        print(soup.find_all('img'))
        
        message=''
        title_text=''
        description_text=''
        img_url=''
        mrp_text=''
        deal_price_text=''
        
        if title_tag is not None:
            if title_attributes["tag"] == "meta":
                title_text = title_tag.get('content', 'Product from '+website_name).strip()
            else:
                title_text = title_tag.text.strip()
            message =message+ f"\n*Fetched title*: {title_text}"
            print("Status:" + message)     
        else:
            message = "Title not found on the page."
            print("Status:" + message)
            tries+=1
            if tries < 10 and website_name == "amazon" :
                await get_link_preview(finalUrl, SENDER,tries)
                return None
               
        if description_tag is not None:
            if  description_attributes["tag"] == "meta":
                description_text = description_tag.get('content', 'Product from '+website_name).strip()
      
            else:
                description_text = description_tag.text.strip()
            message =message+ f"\n*Fetched description*: {description_text}"
            print("Status:" + message) 
        else:
            message = message+"\nDescription not found on the page."
            print("Status:" + message)            
                  
        if img_tag is not None:
            if  img_attributes["tag"] == "meta":
                img_url = img_tag.get('content', '').strip()
            elif img_attributes["tag"] == "img":
                img_url = img_tag.get('data-src', '').strip()
                if img_url == '':
                    img_url = img_tag.get('src', '').strip()
                if img_url ==  '':
                    img_url = img_tag.get('data-a-dynamic-image', '').strip()
            elif img_attributes["tag"] == "div":
                 print(img_tag.get('style',''))
                 links, text_words = extract_links_and_text(img_tag.get('style','').strip()) 
                
                 if links[0] is not None:
                    img_url = links[0]
                 
            
                
            else:
                img_url = img_tag.text.strip()
            message =message+ f"\n*Fetched Image*: {img_url}"
            print("Status:" + message) 
        else:
            message = message+"\nImage not found on the page."
            print("Status:" + message) 
               
        if mrp_tag is not None:
            if  mrp_attributes["tag"] == "meta":
                mrp_text = mrp_tag.get('content', '0').strip()
      
            else:
                mrp_text = mrp_tag.text.strip()
            print("MRP: "+mrp_text)  
            mrp_text = extract_numerical_value(mrp_text)  
            
            message =message+ f"\n*Fetched MRP*: {mrp_text}"
            print("Status:" + message) 
        else:
            message = message+"\nMRP not found on the page."
            print("Status:" + message)            
                 
        if deal_price_tag is not None:
            if  deal_price_attributes["tag"] == "meta":
                deal_price_text = deal_price_tag.get('content', '0').strip()
      
            else:
                deal_price_text = deal_price_tag.text.strip()
            deal_price_text = extract_numerical_value(deal_price_text)        
            message =message+ f"\n*Fetched Deal Price*: {deal_price_text}"
            print("Status:" + message) 
        else:
            message = message+"\nDeal Price not found on the page."
            print("Status:" + message)      
        
        
        if title_text != None:    
            brand_id = await get_brand_id_from_db(website_name)      
            if brand_id == None:
                message = message+"\nBrand ID for "+website_name+" was not found"
            else:
                message = message+"\nBrand ID for "+website_name+" is "+str(brand_id)    
                            
            # Send the message
        await client.send_message(SENDER, message, parse_mode="markdown")
            
        if title_text != None:                
            await add_product_to_db(finalUrl,title_text,description_text,img_url,mrp_text,deal_price_text,brand_id,SENDER)
        await delete_old_products(SENDER)
                    
    except Exception as e:
        print(f"Error: {e}")
        return None



async def delete_old_products(SENDER):
    try:
        # Calculate the date three weeks ago
        three_weeks_ago = datetime.now() - timedelta(days=14)
        three_weeks_ago_str = three_weeks_ago.strftime("%Y-%m-%d")

        # Execute SQL delete query to delete old products
        sql_command = "DELETE FROM products WHERE date < %s"
        crsr.execute(sql_command, (three_weeks_ago_str,))
        conn.commit()

        # Get the number of deleted rows
        deleted_rows = crsr.rowcount

        # Send a message indicating the number of deleted products
        message = f"{deleted_rows} products older than one day have been deleted."
        print(message)
        await client.send_message(SENDER, message, parse_mode="markdown")

    except Exception as e:
        print(f"Error: {e}")


async def add_product_to_db(product_link,title,description, img_url,mrp_text,deal_price_text,brand_id, SENDER):
    try:
        
     

        
       if title != '' and product_link != '' and deal_price_text != '' and mrp_text != '': 
            crsr.execute(
                "SELECT product_title, COUNT(*) FROM products WHERE product_title = %s GROUP BY product_title",
                (title,)
            )
            # gets the number of rows affected by the command executed
            row_count = crsr.rowcount
            
            if row_count == 0:         
                dt_string = (
                    datetime.now()
                )  # Use the datetime library to the get the date (and format it as DAY/MONTH/YEAR)
                # Create the tuple "params" with all the parameters inserted by the user
                params = (
                    title,
                    description,
                    0,
                    '',
                    5,
                    brand_id,
                    '/dealhopp/assets/images/icons/alt.png' if img_url == '' else img_url,
                    '/dealhopp/assets/images/icons/alt.png' if img_url == '' else img_url,
                    '/dealhopp/assets/images/icons/alt.png' ,
                    mrp_text if mrp_text !=  0  else None,
                    deal_price_text if deal_price_text !=  0  else None,
                    product_link if product_link != '' else None,
                    
                    
                    dt_string,
                    'true',
                    660,
                    0,
                )
                sql_command = "INSERT INTO products (product_title, product_description,coupon,product_keywords,  product_category, product_brand, product_img1, product_img2, product_img3, product_old_price, product_price,product_link, date,status,posted_user_id,is_coupon ) VALUES (  %s, %s, %s, %s, %s, %s, %s, %s,  %s, %s, %s, %s, %s, %s, %s, %s);"  # the initial NULL is for the AUTOINCREMENT id inside the table
                crsr.execute(sql_command, params)  # Execute the query
                conn.commit()  # commit the changes

                # If at least 1 row is affected by the query we send specific messages
                if crsr.rowcount < 1:
                    text = "Something went wrong, please try again"
                    await client.send_message(SENDER, text, parse_mode="markdown")
                else:
                    text = "Order correctly inserted"
                    await client.send_message(SENDER, text, parse_mode="markdown")
            else:
                 text = "Product not inserted to database because, a product with same title already exists"
                 await client.send_message(SENDER, text, parse_mode="markdown")

       else:
            text = "Did not publish product to Database"
            await client.send_message(SENDER, text, parse_mode="markdown")
            return

    except Exception as e:
        print(f"Error: {e}")
        return None




def extract_links_and_text(message_text):
    # Regular expression pattern to match URLs
    url_pattern = r'https?://\S+|www\.\S+'

    # Find all URLs in the message text
    links = re.findall(url_pattern, message_text)

    # Remove the URLs from the text
    text_without_links = re.sub(url_pattern, "", message_text)

    # Split the remaining text into a list of words
    text_words = text_without_links.split()

    # Function to extract URLs and remove trailing characters
    def extract_urls(text):
        url_pattern = re.compile(r'https?://\S+')
        matches = url_pattern.findall(text)
        cleaned_urls = [url.split('");')[0] for url in matches]
        return cleaned_urls

    # Extract URLs from links and remove trailing characters
    cleaned_links = extract_urls(" ".join(links))

    # Print the cleaned links
    for link in cleaned_links:
        print(link)

    return cleaned_links, text_words


async def get_brand_id_from_db(brand_name):
    try:
        # Establish a connection to the database (replace 'your_database.db' with the actual database file)
 
        # Execute the query and get all (*) the orders
        crsr.execute("SELECT brand_id FROM brands WHERE LOWER(brand_title) LIKE "+ "'" + brand_name +"'")

        res = crsr.fetchone()  # fetch one result, assuming brand_id is unique
        # If there is at least 1 row selected, print a message with the brand_id
        if res:
            brand_id = res[0]
            print(f"Brand ID for '{brand_name}': {brand_id}")
            return brand_id
        # Otherwise, print a default text
        else:
            text = "No brands found inside the database."
            print(text)
            return None

    except Exception as e:
        print(e)
        return None

 


 
### START COMMAND
@client.on(events.NewMessage(pattern="(?i)/start"))
async def start(event):
    # Get sender
    sender = await event.get_sender()
    SENDER = sender.id

    # set text and send message
    text = "Hello i am a bot that can do CRUD operations inside a MySQL database"
    await client.send_message(SENDER, text)


### Insert command
@client.on(events.NewMessage())
async def insert(event):
    try:
        
         # Get the sender of the message
        sender = await event.get_sender()
        SENDER = sender.id
        await client.send_message(
            SENDER, "Processing...", parse_mode="html"
        )


        # Get the text of the user AFTER the /insert command and convert it to a list (we are splitting by the SPACE " " simbol)

       
        links, text_words = extract_links_and_text(event.message.text)
        
        if len(links) ==0:
            await client.send_message(
                    SENDER, "No Link Found", parse_mode="html"
            )
            return
        
        tasks = [threading.Thread(target=await get_link_preview(link, SENDER, 0)) for  link in links ]
        # Start the threads
        for task in tasks:
            task.start()
            
        

    except Exception as e:
        print(e)
        await client.send_message(
            SENDER, "Something Wrong happened... Check your code!", parse_mode="html"
        )
        return


# Function that creates a message containing a list of all the oders
def create_message_select_query(ans):
    text = ""
    for i in ans:
        id = i[0]
        product = i[1]
        quantity = i[2]
        creation_date = i[3]
        text += (
            "<b>"
            + str(id)
            + "</b> | "
            + "<b>"
            + str(product)
            + "</b> | "
            + "<b>"
            + str(quantity)
            + "</b> | "
            + "<b>"
            + str(creation_date)
            + "</b>\n"
        )
    message = "<b>Received 📖 </b> Information about products:\n\n" + text
    return message


### SELECT COMMAND
@client.on(events.NewMessage(pattern="(?i)/select"))
async def select(event):
    try:
        # Get the sender of the message
        sender = await event.get_sender()
        SENDER = sender.id
        # Execute the query and get all (*) the oders
        crsr.execute("SELECT * FROM products")
        res = crsr.fetchall()  # fetch all the results
        # If there is at least 1 row selected, print a message with the list of all the oders
        # The message is created using the function defined above
        if res:
            text = create_message_select_query(res)
            await client.send_message(SENDER, text, parse_mode="html")
        # Otherwhise, print a default text
        else:
            text = "No products found inside the database."
            await client.send_message(SENDER, text, parse_mode="html")

    except Exception as e:
        print(e)
        await client.send_message(
            SENDER, "Something Wrong happened... Check your code!", parse_mode="html"
        )
        return


### UPDATE COMMAND
@client.on(events.NewMessage(pattern="(?i)/update"))
async def update(event):
    try:
        # Get the sender
        sender = await event.get_sender()
        SENDER = sender.id

        # Get the text of the user AFTER the /update command and convert it to a list (we are splitting by the SPACE " " simbol)
        list_of_words = event.message.text.split(" ")
        id = int(list_of_words[1])  # second (1) item is the id
        new_product = list_of_words[2]  # third (2) item is the product
        new_quantity = list_of_words[3]  # fourth (3) item is the quantity
        dt_string = datetime.now().strftime("%d/%m/%Y")  # We create the new date

        # create the tuple with all the params interted by the user
        params = (id, new_product, new_quantity, dt_string, id)

        # Create the UPDATE query, we are updating the product with a specific id so we must put the WHERE clause
        sql_command = "UPDATE products SET id=%s, product=%s, quantity=%s, LAST_EDIT=%s WHERE id =%s"
        crsr.execute(sql_command, params)  # Execute the query
        conn.commit()  # Commit the changes

        # If at least 1 row is affected by the query we send a specific message
        if crsr.rowcount < 1:
            text = "Order with id {} is not present".format(id)
            await client.send_message(SENDER, text, parse_mode="html")
        else:
            text = "Order with id {} correctly updated".format(id)
            await client.send_message(SENDER, text, parse_mode="html")

    except Exception as e:
        print(e)
        await client.send_message(
            SENDER, "Something Wrong happened... Check your code!", parse_mode="html"
        )
        return


@client.on(events.NewMessage(pattern="(?i)/delete"))
async def delete(event):
    try:
        # Get the sender
        sender = await event.get_sender()
        SENDER = sender.id

        # / delete 1

        # get list of words inserted by the user
        list_of_words = event.message.text.split(" ")
        id = list_of_words[1]  # The second (1) element is the id

        # Crete the DELETE query passing the id as a parameter
        sql_command = "DELETE FROM products WHERE id = (%s);"

        # ans here will be the number of rows affected by the delete
        ans = crsr.execute(sql_command, (id,))
        conn.commit()

        # If at least 1 row is affected by the query we send a specific message
        if ans < 1:
            text = "Order with id {} is not present".format(id)
            await client.send_message(SENDER, text, parse_mode="html")
        else:
            text = "Order with id {} was correctly deleted".format(id)
            await client.send_message(SENDER, text, parse_mode="html")

    except Exception as e:
        print(e)
        await client.send_message(
            SENDER, "Something Wrong happened... Check your code!", parse_mode="html"
        )
        return


# Create database function
def create_database(query):
    try:
        crsr_mysql.execute(query)
        print("Database created successfully")
    except Exception as e:
        print(f"WARNING: '{e}'")


##### MAIN
if __name__ == "__main__":
    try:
        print("Initializing Database...")
        conn_mysql = MySQLdb.connect(host=HOSTNAME, user=USERNAME, passwd=PASSWORD)
        crsr_mysql = conn_mysql.cursor()

        query = "CREATE DATABASE " + str(DATABASE)
        create_database(query)
        conn = MySQLdb.connect(
            host=HOSTNAME, user=USERNAME, passwd=PASSWORD, db=DATABASE
        )
        crsr = conn.cursor()

        # Command that creates the "oders" table
        sql_command = """CREATE TABLE IF NOT EXISTS products ( 
            id INTEGER PRIMARY KEY AUTO_INCREMENT, 
            product_title VARCHAR(255),
            product_description VARCHAR(255),
            product_link VARCHAR(255),
            product_image VARCHAR(255),
            date VARCHAR(100));"""

        crsr.execute(sql_command)
        print("All tables are ready")

        print("Bot Started...")
        client.run_until_disconnected()

    except Exception as error:
        print("Cause: {}".format(error))



