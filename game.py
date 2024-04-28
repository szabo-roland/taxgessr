import sqlite3
import json
import requests

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
    @staticmethod
    def connect():
        con = sqlite3.connect('data.db')
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
        res = self.query_one(f"select * from translations where tax_id={tax_id}")
        if res:
            return [res["en"], res["hu"]]
        else:
            return ["", ""]

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
        result = []
        while tax_id := self.get_parent(tax_id):
            result.append(tax_id)

        return result

    def get_image_url(self, tax_id):
        res = self.query_one(f"select image_url from images where tax_id={tax_id}")
        if res is None:
            return None

        return res["image_url"]

    def get_random_guessable_id(self):
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
