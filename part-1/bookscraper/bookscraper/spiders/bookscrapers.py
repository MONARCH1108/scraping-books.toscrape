import scrapy


class BookscrapersSpider(scrapy.Spider):
    name = "bookscrapers"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        books = response.css('article.product_pod')
        for book in books:
            relative_Url = book.css('h3 a').attrib['href']

            if 'catalogue/' in relative_Url: 
                book_url = 'https://books.toscrape.com/' + relative_Url   
            else:
                book_url = 'https://books.toscrape.com/catalogue/' + relative_Url
            yield scrapy.Request(book_url, callback=self.parse_book_page)

        next_page=response.css('li.next a ::attr(href)').get()  
        if next_page is not None:
            if 'catalouge/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalouge/' + next_page
                
            yield response.follow(next_page_url, callback=self.parse)
            

    def parse_book_page(self,response):
        book = response.css("div.product_main")[0]
        table_rows=response.css("table tr")
        yield{
            'url' : response.url,
            'title': response.css('.product_main h1::text').get(),
            'product_type':table_rows[1].css("td::text").get(),
            'price_excl_tax':table_rows[2].css("td::text").get(),
            'price_incel_tax':table_rows[3].css("td::text").get(),
            'tax':table_rows[4].css("td::text").get(),
            'stars': response.css('p.star-rating').attrib['class'],
            'category': book.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get(),
            'description':response.xpath('//*[@id="content_inner"]/article/p/text()').get(),
            'price':response.css('p.price_color::text').get(),
        }