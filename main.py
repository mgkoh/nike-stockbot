import requests
import datetime
import discord
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands
import math


async def stock_check(name, region, ctx):
    agent = {"User-Agent":"Mozilla/5.0"}
    channelId = '28010794e5-35fe-4e32-aaff-cd2c74f89d61%29'

    if(region == 'MY' or region == 'SG'):
        url_format = ('https://api.nike.com/product_feed/threads/v3/?filter=marketplace%28'+region+'%29&filter=language%28en-GB%29&filter=channelId%')+ channelId +('&filter=seoSlugs%28')+name+('%29&filter=exclusiveAccess%28true%2Cfalse%29')
        #https://api.nike.com/product_feed/threads/v3/?filter=marketplace%28MY%29&filter=language%28en-GB%29&filter=channelId%28010794e5-35fe-4e32-aaff-cd2c74f89d61%29&filter=seoSlugs%28air-max-1-kasina-won-ang%29&filter=exclusiveAccess%28true%2Cfalse%29
    elif(region=='JP'):
        url_format = ('https://api.nike.com/product_feed/threads/v3/?filter=marketplace%28'+region+'%29&filter=language%28ja%29&filter=channelId%')+ channelId +('&filter=seoSlugs%28')+name+('%29&filter=exclusiveAccess%28true%2Cfalse%29')
    elif(region =='TW'):
        url_format = ('https://api.nike.com/product_feed/threads/v3/?filter=marketplace%28'+region+'%29&filter=language%28zh-Hant%29&filter=channelId%')+ channelId +('&filter=seoSlugs%28')+name+('%29&filter=exclusiveAccess%28true%2Cfalse%29')


    r = requests.get(url_format, headers= agent)
    json_string = r.json()

    print(name)

    # json_string['objects'][0]['productInfo'][0]['skus'])
    # json_string['objects'][0]['productInfo'][0]['availableGtins']
    try:
        count = len(json_string['objects'][0]['productInfo'])
    except (IndexError):
        await ctx.send("item not found or inactive for region/ wrong url format. Try !info for more help.")

    for i in range(count):

        try:
            prefix_size = []
            available_gtin = []
            launch_type =""
            launch_date=""
            madeIn=""
            last_fetch_time=""


            for items in json_string['objects'][0]['productInfo'][i]['skus']:
                size = [items['gtin'], items['nikeSize'], items['countrySpecifications'][0]['localizedSize']]
                prefix_size.append(size)


            for items in json_string['objects'][0]['productInfo'][i]['availableGtins']:
                stock = [items['gtin'], items['level']]
                available_gtin.append(stock)


            launch_type = json_string['objects'][0]['productInfo'][i]['launchView']['method']
            launch_date = str(json_string['objects'][0]['productInfo'][i]['launchView']['startEntryDate']).split('T')[0]
            startHour, startMinutes = \
                str(json_string['objects'][0]['productInfo'][i]['launchView']['startEntryDate']).split('T')[1].split('Z')[
                    0].split(':')[0], \
                str(json_string['objects'][0]['productInfo'][i]['launchView']['startEntryDate']).split('T')[1].split('Z')[
                    0].split(':')[1]

            if(launch_type == "DAN"):
                stopHour, stopMinutes = \
                str(json_string['objects'][0]['productInfo'][i]['launchView']['stopEntryDate']).split('T')[1].split('Z')[
                    0].split(':')[0], \
                str(json_string['objects'][0]['productInfo'][i]['launchView']['stopEntryDate']).split('T')[1].split('Z')[
                    0].split(':')[1]

                totalHours, totalMinutes = int(stopHour) - int(startHour), int(stopMinutes) - int(startMinutes)

                if (totalMinutes < 0 and totalHours >0):
                    totalHours, totalMinutes = totalHours - 1, abs(totalMinutes)
                else:
                    totalMinutes = abs(totalMinutes)

                startTime = str(int(startHour) + 8) + ":" + str(startMinutes)

            elif(launch_type=="LEO"):
                startTime = str(int(startHour) + 8) + ":" + str(startMinutes)

            price = str(json_string['objects'][0]['productInfo'][i]['merchPrice']['currentPrice'])
            madeIn = str(json_string['objects'][0]['productInfo'][i]['productContent']['manufacturingCountryOfOrigin'])
            sku = str(json_string['objects'][0]['productInfo'][i]['merchProduct']['styleColor'])
            last_fetch_time = str(json_string['objects'][0]['lastFetchTime'])
            sizing = str(json_string['objects'][0]['productInfo'][i]['merchProduct']['genders'][0])
            country = str(json_string['objects'][0]['marketplace'])
            currency = str(json_string['objects'][0]['productInfo'][i]['merchPrice']['currency'])

            try:
                #won -ang air max error -> no alttext section found
                shoe_name = str(json_string['objects'][0]['publishedContent']['nodes'][1]['properties']['altText']).split('(')[0]

            except:
                shoe_name = str(json_string['objects'][0]['publishedContent']['nodes'][1]['properties']['subtitle'])


        except(KeyError):
            print("Key Error! Object probably not found.")

        except:
            print("An error has occured")

        finally:
            if (len(prefix_size)+len(available_gtin)> 0):
                for item in prefix_size:
                    for stock in available_gtin:
                        if (item[0] == stock[0]):
                            stock.extend([item[1], item[2]])
                #gtin available fully loaded
                #url='https://www.nike.com/my/launch/t/'+name
                e = discord.Embed(title=shoe_name, description=country+ ":flag_"+country.lower()+":", url='https://www.nike.com/my/launch/t/'+name,  )
                e.add_field(name="SKU", value=sku)
                e.add_field(name="Price ("+currency+")", value=price)
                e.add_field(name="Launch Date", value=launch_date)

                e.add_field(name="Size",value=sizing)
                e.add_field(name="Launch Type", value=launch_type)
                e.add_field(name="Start Time", value=startTime)
                e.add_field(name=' \u200b ',value=" \u200b ")
                e.add_field(name=' \u200b ',value=" \u200b ")
                e.add_field(name=' \u200b ',value=" \u200b ")

                for item in available_gtin:
                    # item = [gtin, stock level, US size, UK size]
                    #discord emoji : orange = <:orange_circle:>, green = <:green_circle:>, red = <:red_circle:>, white = <:white_circle:>
                    if(len(item)==4):
                        if(item[1]=='HIGH'):
                            item[1]="US"+item[2]+" | "+"UK" + str(item[3])+"\t\t"+":green_circle:"+str(item[1])
                            # e.add_field(name="UK" + str(item[3]), value=":green_circle:"+str(item[1]), inline=True)
                        elif(item[1]=='MEDIUM'):
                            item[1]="US"+item[2]+" | "+"UK" + str(item[3])+"\t\t"+":orange_circle:"+str(item[1])
                            # e.add_field(name="UK" + str(item[3]), value=":orange_circle:"+str(item[1]), inline=True)
                        elif(item[1]=='LOW'):
                            item[1]="US"+item[2]+" | "+"UK" + str(item[3])+"\t\t"+":red_circle:"+str(item[1])
                            # e.add_field(name="UK" + str(item[3]), value=":red_circle:"+str(item[1]), inline=True)
                        elif(item[1]=='OOS'):
                            item[1]="US"+item[2]+" | "+"UK" + str(item[3])+"\t\t"+":white_circle:"+str(item[1])
                            # e.add_field(name="UK" + str(item[3]), value=":white_circle:"+str(item[1]), inline=True)
                    else:
                        item[1]= str(item[0])+"\n"+str(item[1])
                        # e.add_field(name="GTIN :"+str(item[0]), value=str(item[1]))

                e.add_field(name="Level :", value="\n\n".join(str(item[1]) for item in available_gtin[:(math.floor(len(available_gtin)/2))])+"\n", inline=True)
                e.add_field(name=' \u200b ',value=" \u200b ")

                e.add_field(name="Level :", value="\n\n".join(str(item[1]) for item in available_gtin[(math.ceil(len(available_gtin)/2)):len(available_gtin)])+"\n", inline=True)

                e.add_field(name=' \u200b ',value=" \u200b ")
                e.add_field(name=' \u200b ',value=" \u200b ")
                e.add_field(name=' \u200b ',value=" \u200b ")
                if (launch_type == "DAN"):
                    e.add_field(name="Duration", value=(str(totalHours)+"H" + " " + str(totalMinutes)+"M"))
                e.add_field(name="Made In", value=madeIn)
                e.add_field(name="Last Fetch Time", value=last_fetch_time)
                e.set_thumbnail(url='https://secure-images.nike.com/is/image/DotCom/'+sku.replace('-','_')+'_A_PREM?$SNKRS_COVER_WD$&align=0,1')
                e.set_footer(text="GGEZ")

            else:
                e = discord.Embed(title="Error occurred", description="try !info for more info.")

            print("A request has been sent!")
            await ctx.send(embed=e)

with open("tkn" + '.txt') as f:
    token = f.read()



bot = commands.Bot(command_prefix='!')
@bot.event
async def on_ready():
    print("The bot is running.")

@bot.command()  #decorator
async def name(ctx, arg):
    """!name xxxx"""
    await stock_check(name=arg, region='MY', ctx=ctx)

@bot.command()
async def link(ctx, arg):
    """!link xxxx"""
    url = arg
    if(len(url)>120):
        name = url.split('/')[6].split('?')[0]
    else:
        name = str(url).split('/')[6]
    await stock_check(name=name , region='MY', ctx=ctx)

@bot.command()
async def sglink(ctx, arg):
    """!link xxxx"""
    url = arg
    if(len(url)>120):
        name = url.split('/')[6].split('?')[0]
    else:
        name = str(url).split('/')[6]
    await stock_check(name=name, region='SG', ctx=ctx)

@bot.command()
async def jplink(ctx, arg):
    """!link xxxx"""
    url = arg
    if(len(url)>120):
        name = url.split('/')[6].split('?')[0]
    else:
        name = str(url).split('/')[6]
    await stock_check(name=name, region='JP', ctx=ctx)

@bot.command()
async def twlink(ctx, arg):
    """!link xxxx"""
    url = arg
    if(len(url)>120):
        name = url.split('/')[6].split('?')[0]
    else:
        name = str(url).split('/')[6]
    await stock_check(name=name, region='TW', ctx=ctx)


@bot.command()
async def info(ctx):
    """!info"""
    await ctx.send("!link ""link"" from snkrs")
    await ctx.send("command 2: !name xxx-xxx-xxx eg: !name dunk-low-my-ass, title from snkrs page with ""-""")
    await ctx.send("command 3: !sglink xxxx(link from snkrs my/sg) for SG region" )
    await ctx.send("command 4: !jplink xxxx(link from snkrs my/sg) for JP region" )
    await ctx.send("command 5: !twlink xxxx(link from snkrs my/sg) for TW region" )


bot.run(token)


