from selenium.webdriver.common.action_chains import ActionChains
import codecs,string,re
from selenium import webdriver
from urllib import request as ulreq
from PIL import ImageFile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.headless = True
wd = webdriver.Chrome('chromedriver',options=chrome_options)

wd.get("https://classcentral-scrape-hindi.vercel.app/")

# input + "institution/google.html"
# input + "institution/amazon.html"
# input + "provider/coursera.html"


def is_hover(wd):
    hover =True
    sub_menu = True
    a = ActionChains(wd)

    try:
        m= wd.find_element(By.CLASS_NAME, "hidden.weight-semi.large-up-block.text-1.color-charcoal.padding-right-small")
        a.move_to_element(m).perform()
        m= wd.find_element(By.CLASS_NAME, "main-nav-dropdown__item-control.color-charcoal")
        a.move_to_element(m).perform()
    except:
        hover = False

    try:
        m= wd.find_element(By.CLASS_NAME, "main-nav-dropdown__section-heading")
        a.move_to_element(m).perform()
    except:
        sub_menu = False

    return hover, sub_menu 

def is_hindi(string):
    maxchar = max(string)
    if u'\u0900' <= maxchar <= u'\u097f':
        return True
    else:
        return False

def RemoveHTMLTags(page_source):
    
    strr = ''.join([i for i in page_source if not i.isdigit()])

    # Print string after removing tags
    strr = re.compile(r"(?is)<script[^>]*>(.*?)</script>").sub('', strr)
    strr = re.compile(r"(?is)<style[^>]*>(.*?)</style>").sub('', strr)
    strr = (re.compile(r'<[^>]+>').sub('', strr))
    return strr.replace("\n"," ").replace("  ","")

def getsizes(uri):
    # get file size and image size (None if not known)
    file = ulreq.urlopen(uri)
    size = file.headers.get("content-length")
    if size: 
        size = int(size)
    p = ImageFile.Parser()
    while True:
        data = file.read(1024)
        if not data:
            break
        p.feed(data)
        if p.image:
            return size, p.image.size
            break
    file.close()
    return(size, None)

def img_quality(wd):
    all_img = 0
    loaded_img = 0
    quality_img = 0

    for e in wd.find_elements(By.TAG_NAME,"img"):
        all_img += 1
        # print("Actual size:",getsizes(e.get_attribute("src")))
        # print("Element size:", e.size)
        try:
            img_size = getsizes(e.get_attribute("src"))
        except:
            img_size = (None, None)
        if e.size['height'] == 0 or e.size['height'] == 0 or img_size[0] == None or img_size[1] == None:
            continue
        else:
            loaded_img += 1
            if img_size[1][0] >= e.size['height'] :
                quality_img += 1
    return all_img , loaded_img , quality_img


def pipe(input):
    # wd.get("https://classcentral-scrape-hindi.vercel.app/")
    wd.get(input)
    
    per = (sum([is_hindi(x) for x in RemoveHTMLTags(wd.page_source)]) / (len(RemoveHTMLTags(wd.page_source))+1) ) * 100
    all_img , loaded_img , quality_img = img_quality(wd)
    
#     wd.get(input + "institution/google.html")
#     per1 = (sum([is_hindi(x) for x in RemoveHTMLTags(wd.page_source)]) / (len(RemoveHTMLTags(wd.page_source))+1) ) * 100
    
#     wd.get(input + "institution/amazon.html")
#     per2 = (sum([is_hindi(x) for x in RemoveHTMLTags(wd.page_source)]) / (len(RemoveHTMLTags(wd.page_source))+1) ) * 100
    
#     wd.get(input + "provider/coursera.html")
#     per3 = (sum([is_hindi(x) for x in RemoveHTMLTags(wd.page_source)]) / (len(RemoveHTMLTags(wd.page_source))+1) ) * 100
    
    result = {
        "Hover" : is_hover(wd),
        "per_translated_home " : per,
#         "per_translated_sample_1 " : per1,
#         "per_translated_sample_2 " : per2,
#         "per_translated_sample_3 " : per3,
        "num loaded images " : loaded_img ,
        "num of all images " : all_img ,
         "num of quality img " : quality_img ,
        "percentage of high quality img is " : (quality_img/(loaded_img+1)) * 100
    }
    
    return result

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def process_text():
    text = request.form['text']
    return pipe(text)

if __name__ == '__main__':
    app.run(host="0.0.0.0")

