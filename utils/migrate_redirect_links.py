import MySQLdb
import psycopg2
from re import search


mysql_settings = { 'user': 'root',
                   'host': 'localhost',
                   'db': 'osc',}

postgres_settings = { 'database': 'openstax',
                      'user': 'postgres',}

exclude_patterns = [ r'openstaxcollege.org']


con = MySQLdb.connect(**mysql_settings)
with con:
    cur = con.cursor()
    cur.execute("SELECT id, url, short_code FROM links WHERE CHAR_LENGTH(url) <= 200")
    links = cur.fetchall()
    cur.execute("SELECT id, url, short_code FROM links WHERE CHAR_LENGTH(url) > 200")
    invalid_links = cur.fetchall()

excluded_links = []
for link in links:
    (dbid, url, short_code)=link
    for pattern in exclude_patterns:
        if search(pattern,url):
            excluded_links.append(link)

links = [ link for link in links if link not in excluded_links] 
        

# Include l/ prefix to short_codes to prevent potential routing conflicts
links = [ (dbid, url, 'l/' + short_code) for (dbid, url, short_code) in links ]

with psycopg2.connect(**postgres_settings) as con:
    with con.cursor() as cur:
        cur.execute("SET CLIENT_ENCODING TO 'LATIN1';")
        query = "INSERT INTO wagtailredirects_redirect (id, redirect_link, old_path, is_permanent) VALUES (%s, %s, %s, true)"
        cur.executemany(query,links)

print("Any links not imported will be written to skipped_links.csv")
with open("skipped_links.csv","w") as f:
    f.write("id, url, short_code\n") # include headers
    if invalid_links:
        print("there are {0} links that are too long to be imported".format(len(invalid_links)))
        for (dbid, url, short_code) in invalid_links:
            f.write("{0}, {1}, {2}\n".format(dbid, url, short_code))
    if excluded_links:
        print("there are {0} links that were excluded based on their patterns".format(len(excluded_links)))
        for (dbid, url, short_code) in excluded_links:
            f.write("{0}, {1}, {2}\n".format(dbid, url, short_code))
    if not invalid_links and not excluded_links:
        print("No links skipped during migration")

print("DONE!")
