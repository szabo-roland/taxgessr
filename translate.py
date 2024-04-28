from game import Data
import requests
import json
from get_subtree import get_subtree_for
from urllib.parse import unquote

def translate_name(name):
    result = {"hu": "", "en": ""}
    r = requests.get(f"https://en.wikipedia.org/w/api.php?action=parse&format=json&redirects=1&page={name}&formatversion=2")
    j = json.loads(r.text)

    if "parse" in j and "title" in j["parse"]:
        result["en"] = j["parse"]["title"]

    r = requests.get(f"https://hu.wikipedia.org/w/api.php?action=parse&format=json&redirects=1&page={name}&formatversion=2")
    j = json.loads(r.text)

    if "parse" in j and "title" in j["parse"]:
        result["hu"] = j["parse"]["title"]

    return result["en"], result["hu"]

def gen_retriables(db):
    cur = db.con.cursor()
    res = cur.execute("select tax_id, en from translations where hu='' and en != ''");
    yield {
        "tax_id": 71240,
        "en": "Eudicots"
    }

    while r := res.fetchone():
        yield r

    return

def translation_langlink(name):
    r = requests.get(f"https://en.wikipedia.org/w/api.php?action=parse&format=json&redirects=1&page={name}&formatversion=2")
    j = json.loads(r.text)

    for langlink in j["parse"]["langlinks"]:
        if langlink["lang"] == "hu":
            possible_name = unquote(langlink["url"].removeprefix("https://hu.wikipedia.org/wiki/"))
            r = requests.get(f"https://hu.wikipedia.org/w/api.php?action=parse&format=json&redirects=1&page={possible_name}&formatversion=2")
            j = json.loads(r.text)
            if "parse" in j and "title" in j["parse"]:
                return j["parse"]["title"]
            else:
                return None

    return None

def main_new():
    db = Data()
    retriables = gen_retriables(db)
    for retriable in retriables:
        tax_id = retriable["tax_id"]
        name = retriable["en"]
        hu = translation_langlink(name)
        if hu is not None:
            print('!', end='')
            with open("new_translations.sql", "a") as f:
                f.write(f"UPDATE translations SET hu='{hu}' WHERE tax_id={tax_id}\n")
        else:
            print(".", end='')


def main():
    db = Data()
    g = db.get_all_reachable()
    counter = 0
    m_counter = 0
    subtree = get_subtree_for(33208)
    for tax_id in subtree:
        m_counter += 1
        if m_counter % 100 == 0:
            print(f"progress {m_counter}")
        if not db.get_translation(tax_id):
            name = db.get_name(e["tax_id"])
            en, hu = translate_name(name)
            c = db.con.cursor()
            print(f"{name} -> {en}, {hu}")
            print(f"insert into translations values {tax_id}, '{en}', '{hu}'")
            res = c.execute("insert into translations values (?, ?, ?)", (tax_id, en, hu))
            counter += 1
            if counter >= 10:
                counter = 0
                print("Commiting")
                db.con.commit()


if __name__ == '__main__':
    #main()
    main_new()
