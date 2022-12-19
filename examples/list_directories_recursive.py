def solve():
    import os
    for root, dirs, files in os.walk('.'):
        for dir in dirs:
            os.environ['ans'] = os.path.join(root, dir)
solve()
