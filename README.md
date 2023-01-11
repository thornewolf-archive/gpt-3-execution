<h1>GPT-3xecute</h1>
<p align="center">An AI assistant that write and execute code for you.</p>

<p align="center">
  <a href="https://github.com/usememos/memos/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/thornewolf/gpt-3-execution" /></a>
</p>

<img width="564" alt="image" src="https://user-images.githubusercontent.com/16554266/208806066-bfb1a9e2-4fbb-4912-a0c7-5e91ead71e44.png">

## Features

With some clever prompt engineering, OpenAI's text-davinci-003 has been given the capability to write and execute code to enable it to answer complex questions and accomplish multiple tasks. Some example tasks include:
- Answering complex math questions correctly
- Fetching the contents of an article on wikipedia
- Writing to and reading from local files

## How do I use this?
Currently, this is a self-host only solution. This repository allows GPT-3 to run arbitrary python code on your computer so don't ask it to do anything dangerous!

1. Make a telegram account and creating a new bot by talking to "BotFather" on Telegram. Follow instruction #1 [here](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-channel-connect-telegram?view=azure-bot-service-4.0) for an example.
1. Make an OpenAI account and generate a new secret key [here](https://beta.openai.com/account/api-keys).
1. Store the API keys that your generated in a `.env` file. See `.env.example` for the format you should use.
1. Install the python dependencies and run!

### Installing Python Dependencies
```
pip install -r requirements.txt
```
### Your .env File
follow .env.example to create .env file
```
TELEGRAM_API_KEY = "foo"
OPENAI_API_KEY = "bar"
```
### Run!
```
python main.py
```

## Examples
<img width="608" alt="image" src="https://user-images.githubusercontent.com/16554266/208807953-c959289b-5714-4d00-9251-46ac6ea54cd6.png">
<img width="607" alt="image" src="https://user-images.githubusercontent.com/16554266/208808645-c6c4e8c6-bd40-450b-84c5-27dca7284ad5.png">