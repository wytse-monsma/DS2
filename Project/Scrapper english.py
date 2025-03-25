import requests
from bs4 import BeautifulSoup
from pprint import pprint
import json
import os
import sys
import spacy

# Load the small English model
nlp = spacy.load("en_core_web_sm")

def do_request(i):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'cookie': 'cf_clearance=7trrpIMEtE8jAFBAAH1Gn6fCP2FtrR41U89wB.NQ1A8-1742915668-1.2.1.1-hcPPQHwsnpxLL9q6JRvIJYxNL7ilu7VETojnq13fDXiw.Qwg0l_kI08_Y0nwCZq7eGP9qT73nTnOfnIrAcb6D6lsSWHNSbYJ1wwem8lnXyXxgPgOZkgRiJDb.EF_1khhbdy8wmgW2h78Ni6t5Mq_SE6VO3a2pLtDtrNT17UZD.f7T3iXud1FI6UOOYpQC_NZ12a7gS_9OrqHun16CbFGmQ2T28Z70dbJcNEUCbfoCnZ_QySuRHtPm67iKnu1nJ9JYl_5a.OiNKKQluObLe7vuMI95QyM5qzAy30BJXJYbAmwRHFuDNHGOjbL.es1.OkxjS1LcdcNzWNAkJvfPKIU5_YI0KAtxK.dWH3xhbyrcZM; _ga=GA1.1.1578766871.1742915669; _session_id=v0kYsASmj6%2FBvOQ5hwP3Chf1LDfEA2E4BtOn2b4FjUx9BQPAm33XQCXLBf3oLhZfQR2AehuiY1OUgw60JgmsM2KFzg9qmZ7TebYYDm7%2BIh81wk82oBYKUt4Q%2F21hv3%2F0NyIV7y9JixZW54OusipnRaZfudoJdXHyUjzIlUB0524YgD3hCxL58CcAhpuTzSGSV8F%2BwLI8uc6Q92F7l85ONDwhBI78DG2navQX2o90rTqx%2F%2F43B%2FHDAhXWrVZudJpZFWa3uFlF0DnNj0deMZY7DZHJShqXQnGmoYv4duT%2BtYIF9SN1V57IVEY%3D--OnkhGTb63NwccVlz--LzhVa6Z1QjPj4DJQESyiQw%3D%3D; _ga_R3YSZGS0EG=GS1.1.1742915669.1.1.1742915834.0.0.0; _ga_L87M1KQCYY=GS1.1.1742915669.1.1.1742915834.0.0.0',
        'priority': 'u=0, i',
        'referer': 'https://www.britishtheatreguide.info/listings?q=&region=&filter=&running=all',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Opera";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/117.0.0.0',
    }

    params = (
        ('q', ''),
        ('region', ''),
        ('filter', ''),
        ('running', 'all'),
        ('page', str(i)),
    )

    response = requests.get('https://www.britishtheatreguide.info/listings', headers=headers, params=params)

    if response.status_code != 200:
        print(f"Failed to fetch page {i}, status code {response.status_code}")
        return None

    return response.text


def extract_show_info(soup):
    # TODO fix encoding issue

    title = soup.find("h3").text.strip() if soup.find("h3") else ""
    
    authors_text = soup.find("p", class_="authors").text.strip() if soup.find("p", class_="authors") else ""
    
    # Process the sentence
    doc = nlp(authors_text)

    # Extract named entities of type PERSON
    authors = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]

    print(authors_text, authors)

    location = soup.find("div", class_="prod-info").find_all("p")[0].text.strip() if soup.find("div", class_="prod-info") and soup.find("div", class_="prod-info").find_all("p") else ""

    dates = soup.find("div", class_="prod-info").find_all("time") if soup.find("div", class_="prod-info") else []
    start_date = dates[0]["datetime"] if len(dates) > 0 else ""
    end_date = dates[1]["datetime"] if len(dates) > 1 else ""

    # Use replace to get a higher resolution image
    image_url = soup.find("img")["src"].replace("c_fill,f_auto,g_auto,h_100,q_auto,w_100/", "") if soup.find("img") else ""

    return {
        "title": title,
        "authors_text": authors_text,
        "authors": authors,
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "image_url": image_url
    }

if __name__ == '__main__':
    i = 1
    json_path = os.path.join(os.path.dirname(sys.argv[0]), "shows.json")
    # all_shows = json.load(open(json_path))
    all_shows = []
    while True:
        print(f"Fetching page {i}")
        response_text = do_request(i)

        if response_text is None:
            break

        soup = BeautifulSoup(response_text, 'html.parser')

        # Get all divs with id "performance_*" with * a wildcard
        shows = soup.find_all("div", id=lambda x: x and x.startswith("performance_"))
        
        if not shows:
            print("No more shows found")
            break

        for show in shows:
            print(show)
            pprint(extract_show_info(show))
            all_shows.append(extract_show_info(show))
        
        print(all_shows)

        s = json.dumps(all_shows)
        with open(json_path, 'w') as f:
            f.write(s)

        input("Press Enter to continue...")

        i += 1