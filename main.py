"""Module providingFunction printing python version."""
import requests
from bs4 import BeautifulSoup
from loguru import logger


def main():
    """Function printing python version."""
    base_url = "https://www.vincebanderos.com"
    params = "toutes-les-filles2.php"
    url = f'{base_url}/{params}'
    response = requests.get(url, proxies={}, timeout=5)
    soup = BeautifulSoup(response.text, "html.parser")
    print(soup.getText)

    parts_list = soup.find_all("td", class_="primcell")
    part_ids = []
    story = []

    for part_item in parts_list:
        part_id = part_item.find("a")["href"].split("=")[1]
        part_ids.append(part_id)

    logger.debug("# found '{}' parts", len(part_ids))

    for p_id in part_ids[0:1]:
        logger.debug("# scraping story '{}'", p_id)

        url = f'{base_url}story.php?id={p_id}'
        logger.debug("## first part from: '{}'", url)
        response = requests.get(url, proxies={}, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find("span", itemprop="articleBody").find_all("p")
        logger.debug("### found '{}' paragraphs", len(paragraphs))
        story = story + paragraphs

        url = f'{base_url}story.php?id={p_id}&rest=1'
        logger.debug("## and rest from: '{}'", url)
        response = requests.get(url, proxies={}, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find("span", itemprop="articleBody").find_all("p")
        logger.debug("### found '{}' paragraphs", len(paragraphs))
        story = story + paragraphs

    logger.debug("# complete story has {} array elements/paragraphs", len(story))

if __name__ == "__main__":
    main()
