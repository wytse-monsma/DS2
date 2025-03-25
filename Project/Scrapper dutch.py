import requests
from bs4 import BeautifulSoup
from pprint import pprint
import json
import os
import sys
from datetime import datetime

def do_request(i):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'cookie': 'PHPSESSID=n6jevmtugp44649httl7q34fq1; __eoi=ID=2f02aee74084d17d:T=1729769446:RT=1742911618:S=AA-AfjZspqVxhMSChto416ZOwi2s',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Opera";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/117.0.0.0',
    }

    params = (
        ('start', str(i)),
    )

    response = requests.get('https://www.theater.nl/voorstellingen', headers=headers, params=params)

    if response.status_code != 200:
        print(f"Failed to fetch page {i}, status code {response.status_code}")
        return None

    return response.text


def extract_show_info(soup):
    # TODO fix encoding issue

    # Title
    title = soup.find("meta", itemprop="name")["content"].strip()

    # Artists (could be more than one performer blocks)
    artists = [tag["content"] for tag in soup.find(itemprop="performer").find_all("meta", itemprop="name")]

    # Description
    short_description = soup.select_one(".show__description p:nth-of-type(2)").text.strip()

    # Genre and price
    genre_price_text = soup.select_one(".show__description .grayed").text
    genre_part, price_part = genre_price_text.split(" - €")
    genres = [g.strip() for g in genre_part.split(",")]
    price = float(price_part.replace(",", "."))

    # Date and time
    # date = datetime.strptime(soup.select_one('[itemprop="startDate"]')["content"], "%Y-%m-%d %H:%M:%S")
    date = soup.select_one('[itemprop="startDate"]')["content"]

    # Location
    location = soup.select_one('[itemprop="location"] meta[itemprop="name"]')["content"]

    # Output dictionary
    return {
        "title": title,
        "artists": artists,
        "short_description_dutch": short_description,
        "genre": genres,
        "price_eur": price,
        "date": date,
        "location": location
    }

    

if __name__ == '__main__':
    i = 0
    json_path = os.path.join(os.path.dirname(sys.argv[0]), "shows.json")
    # all_shows = json.load(open(json_path))
    all_shows = []
    while True:
        print(f"Fetching shows {i} - {i + 10}")
        response_text = do_request(i)

        if response_text is None:
            break

        soup = BeautifulSoup(response_text, 'html.parser')

        # Get all divs with class "showlist__show voorstelling_*" with * a wildcard
        shows = soup.find_all('div', class_=lambda x: x and x.startswith('showlist__show voorstelling_'))
        
        if not shows:
            print("No more shows found")
            break

        for show in shows:
            print(show)
            print(type(show))
            pprint(extract_show_info(show))
            all_shows.append(extract_show_info(show))
        
        print(all_shows)


        s = json.dumps(all_shows)
        with open(json_path, 'w') as f:
            f.write(s)

        input("Press Enter to continue...")

        i += 10