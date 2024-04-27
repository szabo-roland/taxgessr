from game import Data
import requests
import json

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

def main():
    db = Data()
    g = db.get_all_reachable()
    counter = 0
    m_counter = 0
    while e:= g.fetchone():
        m_counter += 1
        tax_id = e["tax_id"]
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
    main()
