import os
from selenium import webdriver
from flask import Flask, request, render_template, redirect
from flask_cors import cross_origin
from wikiSearch import WikiSearch
from webdriver_manager.chrome import ChromeDriverManager

import concurrent.futures
import time

app = Flask(__name__)

free_status = True
title, body_summary, info_image_encoded, images_encoded, references = "", "", "", [], []
db_name = "WikiSummary"

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-uses")
chrome_options.add_argument("--no-sandbox")


def scrap(wiki_obj, search_string):
    global free_status, title, body_summary, info_image_encoded, images_encoded, references
    free_status = False
    record = wiki_obj.wiki_scrapper(search_string)
    title = record["title"]
    body_summary = record["summary"]
    info_image_encoded = record['info_image']
    images_encoded = record["images"]
    references = record["references"]
    free_status = True


@app.route('/')
@cross_origin()
def index_page():
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
    driver.get("https://en.wikipedia.org/wiki/Main_Page")
    dyks = driver.find_element_by_id('mp-dyk').find_elements_by_css_selector('li')
    dyks = [dyk.text for dyk in dyks]
    driver.quit()
    return render_template('index.html', dyks=dyks[:-3])


@app.route('/summary', methods=["POST", "GET"])
@cross_origin()
def summary():
    if request.method == 'POST':
        global free_status

        if not free_status:
            return "Website busy"
        else:
            free_status = True

        search_string = request.form['term']
        if search_string == "":
            return redirect('/')

        wiki_obj = WikiSearch(ChromeDriverManager().install(), chrome_options, db_name)

        t1 = time.perf_counter()

        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(scrap, wiki_obj, search_string)
        # thread = ThreadClass(wiki_obj, search_string)
        except Exception as e:
            raise Exception("Error: \t" + str(e))

        t2 = time.perf_counter()
        print(f'Finished scraping in {round(t2 - t1, 2)} seconds')

        return render_template('summary.html', heading=title,
                               summary=body_summary,
                               info_image=info_image_encoded,
                               images=images_encoded,
                               references=references
                               )


if __name__ == '__main__':
    app.run(debug=True)
