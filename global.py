import requests
from bs4 import BeautifulSoup

def get_tickers_from_wikipedia(url):
    """
    This function scrapes the list of stock tickers from a Wikipedia page.
    We will scrape multiple pages for different stock exchanges.
    """
    tickers = []
    try:
        # Send HTTP request to the URL
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all rows in the table that list tickers
        rows = soup.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 0:
                # Extract the ticker symbol from the first column
                ticker = cols[0].text.strip()
                if ticker:  # Ensure ticker is not empty
                    tickers.append(ticker)
    except Exception as e:
        print(f"Error while scraping {url}: {e}")

    return tickers

def write_tickers_to_file(tickers, filename):
    """
    This function writes the list of tickers to a text file.
    """
    with open(filename, 'w') as file:
        for ticker in tickers:
            file.write(f"{ticker}\n")

def main():
    # List of Wikipedia pages for stock exchanges
    wikipedia_urls = [
        "https://en.wikipedia.org/wiki/List_of_companies_listed_on_the_New_York_Stock_Exchange",
        "https://en.wikipedia.org/wiki/List_of_companies_listed_on_the_NASDAQ",
        "https://en.wikipedia.org/wiki/List_of_companies_listed_on_the_Toronto_Stock_Exchange",
        "https://en.wikipedia.org/wiki/List_of_companies_listed_on_the_London_Stock_Exchange",
        "https://en.wikipedia.org/wiki/List_of_companies_listed_on_the_Hong_Kong_Stock_Exchange",
        # Add more URLs for other stock exchanges as needed
    ]

    # List to hold tickers from all sources
    all_tickers = []

    for url in wikipedia_urls:
        print(f"Scraping {url}...")
        tickers = get_tickers_from_wikipedia(url)
        print(f"Found {len(tickers)} tickers from {url}")
        all_tickers.extend(tickers)

    # Remove duplicates by converting to a set, then back to a list
    unique_tickers = list(set(all_tickers))

    # Write the tickers to a file
    write_tickers_to_file(unique_tickers, 'global_stock_universe.txt')

    print(f"Saved {len(unique_tickers)} unique tickers to 'global_stock_universe.txt'")

if __name__ == "__main__":
    main()
