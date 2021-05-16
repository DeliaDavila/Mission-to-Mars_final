
# Import Splinter, BeautifulSoup, and pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    #set up Splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)
    
    news_title, news_paragraph = mars_news(browser)

    hemisphere_urls = hemispheres(browser)
    
    # Run all scraping functions and store results in dictionary
    data = {
          "news_title": news_title,
          "news_paragraph": news_paragraph,
          "featured_image": featured_image(browser),
          "facts": mars_facts(),
          "last_modified": dt.datetime.now(),
          "hemispheres": hemisphere_urls
    }  
    
    # Stop webdriver and return data
    browser.quit()
    
    return data
    

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'  
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    #use browser to pull html and use soup to parse it. 
    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None
        
    return news_title, news_p  


# JPL Space Images Featured Image

def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None
    
    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url

#Mars Facts

def mars_facts():
    try:
        #scraping Mars Facts table into pandas df   
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
        
    except BaseException:
        return None
    
    # Assign columns and set index of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)
    
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-dark table-hover")

#Mars Hemisphere images
def hemispheres(browser):
    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    html = browser.html
    #mars_soup = soup(html, 'html.parser')

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Retrieve the image urls and titles for each hemisphere.

    for i in range (0,4):
        
        browser.find_by_css("a.product-item img")[i].click()

        html = browser.html
        link_soup = soup(html, 'html.parser')
        
        parent_class = link_soup.find('li')
        url_link = parent_class.find('a', target='_blank')['href']
        image_url = (url + url_link)
        
        image_title = link_soup.find('h2', class_='title').get_text() 
        
        hemispheres = {}
        hemispheres ["title"] = image_title
        hemispheres ["img_url"] = image_url

        hemisphere_image_urls.append(hemispheres)
        
        browser.back()

    # 4. return the list of dictionaries with each image url and title.
    return hemisphere_image_urls

    
if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())


