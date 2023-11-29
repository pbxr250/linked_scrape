import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import json
import os
import csv
import logging
from scrapy.utils.log import configure_logging 
from scrapy.selector import Selector

from scrapy.utils.reactor import install_reactor 
install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor') 

from scrapy_playwright.page import PageMethod

# link to scrape
LINK = 'https://www.linkedin.com/jobs/search?keywords=React&location=Poland&locationId=&geoId=105072130&f_TPR=r604800&position=1&pageNum=0'



class JobsSpider(scrapy.Spider):
    name = 'jobs'
    start_urls = [
        LINK,
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # python3

    def start_requests(self):
        # GET request
        yield scrapy.Request(LINK, meta=dict(
				playwright = True,
				playwright_include_page = True,
                errback=self.errback,
            ))
				#playwright_page_methods =[PageMethod('wait_for_selector', 'ul.jobs-search__results-list')],
			    #))
        

    async def parse(self, response):
        page = response.meta["playwright_page"]
        #await page.close()

        # for jobpan in response.css("ul.jobs-search__results-list li"):
        #     css_selector = jobpan.__repr__()
        #     jdiv = await page.wait_for_selector(css_selector)
        #     await jdiv.click()
            

        elHandle_joblisting = await page.query_selector_all('ul.jobs-search__results-list li')
        counter = 1
        for elHandle_li in elHandle_joblisting:
            await page.wait_for_timeout(1000)

            elHandle_jobpan = await elHandle_li.query_selector('div')
            await elHandle_jobpan.click()
            jobpan_html = await elHandle_jobpan.inner_html()
            scrapy_jobpan = Selector(text = jobpan_html)

            try:
                elHandle_details = await page.wait_for_selector('div.description__text.description__text--rich', timeout = 1000)
                details_html = await elHandle_details.inner_html()
                scrapy_details = Selector(text = details_html)
                job_title = scrapy_jobpan.css('div.base-search-card__info h3::text').get().strip()
                job_comp = scrapy_jobpan.css('div.base-search-card__info h4 a::text').get().strip()
                #job_details = scrapy_details.css(' *::text').get().strip()
                job_details = scrapy_details.xpath('string()').get()
                #job_html = scrapy_details.css('').get()
                job_html = details_html
            except Exception as e:
                logging.warning(e.message)
                job_details = 'timeout'
                job_html = 'timeout'
                
            result = {
                'title' : job_title,
                'company': job_comp,
                'details': job_details,
                'html': job_html
            }
            yield result
            
            counter += 1
            #if counter == 10:
            #    break
    
    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

    # next_page = response.css('li.next a::attr("href")').get()
    # if next_page is not None:
    # yield response.follow(next_page, self.parse)


class CustomPipeline:
    def __init__(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        output_path = os.path.join(script_dir, 'output.json')
        self.file = open(output_path, 'w')

    def process_item(self, item, spider):
        brief = {k:v for (k,v) in item.items() if k!='details' if k != 'html'}
        line = json.dumps(brief) + "\n"
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()

class HtmlPipeline:
    def __init__(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        output_path = os.path.join(script_dir, 'site.html')
        self.file = open(output_path, 'w')

    def process_item(self, item, spider):
        headLine = f'<br><h1 style="color:#005aff;">Title: {item["title"]}</h1><h2 style="color:#fc730ae0;">Company: {item["company"]}</h2><br>\n'
        self.file.write(headLine)
        line = item['html'] + "\n"
        self.file.write(line)
        footerline = '<br><hr class="rounded"><br>\n'
        self.file.write(footerline)
        return item

    def close_spider(self, spider):
        self.file.close()


class CSVPipeline:
    def __init__(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.csv_file = open(os.path.join(script_dir, 'output.csv'), 'w', encoding='utf-8', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['author', 'text'])

    def process_item(self, item, spider):
        self.csv_writer.writerow([item['author'], item['text']])
        return item

    def close_spider(self, spider):
        self.csv_file.close()


def init():
    settings_path = 'settings' # The path seen from root
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_path)
    settings = get_project_settings()
   
    process = CrawlerProcess(settings)
    #print(f"Existing settings: {process.settings.attributes.values()}")

    process.crawl(JobsSpider)
    
    process.start()

init()