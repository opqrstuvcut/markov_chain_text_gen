import argparse
import os
import ssl
from urllib import request
from bs4 import BeautifulSoup
import tqdm
# from selenium import webdriver

ssl._create_default_https_context = ssl._create_unverified_context

YUGIOH_URL = "https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=1&sess=1&keyword=&stype=1&ctype=1&starfr=&starto=&pscalefr=&pscaleto=&linkmarkerfr=&linkmarkerto=&link_m=2&atkfr=&atkto=&deffr=&defto=&othercon=2&other=0&rp=100&page={}"
POKEMON_URL = "https://wiki.xn--rckteqa2e.com"


def parse_argument():
    parser = argparse.ArgumentParser("", add_help=True)
    parser.add_argument("--type", "-t", default="pokemon")
    parser.add_argument("--output", "-o", default=os.path.join(os.path.split(__file__)[0], "../data/pokemon.txt"))
    args = parser.parse_args()
    return args


def scaraping_pokemon():
    html = request.urlopen(POKEMON_URL + "/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E4%B8%80%E8%A6%A7")
    top_page = BeautifulSoup(html, "html.parser")
    table = top_page.findAll("table", {"class": "bluetable c sortable"})[0]
    rows = table.findAll("tr")

    texts = []
    for i, row in tqdm.tqdm(enumerate(rows)):
        if i == 0:
            continue
        name_cell = row.findAll("td")[1]
        a_tag = name_cell.find("a")
        target_url = POKEMON_URL + a_tag.get("href")
        target_name = a_tag.text

        # target_html = requests.get(target_url)
        target_html = request.urlopen(target_url)
        target_page = BeautifulSoup(target_html.read())

        for dd in target_page.findAll("dd"):
            row = dd.text.strip()
            if row[1: 3] == "漢字":
                texts.append(row[4:])

    return texts


def scraping_yugioh():
    res = []
    for i in range(1, 8):

        url = YUGIOH_URL.format(i)

        driver = webdriver.PhantomJS(service_log_path=os.path.devnull)
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        cart_box = soup.find("ul", attrs={"class", "box_list"})
        cards = cart_box.find_all("li")

        for li_tag in cards:
            for dl in li_tag.find_all("dl"):
                name = dl.find("dt", attrs={"class", "box_card_name"}).strong.text.strip()
                text = dl.find("dd", attrs={"class", "box_card_text"}).text.strip()

                spec = dl.find("dd", attrs={"class": "box_card_spec"})
                attack = spec.find("span", attrs={"class", "atk_power"}).text.strip()
                defence = spec.find("span", attrs={"class", "def_power"}).text.strip()
                species = spec.find("span", attrs={"class", "card_info_species_and_other_item"}).\
                    text.replace("\n", "").replace("\t", "")
                level = spec.find("span", attrs={"class", "box_card_level_rank"}).span.text.strip()
                attribute = spec.find("span", attrs={"class", "box_card_attribute"}).\
                    span.text.replace("\n", "").replace("\t", "")
                res.append((name, text, attack, defence, species, level, attribute))

    return res


def main():
    args = parse_argument()

    save_dir_path = os.path.split(args.output)[0]
    print(os.path.split(args.output)[0])
    if not os.path.isdir(save_dir_path):
        os.makedirs(save_dir_path)

    with open(args.output, "w") as f:
        if args.type == "yugioh":
            f.write("name,text,attack,defence,species,level,attribute\n")
            for name, text, attack, defence, species, level, attribute in a:
                f.write(",".join([name, text, attack, defence,
                                  species, level, attribute + "\n"]))
        elif args.type == "pokemon":
            texts = scaraping_pokemon()
            for row in texts:
                f.write(row + "\n")
        else:
            raise "Data type you selected is wrong."


if __name__ == "__main__":
    main()
