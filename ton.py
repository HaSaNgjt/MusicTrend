import requests
import telebot
import traceback
from config import Config 
token = Config.token
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, """*Welcome to the bot ton
I do some simple orders
1- /start • Starting Message •
- - - - - - - - - - - - - - - - - 
2- /price • To know the price of the ton 
- - - - - - - - - - - - - - - - - 
3- /nft + User • To check whether the Username is Nft or not
- - - - - - - - - - - - - - - - - 
4- /user + • Address of a specific person To show the names of the NFT users they own • 
- - - - - - - - - - - - - - - - - 
5 - /Address - + username A specific person to display his Address with the usernames he owns *

6 - /info + username - • Display information for a specific username •
""",
                 parse_mode="Markdown")


@bot.message_handler(commands=['price'])
def price(message):
    req = requests.get("https://api.tonkeeper.com/stock/chart-new?period=1H")
    data = req.json()
    price = data['data'][6]['y']
    rou = round(price, 2)
    fomr = str(rou)
    bot.reply_to(message, f"*The current price ton is : {fomr}*",
                 parse_mode="Markdown")


@bot.message_handler(commands=['info'])
def inf(message):
    user = message.text.split()[1]
    result = info(message, user)
    bot.reply_to(message, result)


def info(message, user):
    try:
        chat_id = message.chat.id
        img = f'https://nft.fragment.com/username/{user}.webp'
        response = requests.get(f"https://fragment.com/username/{user}")
        soup = BeautifulSoup(response.content, 'html.parser')
        sold = re.findall(r'table-cell-value tm-value icon-before icon-ton">(.*?)<', str(soup))
        token = re.findall(r'tm-section-header-status tm-status-unavail">(.*?)<', str(soup))
        if token:
            bot.send_photo(chat_id, img, caption=f'* This username is sold and is  : {token[0]}\nIt was sold at a price : {sold[0]}*', parse_mode="Markdown")
        else:
            raise Exception("Empty token")
    except:
        try:
            response2 = requests.get(f"https://fragment.com/username/{user}")
            soup2 = BeautifulSoup(response2.content, 'html.parser')
            max = re.findall(r'icon-before icon-ton tm-amount js-bid_value">(.*?)<', str(soup2))
            token2 = re.findall(r'tm-section-header-status tm-status-avail">(.*?)<', str(soup2))
            if token2 and token2[0] == "Available":
            
                bot.send_photo(chat_id, img, caption=f'*This username is available for auction if:{token2[0]}\n Minimum bid : {max[0]}*', parse_mode="Markdown") 
            else:
                
                response3 = requests.get(f"https://fragment.com/username/{user}")
                soup3 = BeautifulSoup(response3.content, 'html.parser')
                max2 = re.findall(r'table-cell-value tm-value icon-before icon-ton">(.*?)<', str(soup3))
                token3 = re.findall(r'tm-section-header-status tm-status-avail">(.*?)<', str(soup3))
                if token3:
                    bot.send_photo(chat_id, img, caption=f'* This username is in the bidding and is in the case of : {token3[0]}\n Current highest bid : {max2[0]}*', parse_mode="Markdown")
                else:
                    return "an error occurred . Verify that the username is NFT"
        except:
            return "حدث خطأ ما"

            
@bot.message_handler(commands=['nft'])
def checknft(message):
    try:
        chat_id = message.chat.id
        user = message.text.split()[1]
        img = f'https://nft.fragment.com/username/{user}.webp'
        bot.send_photo(chat_id, img, caption=f'*Yes, this is the nft : {user}*', parse_mode="Markdown")
    except:
        bot.reply_to(message, f'*Sorry, this username is not nft : {user}*', parse_mode="Markdown")


from bs4 import BeautifulSoup
import re


# Thank you t.me/Onlydragon for the API
@bot.message_handler(commands=['Address'])
def Address(message):
    try:
        chat_id = message.chat.id
        user = message.text.split()[1]
        url = f"https://fragment.com/username/{user}"

        rsl = requests.get(url)
        soup = BeautifulSoup(rsl.content, 'html.parser')
        token = re.findall("href=\"(.*?)\"", str(soup.find("a", attrs={'class': 'tm-wallet'})))
        token = str(token[0].replace('https://tonviewer.com/', ''))
        req = requests.get(f"https://tonapi.io/v2/accounts/{token}/nfts").json()["nft_items"]

        ton = f"https://tonviewer.com/{token}"
        response = requests.get(ton)
        content = response.content.decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        div = soup.find('div', class_='b1pacd95')
        text = div.text.strip()
        value = text.split()[0]

        usernames = []
        for c in req:
            try:
                usernames.append(c["metadata"]["name"])
            except:
                pass
        bot.reply_to(message, f"""User address : {token}\n\nThe number of tons he owns : {value} \n\nHis usernames : \n""" + ' '.join([f'{username}' for username in usernames]))
                     
    except Exception as e:
        traceback.print_exc()
        bot.reply_to(message, f'*Sorry, an error occurred: {e}*')
# Thank you t.me/Onlydragon for the API


@bot.message_handler(commands=['user'])
def nft(message):
    Address = message.text.split()[1]
    try:
        req = requests.get(f"https://tonapi.io/v2/accounts/{Address}/nfts").json()["nft_items"]
        usernames = []
        for c in req:
            try:
                usernames.append(c["metadata"]["name"])
            except:
                pass
        if len(usernames) == 0:
            bot.reply_to(message, "*There are no NFT usernames in this wallet!*",
                         parse_mode="Markdown")
        else:
            bot.reply_to(message, "*Usernames:*\n" + "\n*".join(usernames),
                         parse_mode="Markdown")
    except:
        bot.reply_to(message, "*Invalid address. Please enter a valid address.*",
                     parse_mode="Markdown")


bot.infinity_polling()