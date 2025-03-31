import scrapy
import re
from datetime import datetime

category_pattern = r"https://www\.fabi-muenchen\.de/programm/([^/]+)"


class FabiMuenchenSpider(scrapy.Spider):
    name = "fabi-muenchen"
    allowed_domains = ["fabi-muenchen.de"]
    # start_urls = ["https://www.fabi-muenchen.de/programm/kw/kathaupt/"]
    
    def start_requests(self):
        return [
            scrapy.Request(
                "https://www.fabi-muenchen.de/programm/kw/kathaupt/1?katasfilter[]="+location+"&katasfilter[]=__reset__",
                meta={"cookiejar": location, "blub": location},
                callback=self.after_request,
            ) for location in ["Giesing", "Milbertshofen", "Neuperlach", "Online-Angebot", "Pasing", "Thalkirchen"]
        ]

    def after_request(self, response):
        for entry in response.css(".kw-container > .row > .kw-ue"):
            title = entry.css(".row > div:nth-child(1) > .kw-ue-title > a > b::text").get().strip()
            url = entry.css(".row > div:nth-child(1) > .kw-ue-title > a::attr(href)").get()

            start = extract_date_time_parts(entry.css(".row > div:nth-child(1) > .row:nth-child(2) > div:nth-child(2)::text").get().strip())
            start_date = datetime.strptime(start["date"], '%d.%m.%Y').date() # Parse into Python native date object => will export as ISO format, e.g. 2025-12-01

            location = response.meta["blub"]
            location_exact = entry.css(".row > div:nth-child(1) > .row:nth-child(3) > div:nth-child(2)::text").get().strip()

            price = entry.css(".row > div:nth-child(1) > .row:nth-child(4) > div:nth-child(2)::text").get().strip()

            category_match = re.search(category_pattern, url)

            category="?"
            if category_match:
                category = category_match.group(1)

            spotsleft =  "✅" if "btn-success" in entry.css(".row > div:nth-child(2) > p > a::attr(class)").get() else "❌"

            yield {
                "title": title,
                "category": category,
                "url": url,
                "start_weekday": start["weekday"],
                "start": start_date.isoformat() + ", " + start["timerange"],
                "location": location,
                "location_exact": location_exact,
                "price": price,
                "spots_left": spotsleft
            }
        
        next_page = response.css(".hauptseite_kurse > div > div.kw-paginationleiste.clearfix > div.text-center.kw-pages > ul > li.active.disabled + li > a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, meta={"cookiejar": response.meta["cookiejar"], "blub": response.meta["blub"]}, callback=self.after_request)

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