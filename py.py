import os


def solve():
    import requests
    from bs4 import BeautifulSoup

    url = "https://en.wikipedia.org/wiki/Elvis_Presley"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    os.environ["ans"] = str(soup.find_all("p")[:4])


solve()
print(os.environ["ans"])
