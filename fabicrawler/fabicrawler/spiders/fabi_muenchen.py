import scrapy
from datetime import datetime


class FabiMuenchenSpider(scrapy.Spider):
    name = "fabi-muenchen"
    allowed_domains = ["fabi-muenchen.de"]
    start_urls = ["https://www.fabi-muenchen.de/programm/kw/kathaupt/"]

    def start_requests(self):
        for i, url in enumerate(self.start_urls):
            yield scrapy.Request(url, meta={"cookiejar": i}, callback=self.parse)

    def parse(self, response):
        for entry in response.css(".kw-container > .row > .kw-ue"):
            title = entry.css(".row > div:nth-child(1) > .kw-ue-title > a > b::text").get().strip()
            url = entry.css(".row > div:nth-child(1) > .kw-ue-title > a::attr(href)").get()

            start = extract_date_time_parts(entry.css(".row > div:nth-child(1) > .row:nth-child(2) > div:nth-child(2)::text").get().strip())
            start_date = datetime.strptime(start["date"], '%d.%m.%Y').date() # Parse into Python native date object => will export as ISO format, e.g. 2025-12-01

            location = entry.css(".row > div:nth-child(1) > .row:nth-child(3) > div:nth-child(2)::text").get().strip()

            price = entry.css(".row > div:nth-child(1) > .row:nth-child(4) > div:nth-child(2)::text").get().strip()

            # TODO: Kategorie (via URL?!), z.B. "Fit mit Fabi"

            spotsleft =  True if "btn-success" in entry.css(".row > div:nth-child(2) > p > a::attr(class)").get() else False

            yield {
                "title": title,
                "url": url,
                "start_weekday": start["weekday"],
                "start_date": start_date,
                "start_timerange": start["timerange"],
                "location": location,
                "price": price,
                "spots_left": spotsleft
            }
        
        next_page = response.css(".hauptseite_kurse > div > div.kw-paginationleiste.clearfix > div.text-center.kw-pages > ul > li.active.disabled + li > a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, meta={"cookiejar": response.meta["cookiejar"]}, callback=self.parse)

# Sample string: "Mi., 15.01.2025, 19:30 - 20:45 Uhr"
# Output: Mi., 15.01.2025, 19:30 - 20:45 Uhr
def extract_date_time_parts(input_string):
    parts = [part.strip() for part in input_string.split(',')]

    if len(parts) != 3:
        raise Exception("length != 3")
    
    return {
        'weekday': parts[0],
        'date': parts[1],
        'timerange': parts[2]
    }