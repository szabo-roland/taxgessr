import sqlite3
import json
import requests
import random

class Node:
    def __init__(self, db, tax_id):
        self.db = db
        self.tax_id = tax_id
        self.name = db.get_name(tax_id)
        self.alt_names = db.get_translation(tax_id)

    def _to_dict(self):
        return {
            "tax_id": self.tax_id,
            "name": self.name,
            "alt_names": self.alt_names
        }

    def get_parent(self):
        print(f"get_parent {self.tax_id}")
        return self.db.get_parent(self.tax_id)

    def get_children(self):
        print(f"get_children {self.tax_id}")
        children = self.db.get_children(self.tax_id)
        return [Node(self.db, tax_id) for tax_id in children]

    def get_ancestors(self):
        print(f"get_ancestors {self.tax_id}")
        ancestors = self.db.get_ancestors(self.tax_id)
        return [Node(self.db, tax_id) for tax_id in ancestors]

    def get_siblings(self):
        print(f"get_siblings {self.tax_id}")
        parent_id = self.db.get_parent(self.tax_id)
        children = [child_id for child_id in self.db.get_children(parent_id) if child_id != self.tax_id]
        return [Node(self.db, tax_id) for tax_id in children]

    def __format__(self, fmt):
        return f"{self.name}({self.tax_id})"

    @classmethod
    def random_node(cls, db):
        return cls(db.get_random_guessable_id(), db)

class Data:
    instance = None
    @classmethod
    def get_instance(cls):
        if cls.instance:
            return cls.instance

        cls.instance = cls()
        return cls.instance

    @staticmethod
    def connect():
        con = sqlite3.connect('data.db', check_same_thread=False)
        con.row_factory = sqlite3.Row
        return con

    def get_all_guessable(self):
        c = self.con.cursor()
        res = c.execute("select tax_id from images")
        return res

    def get_all_reachable(self):
        c = self.con.cursor()
        res = c.execute("select tax_id from reachable")
        return res

    def __init__(self):
        self.con = self.connect()

    def _query(self, q):
        c = self.con.cursor()
        res = c.execute(q)
        return res

    def query_one(self, q):
        res = self._query(q)
        return res.fetchone()

    def query_all(self, q):
        res = self._query(q)
        return res.fetchall()

    def get_translation(self, tax_id):
        res = self.query_one(f"select en, hu from translations where tax_id={tax_id}")
        if res:
            return {"en": res["en"], "hu": res["hu"]}
        else:
            return {"en": "", "hu": ""}

    def get_name(self, tax_id):
        res = self.query_one(f"select name from names where class='scientific name' and tax_id={tax_id}")
        return res["name"]

    def get_parent(self, tax_id):
        if tax_id == 1:
            return 0
        res = self.query_one(f"select parent_id from nodes where tax_id={tax_id}")
        return int(res["parent_id"])

    def get_children(self, tax_id):
        res = self.query_all(f"select tax_id from nodes where parent_id={tax_id}")
        return [int(row["tax_id"]) for row in res]

    def get_siblings(self, tax_id):
       # print(f"get_siblings({tax_id})")

        parent_id = self.get_parent(tax_id)
        if parent_id == 0:
            return []

        return [child for child in self.get_children(parent_id) if child != tax_id]

    def get_ancestors(self, tax_id):
        # print(f"get_ancestors({tax_id})")
        result = [tax_id]
        while tax_id := self.get_parent(tax_id):
            result.append(tax_id)

        return result

    def get_image_url(self, tax_id):
        res = self.query_one(f"select image_url from images where tax_id={tax_id}")
        if res is None:
            return None

        return res["image_url"]

    def get_random_guessable_id(self, hu_only=False):
        if hu_only:
            return int(self.query_one("select tax_id from images where tax_id in (select tax_id from translations where hu != '') ORDER BY RANDOM() LIMIT 1")["tax_id"])
        return int(self.query_one("select tax_id from images ORDER BY RANDOM() LIMIT 1")["tax_id"])


def _is_bullshit(name):
    for bs in ['unclassified', 'other', 'unknown', 'environmental', 'sample']:
        if bs in name:
            return True
    return False

class Puzzle:
    def __init__(self, tax_id, db=None):
        if db is None:
            db = Data()
        self.node = Node(db, tax_id)
        self.url = db.get_image_url(tax_id)
        self.ancestors = self.node.get_ancestors()[::-1][1:]
        self.other_choices = {ancestor.tax_id: [sibling for sibling in ancestor.get_siblings()  if not _is_bullshit(sibling.name)] for ancestor in self.ancestors}

    @classmethod
    def gen_random(cls, db=None):
        if db is None:
            db = Data()
        tax_id = db.get_random_guessable_id()
        return cls(tax_id, db)

    def pretty_print(self):
        print(f"Puzzle for {self.node}")
        print("Ancestors:")
        for ancestor in self.ancestors:
            print(f"\t{ancestor}")
            print("\tChoices:")
            for choice in self.other_choices[ancestor.tax_id]:
                print(f"\t\t{choice}")

    def _to_dict(self):
        return {
            "node": self.node,
            "url": self.url,
            "ancestors": self.ancestors,
            "other_choices": self.other_choices,
        }

    def to_json(self):
        return json.dumps(self, default=lambda o: o._to_dict())


def get_name_data(db, tax_id, hu_only):
    res = {
        "tax_id": tax_id,
        "sci": db.get_name(tax_id),
        **db.get_translation(tax_id)
    }

    if hu_only:
        res["label"] = f"{res['hu']} / {res['sci']}"
    else:
        res["label"] = res['sci']
        if res['en'] != '' and res['en'] != res['sci']:
            res["label"] += f" / {res['en']}"

        if res['hu'] != '' and res['hu'] != res['sci'] and res['hu'] != res['en']:
            res["label"] += f" / {res['hu']}"

    return res

def has_hun_name(name):
    return name["hu"] != "" and name["hu"] != name["sci"] and name["hu"] != name["en"]

def get_puzzle_data(hu_only, rand, tax_id, errors, progress):
    db = Data.get_instance()

    if rand:
        tax_id = db.get_random_guessable_id(hu_only)

    subject = get_name_data(db, tax_id, hu_only)
    image_url = db.get_image_url(tax_id)
    ancestors = db.get_ancestors(tax_id)[::-1][1:]
    if progress >= len(ancestors):
        return {
            "ancestors": [ancestor for ancestor in [get_name_data(db, ancestor, hu_only) for ancestor in ancestors] if not hu_only or has_hun_name(ancestor)],
            "hu_only": hu_only,
            "image_url": image_url,
            "subject": subject,
            "choices": [],
            "errors": errors,
            "progress": progress,
            "won": True
        }

    ancestor = get_name_data(db, ancestors[progress], hu_only)
    if hu_only:
        if not has_hun_name(ancestor):
            return get_puzzle_data(
                hu_only=hu_only,
                rand=False,
                tax_id=tax_id,
                errors=errors,
                progress=progress+1
            )

    siblings = [sibling for sibling in [get_name_data(db, sibling, hu_only) for sibling in db.get_siblings(ancestor["tax_id"])] if not _is_bullshit(sibling["sci"])]
    if hu_only:
        siblings = [sibling for sibling in siblings if has_hun_name(sibling)]

    if len(siblings) < 1:
        return get_puzzle_data(
            hu_only=hu_only,
            rand=False,
            tax_id=tax_id,
            errors=errors,
            progress=progress+1
        )

    choices = [{"ans": False, **sibling} for sibling in siblings]
    if len(choices) > 5:
        choices = choices[:5]

    choices.append({"ans": True, **ancestor})
    random.shuffle(choices)

    return {
        "hu_only": hu_only,
        "image_url": image_url,
        "subject": subject,
        "choices": choices,
        "errors": errors,
        "progress": progress,
        "won": False,
    }

def main():
    import sys
    db = Data()

    if len(sys.argv) > 1:
        p = Puzzle(sys.argv[1], db)
    else:
        p = Puzzle.gen_random(db)
    p.pretty_print()
    print(p.to_json())

if __name__ == "__main__":
    main()
