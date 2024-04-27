from game import Data

def get_subtree_for(tax_id):
    db = Data()
    children = db.get_children(tax_id)
    for child in children:
        yield child

    for child in children:
        yield from get_subtree_for(child)

    return


if __name__ == '__main__':
    tax_id = 219115 # Viverrinae
    db = Data()
    subtree = get_subtree_for(tax_id)

    for s in subtree:
        print(f"{s}: {db.get_name(s)}")
