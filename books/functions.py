from books.models import Book
from lxml import etree
import requests
import json

def get_authors(book):
    print(book.cnx_id)
    toc_url = 'https://archive.cnx.org/contents/' + book.cnx_id + '.json'
    print(toc_url)
    response = requests.get(toc_url)

    toc = json.loads(response.text)
    preface_id = toc['tree']['contents'][0]['id']
    preface_url = 'https://archive.cnx.org/contents/' + preface_id + '.html'

    response2 = requests.get(preface_url)
    xml = etree.XML(response2.text)
    sa = xml.xpath('//*[@class="sr-contrib-auth"]/x:p/x:strong/text()',namespaces={'x': 'http://www.w3.org/1999/xhtml'})
    if len(sa) == 0:
        sa = xml.xpath('//*[@class="sr-contrib-auth"]/x:p/text()', namespaces={'x': 'http://www.w3.org/1999/xhtml'})

    if book.title == 'Fizyka dla szkół wyższych. Tom 1':
        sa = xml.xpath('//*[@class="sr-contrib-auth"]/x:p/x:span/text()', namespaces={'x': 'http://www.w3.org/1999/xhtml'})

    if book.title == 'Psychology':
        sa.pop(1)

    if book.title == 'Chemistry: Atoms First':
        sa.pop(4)
        sa[3] = remove_last_char(sa[3])

    if book.title == 'Principles of Economics':
        sa.pop(1)
        sa.pop(1)
        sa.pop(1)
        sa.pop(1)
        sa.pop(1)
        sa.pop(2)
        sa.pop(2)
        sa.pop(2)
        sa.pop(2)
        sa.pop(2)


    for item in sa:
        print(item)

    contrib_authors = xml.xpath('//*[@class="contrib-auth"]/x:p/text()', namespaces={'x': 'http://www.w3.org/1999/xhtml'})

    if book.title == 'Fizyka dla szkół wyższych. Tom 1':
        contrib_authors = xml.xpath('//*[@class="contrib-auth"]/x:ul/x:li/text()', namespaces={'x': 'http://www.w3.org/1999/xhtml'})

    if book.title == 'Introduction to Sociology 2e':
        contrib_authors.pop(len(contrib_authors) -1)
        contrib_authors.pop(len(contrib_authors) - 1)
        contrib_authors[0] = remove_last_char(contrib_authors[0])
        contrib_authors[1] = remove_last_char(contrib_authors[1])
        contrib_authors[2] = remove_last_char(contrib_authors[2])
        contrib_authors[6] = remove_last_char(contrib_authors[6])
        contrib_authors[7] = remove_last_char(contrib_authors[7])

    for item in contrib_authors:
        print(item)


def remove_last_char(string_to_change):
    return string_to_change[:-1]



