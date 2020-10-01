#!/usr/bin/python
# -*- coding: utf-8 -*-
import discord
import asyncio
import requests
import time
import json
import re
import urllib3
from datetime import datetime

urllib3.disable_warnings()

# Miscallaneous Variables
client = discord.Client()
with open("settings.json") as settings_file:
    settings = json.load(settings_file)
print(settings)
bot_token = settings["bot_token"]
server = settings["server_id"]
command_prefix = settings["command_prefix"]
thumbnail_icon_url = settings["thumbnail_icon_url"]
footer_text = settings["footer_text"]
footer_icon_url = settings["footer_icon_url"]
embed_color = 0x13e79e # Feel free to change this to a different color code!
guild = None
marketplace_fee_rates = {
    "stockx": {
        "level_one": 0.125,
        "level_two": 0.12,
        "level_three": 0.115,
        "level_four": 0.11
    },
    "goat": 0.124
}


# Checks for when bot is online
@client.event
async def on_ready():
    global guild
    print("Bot is logged in as {0.user}".format(client))
    print("StockX - Goat Bot is Online")
    await client.change_presence(status=discord.Status.online, activity=discord.Game("@ayyitsc9"))
    guild = client.get_guild(server)




# Checks for when a message is sent
@client.event
async def on_message(message):
    # StockX search command
    if message.content.startswith(f"{command_prefix}stockx"):
        args = message.content.split("stockx ")[1]
        words = re.findall(r'\w+', args)
        keywords = ''
        for word in words:
            keywords += word + '%20'
        json_string = json.dumps({"params": f"query={keywords}&hitsPerPage=10&facets=*"})
        byte_payload = bytes(json_string, 'utf-8')
        algolia = {"x-algolia-agent": "Algolia for vanilla JavaScript 3.32.0", "x-algolia-application-id": "XW7SBCT9V6", "x-algolia-api-key": "6bfb5abee4dcd8cea8f0ca1ca085c2b3"}
        with requests.Session() as session:
            r = session.post("https://xw7sbct9v6-dsn.algolia.net/1/indexes/products/query", params=algolia, data=byte_payload, timeout=30)
            results = r.json()["hits"][0]
            apiurl = f"https://stockx.com/api/products/{results['url']}?includes=market,360&currency=USD"
            header = {
                'accept': '*/*',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7,la;q=0.6',
                'appos': 'web',
                'appversion': '0.1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
            }
            response = requests.get(apiurl, verify=False, headers=header)

        prices = response.json()
        general = prices['Product']
        market = prices['Product']['market']
        sizes = prices['Product']['children']
    
        bidasks = ''
        for size in sizes:
            if len(bidasks) + len(f"Size {sizes[size]['shoeSize']} | Low Ask ${sizes[size]['market']['lowestAsk']} | High Bid ${sizes[size]['market']['highestBid']}\n") < 1024:
                bidasks +=f"Size {sizes[size]['shoeSize']} | Low Ask ${sizes[size]['market']['lowestAsk']} | High Bid ${sizes[size]['market']['highestBid']}\n"

        embed = discord.Embed(title=general['title'], url='https://stockx.com/' + general['urlKey'], color=embed_color, timestamp=datetime.utcnow())
        embed.set_image(url=results['thumbnail_url'])
        embed.set_thumbnail(url=thumbnail_icon_url)
        embed.set_footer(icon_url=footer_icon_url, text=footer_text)
        if 'styleId' in general:
            embed.add_field(name='SKU', value=general['styleId'], inline=True)
        else:
            embed.add_field(name='SKU', value='None', inline=True)
        if 'colorway' in general:
            embed.add_field(name='Colorway', value=general['colorway'], inline=True)
        else:
            embed.add_field(name='Colorway', value='None', inline=True)
        if 'retailPrice' in general:
            embed.add_field(name='Retail Price', value=f"${general['retailPrice']}", inline=True)
        else:
            for trait in general['traits']:
                try:
                    embed.add_field(name='Retail Price', value=f"${int(trait['value'])}")
                except:
                    pass
        if 'releaseDate' in general:
            embed.add_field(name='Release Date', value=general['releaseDate'], inline=True)
        else:
            embed.add_field(name='Release Date', value='None', inline=True)
        embed.add_field(name='Highest Bid', value=f"${market['highestBid']} Size {market['highestBidSize']}", inline=True)
        embed.add_field(name='Lowest Ask', value=f"${market['lowestAsk']} Size {market['lowestAskSize']}", inline=True)
        embed.add_field(name='Total Asks', value=market['numberOfAsks'], inline=True)
        embed.add_field(name='Total Bids', value=market['numberOfBids'], inline=True)
        embed.add_field(name='Total Sold', value=market['deadstockSold'], inline=True)
        embed.add_field(name='Sales last 72 hrs', value=market['salesLast72Hours'], inline=True)
        try:
            embed.add_field(name='Last Sale', value=f"${market['lastSale']} Size {market['lastSaleSize']} {market['lastSaleDate'].split('T')[0]} {market['lastSaleDate'].split('T')[1].split('+')[0]}", inline=True)
        except:
            pass
        embed.add_field(name='Sizes', value=bidasks, inline=False)
        await message.channel.send(embed=embed)

    # Goat search Command
    elif message.content.startswith(f"{command_prefix}goat"):
        args = message.content.split("goat ")[1]
        words = re.findall(r'\w+', args)
        keywords = ''
        for word in words:
            keywords += word + '%20'
        json_string = json.dumps({"params": f"distinct=true&facetFilters=()&facets=%5B%22size%22%5D&hitsPerPage=10&numericFilters=%5B%5D&page=0&query={keywords}"})
        byte_payload = bytes(json_string, 'utf-8')
        x = {"x-algolia-agent": "Algolia for vanilla JavaScript 3.25.1", "x-algolia-application-id": "2FWOTDVM2O", "x-algolia-api-key": "ac96de6fef0e02bb95d433d8d5c7038a"}
        with requests.Session() as s:
            r = s.post("https://2fwotdvm2o-dsn.algolia.net/1/indexes/product_variants_v2/query", params=x, verify=False, data=byte_payload, timeout=30)
        try:
            results = r.json()["hits"][0]
            priceurl = f"https://www.goat.com/web-api/v1/product_variants?productTemplateId={results['slug']}"
            with requests.Session() as s2:
                header = {
                    'accept': 'application/json',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                    'accept-language': 'en-us',
                    'accept-encoding': 'br,gzip,deflate'
                }
            cont = True
        except:
            print("Product not found")
            cont = False
        if cont:
            r2 = s2.get(priceurl, headers=header)
            prices = r2.json()
            priceformat = ''
            availableSizesNewV2 = {}
            for sizeEntry in prices:
                if sizeEntry['shoeCondition'] == 'new_no_defects' and sizeEntry['boxCondition'] == 'good_condition':
                    availableSizesNewV2.update({
                        sizeEntry['size']:str(sizeEntry['lowestPriceCents']['amount'])[:-2]
                    })
            for ask in availableSizesNewV2:
                priceformat += f"Size {ask} | Ask: ${availableSizesNewV2[ask]}\n"
            embed = discord.Embed(title=results['name'], url=f"https://goat.com/sneakers/{results['slug']}", color=embed_color, timestamp=datetime.utcnow())
            embed.set_image(url=results['main_picture_url'])
            embed.set_thumbnail(url=thumbnail_icon_url)
            embed.set_footer(icon_url=footer_icon_url, text=footer_text)
            if results['sku']:
                embed.add_field(name='SKU', value=f"{results['sku']}", inline=True)
            else:
                embed.add_field(name='SKU', value="None", inline=True)
            if results['details']:
                embed.add_field(name='Colorway', value=f"{results['details']}", inline=True)
            else:
                embed.add_field(name='Colorway', value="None", inline=True)
            if results['special_display_price_cents']:
                embed.add_field(name='Retail Price', value=f"${str(results['special_display_price_cents'])[:-2]}", inline=True)
            else:
                embed.add_field(name='Retail Price', value="None", inline=True)
            if results['release_date']:
                embed.add_field(name='Release Date', value=f"{results['release_date']}", inline=True)
            else:
                embed.add_field(name='Release Date', value="None", inline=True)
            embed.add_field(name='Prices', value=priceformat, inline=False)
            await message.channel.send(embed=embed)

    # Compare command. Searches both StockX and Goat
    elif message.content.startswith(f"{command_prefix}compare"):
        command_ran_by = message.author.id
        command_ran_in = message.channel.id
        def check(message):
            if message.author.id == command_ran_by and message.channel.id == command_ran_in:
                return message.content == message.content and message.channel == message.channel
        args = message.content.split("compare ")[1]
        words = re.findall(r'\w+', args)
        keywords = ''
        for word in words:
            keywords += word + '%20'
        try:
            embed = discord.Embed(title="What StockX level are you? 1 to 4", colour=0x13e79e, timestamp=datetime.utcnow())           
            embed.set_footer(icon_url=footer_icon_url, text=footer_text)
            await message.channel.send(embed=embed)
            stockx_level = await client.wait_for("message", check=check, timeout=30.0)
            stockx_level = str(stockx_level.content)
            if int(stockx_level)>4 or int(stockx_level)<1:
                embed = discord.Embed(title="😰 Invalid input! Make sure to enter a number between 1 to 4.", colour=0x13e79e, timestamp=datetime.utcnow())           
                embed.set_footer(icon_url=footer_icon_url, text=footer_text)
                await message.channel.send(embed=embed)
            else:
                if int(stockx_level) == 1:
                    stockx_fee_rate = marketplace_fee_rates["stockx"]["level_one"]
                elif int(stockx_level) == 2:
                    stockx_fee_rate = marketplace_fee_rates["stockx"]["level_two"]
                elif int(stockx_level) == 3:
                    stockx_fee_rate = marketplace_fee_rates["stockx"]["level_three"]
                elif int(stockx_level) == 4:
                    stockx_fee_rate = marketplace_fee_rates["stockx"]["level_four"]
                else:
                    pass
                json_string = json.dumps({"params": f"query={keywords}&hitsPerPage=20&facets=*"})
                byte_payload = bytes(json_string, 'utf-8')
                algolia = {"x-algolia-agent": "Algolia for vanilla JavaScript 3.32.0", "x-algolia-application-id": "XW7SBCT9V6", "x-algolia-api-key": "6bfb5abee4dcd8cea8f0ca1ca085c2b3"}
                with requests.Session() as session:
                    r = session.post("https://xw7sbct9v6-dsn.algolia.net/1/indexes/products/query", params=algolia, data=byte_payload, timeout=30)
                try:
                    results = r.json()["hits"][0]
                    apiurl = f"https://stockx.com/api/products/{results['url']}?includes=market,360&currency=USD"
                    header = {
                        'accept': '*/*',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7,la;q=0.6',
                        'appos': 'web',
                        'appversion': '0.1',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
                    }
                    response = requests.get(apiurl, verify=False, headers=header)
                except IndexError:
                    embed = discord.Embed(title="😰 Could not find product on StockX", colour=0x13e79e, timestamp=datetime.utcnow())           
                    embed.set_footer(icon_url=footer_icon_url, text=footer_text)
                    await message.channel.send(embed=embed)
                prices = response.json()
                general = prices['Product']
                market = prices['Product']['market']
                sizes = prices['Product']['children']
                stockx_object = {}
                for size in sizes:
                    if "Y" in sizes[size]['shoeSize']:
                        sizes[size]['shoeSize'] = sizes[size]['shoeSize'].replace("Y", "")
                    elif "W" in sizes[size]['shoeSize']:
                        sizes[size]['shoeSize'] = sizes[size]['shoeSize'].replace("W", "")
                    stockx_object.update({
                        sizes[size]['shoeSize']: sizes[size]['market']['lowestAsk'] - (stockx_fee_rate * float(sizes[size]['market']['lowestAsk']))
                    })
                embed = discord.Embed(title=general['title'], description="The payouts being compared are asks!", url='https://stockx.com/' + general['urlKey'], color=embed_color, timestamp=datetime.utcnow())
                embed.set_image(url=results['thumbnail_url'])
                embed.set_thumbnail(url=thumbnail_icon_url)
                embed.set_footer(icon_url=footer_icon_url, text=footer_text)


                json_string = json.dumps({"params": f"distinct=true&facetFilters=()&facets=%5B%22size%22%5D&hitsPerPage=20&numericFilters=%5B%5D&page=0&query={keywords}"})
                byte_payload = bytes(json_string, 'utf-8')
                x = {"x-algolia-agent": "Algolia for vanilla JavaScript 3.25.1", "x-algolia-application-id": "2FWOTDVM2O", "x-algolia-api-key": "ac96de6fef0e02bb95d433d8d5c7038a"}
                with requests.Session() as s:
                    r = s.post("https://2fwotdvm2o-dsn.algolia.net/1/indexes/product_variants_v2/query", params=x, verify=False, data=byte_payload, timeout=30)
                try:
                    results = r.json()["hits"][0]
                    priceurl = f"https://www.goat.com/web-api/v1/product_variants?productTemplateId={results['slug']}"
                    with requests.Session() as s2:
                        header = {
                            'accept': 'application/json',
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                            'accept-language': 'en-us',
                            'accept-encoding': 'br,gzip,deflate'
                        }
                    cont = True
                except IndexError:
                    embed = discord.Embed(title="😰 Could not find product on Goat", colour=0x13e79e, timestamp=datetime.utcnow())           
                    embed.set_footer(icon_url=footer_icon_url, text=footer_text)
                    await message.channel.send(embed=embed)
                    cont = False
                if cont:
                    r2 = s2.get(priceurl, headers=header)
                    prices = r2.json()
                    embed.add_field(name="Goat Product Found", value=results['name'])
                    goat_object = {}
                    availableSizesNewV2 = {}
                    for sizeEntry in prices:
                        if sizeEntry['shoeCondition'] == 'new_no_defects' and sizeEntry['boxCondition'] == 'good_condition':
                            availableSizesNewV2.update({
                                str(sizeEntry['size']):str(sizeEntry['lowestPriceCents']['amount'])[:-2]
                            })
                    for ask in availableSizesNewV2:
                        if ".0" in ask:
                            ask = ask.replace(".0", "")
                        goat_object.update({
                            ask: int(availableSizesNewV2[ask]) - (marketplace_fee_rates["goat"] * float(int(availableSizesNewV2[ask]))) - 5
                        })
                    if len(stockx_object) > len(goat_object):
                        for size in stockx_object:
                            embed_val = f"**StockX**\n${stockx_object[size]}\n"
                            if size in goat_object.keys():
                                embed_val += f"**Goat**\n{goat_object[size]}"
                                if stockx_object[size] > goat_object[size]:
                                    verdict = f"\n__StockX | ${stockx_object[size] - goat_object[size]}__"
                                else:
                                    verdict = f"\n__Goat | ${goat_object[size] - stockx_object[size]}__"
                            else:
                                embed_val += f"**Goat**\nNo data found"
                                verdict = f"\n__StockX | ${stockx_object[size] - 0}__"
                            embed_val += verdict
                            embed.add_field(name=size, value=embed_val, inline=True)
                    else:
                        for size in goat_object:
                            embed_val = f"**Goat**\n${goat_object[size]}\n"
                            if size in stockx_object.keys():
                                embed_val += f"**StockX**\n{stockx_object[size]}"
                                if stockx_object[size] > goat_object[size]:
                                    verdict = f"\n__StockX | ${stockx_object[size] - goat_object[size]}__"
                                else:
                                    verdict = f"\n__Goat | ${goat_object[size] - stockx_object[size]}__"
                            else:
                                embed_val += f"**StockX**\nNo data found"
                                verdict = f"\n__Goat | ${goat_object[size] - 0}__"
                            embed_val += verdict
                            embed.add_field(name=size, value=embed_val, inline=True)
                    await message.channel.send(embed=embed)
        except asyncio.TimeoutError:
            embed = discord.Embed(title="😰 Timed out! Please make sure to reply within 30 seconds", colour=0x13e79e, timestamp=datetime.utcnow())           
            embed.set_footer(icon_url=footer_icon_url, text=footer_text)
            await message.channel.send(embed=embed)
client.run(bot_token)
