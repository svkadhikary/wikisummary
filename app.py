import os
from flask import Flask, request, render_template, redirect
from wikiSearch import WikiSearch
from webdriver_manager.chrome import ChromeDriverManager
from mongodbOperations import MongoDBOperations
import threading

app = Flask(__name__)

title, body_summary, images_encoded, references = "", "", [], []
db_name = "WikiSummary"


class ThreadClass:

    def __init__(self, wiki_obj, search_string):
        self.wiki_obj = wiki_obj
        self.search_string = search_string
        self.lock = threading.Lock()

        thread = threading.Thread(target=self.scrap)
        thread.daemon = True
        thread.start()
        thread.join()

    def scrap(self):
        self.lock.acquire()
        global title, body_summary, images_encoded, references
        record = self.wiki_obj.wiki_scrapper(self.search_string)
        title = record["title"]
        body_summary = record["summary"]
        images_encoded = record["images"]
        references = record["references"]
        self.lock.release()


@app.route('/')
def index_page():
    return render_template('index.html')


@app.route('/summary', methods=["POST", "GET"])
def summary():
    if request.method == 'POST':
        search_string = request.form['term']
        if search_string == "":
            return redirect('/')

        wiki_obj = WikiSearch(ChromeDriverManager().install(), db_name)
        try:
            thread = ThreadClass(wiki_obj, search_string)
        except Exception as e:
            raise Exception("Error: \t" + str(e))


        # images = os.listdir(os.path.join(app.static_folder, "images"))
        return render_template('summary.html', heading=title, summary=body_summary, images=images_encoded, references=references)


if __name__ == '__main__':
    app.run(debug=True)
