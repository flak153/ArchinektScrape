import requests
from lxml import html
import csv

LIST_URL = 'https://archinect.com/firms/list/'

urls = (LIST_URL + str(x) for x in range(0, 500, 17))


def num_validate(phone_number):
    return any(str(digit) in phone_number for digit in range(10))


def num_strip(phone_number):
    cleaned = repr(phone_number.replace("\t", " ").strip())
    return cleaned


def profile_scrape(link):
    data = {}
    page = requests.get('https://archinect.com/' + link)
    tree = html.fromstring(page.content)
    data["Name"] = tree.xpath('//h1/a/text()')[0]
    data["Description"] = tree.xpath('//div[@id="ProfileDescription"]/p/text()')

    try:
        follow = tree.xpath('//li[@class="Col1"]/p[@class="last"]/a[contains(text(),"Contact")]/@href')[0]
        page = requests.get('https://archinect.com' + follow)
        tree = html.fromstring(page.content)
        data["Email"] = tree.xpath('//div[@class="Col50"]/a/text()')
        data["Phone"] = [num_strip(number) for number in tree.xpath('//div[@class="Col50"]/text()') if num_validate(number)]
        data["Location"] = [num_strip(address) for address in tree.xpath('//div[@class="Col30"]/text()')]
    except:
        pass

    return data


with open('leads.csv', mode='w') as file:
    fieldnames = ['Name', 'Description', 'Phone', 'Email', 'Location']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for url in urls:
        page = requests.get(url)
        tree = html.fromstring(page.content)
        links = tree.xpath('//a[@class="ThumbA"]/@href')

        for link in links:
            print(profile_scrape(link))
            writer.writerow(profile_scrape(link))
