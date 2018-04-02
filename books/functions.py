from lxml import etree
import requests
import json

def get_authors(cnx_id, title):
    cnx_domain = 'https://archive.cnx.org'
    toc_url = cnx_domain + '/contents/' + cnx_id + '.json'
    response = requests.get(toc_url)

    toc = json.loads(response.text)
    preface_id = toc['tree']['contents'][0]['id']
    preface_url = cnx_domain + '/contents/' + preface_id + '.html'

    response2 = requests.get(preface_url)
    xml = etree.XML(response2.text)
    sa = xml.xpath('//*[@class="sr-contrib-auth"]/x:p/x:strong/text()',namespaces={'x': 'http://www.w3.org/1999/xhtml'})
    if len(sa) == 0:
        sa = xml.xpath('//*[@class="sr-contrib-auth"]/x:p/text()', namespaces={'x': 'http://www.w3.org/1999/xhtml'})

    if title == 'Fizyka dla szkół wyższych. Tom 1':
        sa = xml.xpath('//*[@class="sr-contrib-auth"]/x:p/x:span/text()', namespaces={'x': 'http://www.w3.org/1999/xhtml'})

    if title == 'Psychology':
        sa.pop(1)

    if title == 'Chemistry: Atoms First':
        sa.pop(4)
        sa[3] = remove_last_char(sa[3])

    if title == 'Principles of Economics':
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

    authors = []
    if len(sa) > 0:
        for item in sa:
            clean_item = item.replace('\n','')
            items = clean_item.split(',')
            if len(items) != 2:
                items.append('')
            authors.append(create_author_obj(items[0], items[1], True, True))


    contrib_authors = xml.xpath('//*[@class="contrib-auth"]/x:p/text()', namespaces={'x': 'http://www.w3.org/1999/xhtml'})

    if title == 'Fizyka dla szkół wyższych. Tom 1':
        contrib_authors = xml.xpath('//*[@class="contrib-auth"]/x:ul/x:li/text()', namespaces={'x': 'http://www.w3.org/1999/xhtml'})

    if title == 'Introduction to Sociology 2e':
        contrib_authors.pop(len(contrib_authors) -1)
        contrib_authors.pop(len(contrib_authors) - 1)
        contrib_authors[0] = remove_last_char(contrib_authors[0])
        contrib_authors[1] = remove_last_char(contrib_authors[1])
        contrib_authors[2] = remove_last_char(contrib_authors[2])
        contrib_authors[6] = remove_last_char(contrib_authors[6])
        contrib_authors[7] = remove_last_char(contrib_authors[7])

    for item in contrib_authors:
        clean_item = item.replace('\n', '')
        items = clean_item.split(',')
        if len(items) == 2:
            authors.append(create_author_obj(items[0], items[1]))

    return authors


def remove_last_char(string_to_change):
    return string_to_change[:-1]


def create_author_obj(author, school='', senior=False, at_top=False):
    if school.strip() == 'PhD':
        school=''
    from books.models import Authors
    return Authors.objects.create(name=author.strip(),
                                 university=school.strip(),
                                 senior_author=senior,
                                 display_at_top=at_top,)




