import logging
import requests
import json
from bs4 import BeautifulSoup
from pathlib import Path

logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')


class TravelScraper:
    """
        A web scraper for travel destinations.

        Attributes:
            url: The URL of the website to scrape.
            data_file: The file to save scraped data to.
            destinations: A list of dictionaries containing data for each destination.

    """

    def __init__(self, url: str, data_file: str) -> None:
        self.url = url
        self.data_file = Path(data_file)
        self.destinations = []

    def run(self) -> None:
        """
            Run the scraper to retrieve and save data for all destinations.
        """
        try:
            self.scrape_destination_links()
            self.scrape_destination_data()
            self.save_destination_data()
        except Exception as e:
            logging.exception(f"An error occurred during the scraping process: {str(e)}")

    def scrape_destination_links(self) -> None:
        """
            Scrape the website to get links to each destination page.
        """
        logging.info("Scraping destination links...")
            
        try:
            res = requests.get(self.url)
            content = res.content
            soup = BeautifulSoup(content, 'html.parser')
            destination_links = [self.url + link.attrs['href']
                                 for link in soup.find_all(name='a', class_='uitk-card-link')]
            self.destination_links = destination_links
        except Exception as e:
            logging.exception(f"An error occurred while scraping destination links: {str(e)}")

        logging.info(f"Scraped {len(destination_links)} destination links")

    def scrape_destination_data(self) -> None:
        """
            Scrape each destination page to retrieve data.
        """
                
        logging.info("Scraping destination data...")
                        
        for i, link in enumerate(self.destination_links):
            logging.info(f"Scraping destination {i+1}/{len(self.destination_links)}: {link}")
            try:
                res = requests.get(link)
                content = res.content
                soup = BeautifulSoup(content, 'html.parser')

                destination_name = soup.find(name='h1', class_='uitk-heading uitk-heading-1').string

                gallery = [img.attrs['src'].replace("mediumHigh", "High")
                           for img in soup.select(".GalleryMosaic--5 img")]

                place_of_interest = [{"name": place.string, "url": self.url + place.attrs['href']}
                                     for place in soup.select('a[href*=".Attraction"]')]

                data = {"name": destination_name, "gallery": gallery, "places of interest": place_of_interest}

                self.destinations.append(data)
            except Exception as e:
                logging.exception(f"An error occurred while scraping destination data: {str(e)}")

    def save_destination_data(self) -> None:
        """
            Save the scraped destination data to a file.
        """
        logging.info(f"Saving scraped data to {self.data_file}...")
        try:
            with open(self.data_file, 'w') as file:
                json.dump(self.destinations, file, indent=4)
        except Exception as e:
            logging.exception(f"An error occurred while saving destination data: {str(e)}")
        
        logging.info("Scraping complete.")


if __name__ == '__main__':
    url = "https://euro.expedia.net/"
    data_file = Path(__file__).resolve().parent / 'data.json'
    scraper = TravelScraper(url, data_file)
    scraper.run()
