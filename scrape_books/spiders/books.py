import scrapy

from scrapy.http import Response
from typing import Any


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs: Any) -> None:
        for book in response.css("article.product_pod"):
            detail_url = response.urljoin(book.css("a::attr(href)").get())
            yield scrapy.Request(
                url=detail_url,
                callback=self._parse_book_detail
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _parse_book_detail(self, response: Response) -> dict[str, Any]:
        yield {
            "title": response.css(
                ".product_main > h1::text"
            ).get(),
            "price": float(response.css(
                ".product_main > .price_color::text"
            ).get().replace("£", "")),
            "amount_in_stock": int(response.css(
                ".product_main > p.instock.availability::text"
            ).getall()[1].replace("\n", "").split()[2].replace("(", "")),
            "rating": int(len([response.css(
                "i.icon-star::text"
            ).getall()])),
            "category": response.css(
                "ul.breadcrumb > li:nth-last-child(2) a::text"
            ).get(),
            "description": response.css(
                "#product_description + p::text"
            ).get(),
            "upc": response.css(
                "table.table-striped > tr:first-child > td::text"
            ).get()
        }
