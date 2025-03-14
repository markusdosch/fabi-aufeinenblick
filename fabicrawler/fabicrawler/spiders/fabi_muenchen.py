import scrapy


class FabiMuenchenSpider(scrapy.Spider):
    name = "fabi-muenchen"
    allowed_domains = ["fabi-muenchen.de"]
    start_urls = ["https://www.fabi-muenchen.de/programm/kw/kathaupt/"]

    def parse(self, response):
        for entry in response.css(".kw-container > .row > .kw-ue"):
            title = entry.css(".row > div:nth-child(1) > .kw-ue-title > a > b::text").get().strip()
            url = entry.css(".row > div:nth-child(1) > .kw-ue-title > a::attr(href)").get()

            start = extract_date_time_parts(entry.css(".row > div:nth-child(1) > .row:nth-child(2) > div:nth-child(2)::text").get().strip())

            location = entry.css(".row > div:nth-child(1) > .row:nth-child(3) > div:nth-child(2)::text").get().strip()

            price = entry.css(".row > div:nth-child(1) > .row:nth-child(4) > div:nth-child(2)::text").get().strip()

            # TODO: Kategorie (via URL?!), z.B. "Fit mit Fabi"
            # TODO: Date => make it ISO & just display that later for simplicity
            # TODO: Extract general standort (e.g. "Neuperlach"). Maybe crawl the standort websites separately, e.g. https://www.fabi-muenchen.de/programm/kw/bereich/suche/suchesetzen/true/?kathaupt=26%3B&suchesetzen=false%3B&kfs_aussenst=Giesing

            spotsleft =  True if "btn-success" in entry.css(".row > div:nth-child(2) > p > a::attr(class)").get() else False

            yield {
                "title": title,
                "url": url,
                "start_weekday": start["weekday"],
                "start_date": start["date"],
                "start_timerange": start["timerange"],
                "location": location,
                "price": price,
                "spots_left": spotsleft
            }
        
        next_page = response.css(".hauptseite_kurse > div > div.kw-paginationleiste.clearfix > div.text-center.kw-pages > ul > li.active.disabled + li > a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

# Sample string: "Mi., 15.01.2025, 19:30 - 20:45 Uhr"
def extract_date_time_parts(input_string):
    parts = [part.strip() for part in input_string.split(',')]

    if len(parts) != 3:
        raise Exception("length != 3")
    
    return {
        'weekday': parts[0],
        'date': parts[1],
        'timerange': parts[2]
    }