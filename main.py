import datetime
import discord
import requests
import json
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

# url_light_madder_root = 'https://api.nike.com/deliver/available_gtins/v3/?filter=styleColor(DC0774-800)&filter=merchGroup(XA)'
#
# url_coconut = 'https://api.nike.com/deliver/available_gtins/v3/?filter=styleColor(DN4281-100)&filter=merchGroup(XA)'
#
# url_webhook = 'https://discord.com/api/webhooks/946414280310419507/QB3CPzjLgaXlI0jWmoCd2GxB8cxF61hM9Zx3cFOac4OwTCaBWPQeKgHRltpZkrZvzQft'
# url_webhook2 = 'https://discord.com/api/webhooks/931878180103544843/zINcFb97bVbEwVXU_25KyQzDU07CSstA9FTiCqz9ZsUPUkPF5erThAA9PP-Z-6zD9RbQ'
url_webhook2_token = 'zINcFb97bVbEwVXU_25KyQzDU07CSstA9FTiCqz9ZsUPUkPF5erThAA9PP-Z-6zD9RbQ'

# sku = "DQ4121-001"
# url = 'https://api.nike.com/deliver/available_gtins/v3/?filter=styleColor('+sku+')&filter=merchGroup(XA)'
# sku_test = 'DH7004-102'

json_xpath ='/html/body/pre'
#sizing
#   wmns = us 5- 12 (14sizes)
#   mns = us7 to 12 (10) usual


webhook = Webhook.from_url("https://discord.com/api/webhooks/947162466960437288/LgC2SbByE6d1ncdGpwKFMagBtnNffqvEdMOpscfdRqiq2BT83K5vU1lLn4jm0WSA1h_k", adapter=RequestsWebhookAdapter())



bot = commands.Bot(command_prefix='!')


@bot.command()  #decorator
async def sku(ctx, arg):
    """!sku xxxx"""
    sku = arg
    url1 = 'https://api.nike.com/deliver/available_gtins/v3/?filter=styleColor(' + sku + ')&filter=merchGroup(XA)'
    r = requests.get(url1)
    json_string = r.json()
    print(json_string)
    details = []
    if (len(json_string['objects']) < 15 and len(json_string['objects'])>10):
        start_size = 5
        for size in json_string['objects']:
            stock = []
            stock.append(str(start_size))
            stock.append(size['level'])
            start_size += 0.5
            details.append(stock)

    elif (len(json_string['objects']) > 14):
        start_size = 4
        for size in json_string['objects']:
            stock = []
            stock.append(str(start_size))
            stock.append(size['level'])
            start_size += 0.5
            details.append(stock)

    elif (len(json_string['objects']) < 11):
        start_size = 7
        for size in json_string['objects']:
            stock = []
            stock.append(str(start_size))
            stock.append(size['level'])
            start_size += 0.5
            details.append(stock)

    print(details)

    e = discord.Embed(title=sku, description="")
    for item in details:
        e.add_field(name=item[0], value=item[1])


    e.add_field(name="Time", value=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    await ctx.send(embed= e)

string = "OTQ3MTY0NDI5MTgxNjUzMDEz.YhpRnQ.KDv5o0Z2qeWbzpDwJk2Ad0XqF4c"
bot.run(string)
