from flask import Flask, jsonify
import json
import pandas
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)


class Scraper:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.quotes_list = []

    def get_quotes(self):
        res = requests.get(self.url, headers=self.headers)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            contents = soup.find_all("div", attrs={"class": "quote"})
            for content in contents:
                quote = content.find("span", attrs={"class": "text"}).text.strip()
                author = content.find("small", attrs={"class": "author"}).text.strip()
                author_detail = content.find("a")["href"]
                data_dict = {
                    "quote": quote,
                    "quotes by": author,
                    "author detail": self.url + author_detail
                }
                self.quotes_list.append(data_dict)

            with open("quotes.json", "w+") as file:
                json.dump(self.quotes_list, file)
            print("Berhasil menyimpan data ke dalam file quotes.json")

    def get_detail(self, detail_url):
        res = requests.get(detail_url, headers=self.headers)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            author_title = soup.find("h3", attrs={"class": "author-title"}).text.strip()
            author_born = soup.find("span", attrs={"class": "author-born-date"}).text.strip()
            author_born_location = soup.find("span", attrs={"class": "author-born-location"}).text.strip()
            description = soup.find("div", attrs={"class": "author-description"}).text.strip()
            data_dict = {
                "author": author_title,
                "born": author_born,
                "born location": author_born_location,
                "description": description
            }
            return data_dict

    def generate_format(self, filename, result):
        df = pandas.DataFrame(result)
        if ".csv" or ".xlsx" not in filename:
            df.to_csv(filename + ".csv", index=False)
            df.to_excel(filename + ".xlsx", index=False)
        print("DONE!!!")

    def crawling(self):
        result = []
        self.get_quotes()

        for quote in self.quotes_list:
            detail = self.get_detail(quote["author detail"])
            final_result = {**quote, **detail}
            result.append(final_result)

        self.generate_format("reports", result)
        return result


@app.route('/')
def index():
    scraper = Scraper(url="https://quotes.toscrape.com", headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    })
    results = scraper.crawling()
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)