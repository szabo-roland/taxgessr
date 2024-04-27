from game import Data

def main():
    db = Data()
    g = db.get_all_guessable()
    counter = 0
    m_counter = 0
    while e:= g.fetchone():
        ids = set()
        tax_id = e["tax_id"]
        ids.add(tax_id)
        ancestors = db.get_ancestors(tax_id)
        for ancestor in ancestors:
            ids.add(ancestor)
            siblings = db.get_siblings(ancestor)
            for sibling in siblings:
                ids.add(sibling)

        c = db.con.cursor()
        count_before = c.execute("select count(*) as count from reachable").fetchone()["count"]
        

        for tax_id in ids:
            c = db.con.cursor()
            c.execute("insert or ignore into reachable values(?)", (tax_id,))

        db.con.commit()
        count_after = c.execute("select count(*) as count from reachable").fetchone()["count"]
        print(f"Inserted {count_after - count_before} ids")


main()
