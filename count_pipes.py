import sys

def count_pipes(s):
    return s.count('|')


for path in sys.argv[1:]:
    pipes = set()
    with open(path) as f:
        while line:= f.readline():
            pipes.add(count_pipes(line))

    print(f"{path}: {pipes}")
