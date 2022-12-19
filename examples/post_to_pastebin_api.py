def solve():
    import requests
    import os

    url = "https://pastebin.com/api/api_post.php"
    data = {
        "api_dev_key": "<YOUR_API_KEY>",
        "api_option": "paste",
        "api_paste_code": "print('Hello World')",
        "api_paste_name": "Example of Posting to Pastebin API",
    }
    response = requests.post(url, data=data)
    os.environ["ans"] = response.text

solve()
