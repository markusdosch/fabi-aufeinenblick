import scrapy


class FabiMuenchenSpider(scrapy.Spider):
    name = "fabi-muenchen"
    allowed_domains = ["fabi-muenchen.de"]
    start_urls = ["https://www.fabi-muenchen.de/programm/kw/kathaupt/"]

    def parse(self, response):
        for entry in response.css(".kw-container > .row > .kw-ue"):
            yield {
                "title": entry.css(".row > div:nth-child(1) > .kw-ue-title > a > b::text").get().strip(),
                "url": entry.css(".row > div:nth-child(1) > .kw-ue-title > a::attr(href)").get(),
                "start": entry.css(".row > div:nth-child(1) > .row:nth-child(2) > div:nth-child(2)::text").get().strip(),
                "location": entry.css(".row > div:nth-child(1) > .row:nth-child(3) > div:nth-child(2)::text").get().strip(),
                "price": entry.css(".row > div:nth-child(1) > .row:nth-child(4) > div:nth-child(2)::text").get().strip(),
                "spotsleft": True if "btn-success" in entry.css(".row > div:nth-child(2) > p > a::attr(class)").get() else False
            }
        
        next_page = response.css(".hauptseite_kurse > div > div.kw-paginationleiste.clearfix > div.text-center.kw-pages > ul > li.active.disabled + li > a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)