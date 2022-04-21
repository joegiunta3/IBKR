from telethon import TelegramClient
import telethon
import requests
import datetime
from datetime import datetime, timezone, timedelta
from IbApi import buyOrder
import time

# Remember to use your own values from my.telegram.org!
# 8894405
# d4fcbaff22d34abf0360411941eacb85
api_id = 7297355
api_hash = '82e1551032f3d105fa1101c4489e594b'
# api_id = 8894405
# api_hash = 'd4fcbaff22d34abf0360411941eacb85'
# api_id = 8078121
# api_hash = 'd3307eb938edc78392c95a5963d07a3b'
# api_id = 8336232
# api_hash = '753c3058d21574b902e06c972a7392f3'
# api_id = 8616990
# api_hash = 'cbf5b1041de20df263a78e83f6bcd719'
# api_id = 7938801
# api_hash = 'b6301dc1c7a24bba54a3182a23047931'
# api_id = 7297355
# api_hash = '82e1551032f3d105fa1101c4489e594b'
# api_id = 7279649
# api_hash = 'c79e45f0d0ecf4cbdfc7c6ca23fd0e51'
client = TelegramClient('anon', api_id, api_hash)


def preBuyOrder(tickerSymbol, buyInPriceStr, targetPriceFinalStr):
    print('PreBuyOrder: ', tickerSymbol)
    buyOrder(tickerSymbol, buyInPriceStr, targetPriceFinalStr)
    
def getReadyToBuy(tickerSymbol, buyInPriceStr, targetPriceFinalStr):
    # getaPriceApiUrl = 'https://finnhub.io/api/v1/quote?symbol=' + tickerSymbol + '&token=' + 'c2i5ntqad3idsa35ii5g'
    # print("getaPriceApiUrl")
    # print(getaPriceApiUrl)
    # r = requests.get(getaPriceApiUrl)
    # jsonReturnPrice = r.json()
    # print(jsonReturnPrice)
    # print('Current Price Finnhub')
    # stockPriceCurrent = jsonReturnPrice['c']
    # print(stockPriceCurrent)

    # orderNotificationMessage = 'Ticker Symbol:' + tickerSymbol + ', Price: ' + str(stockPriceCurrent)
    # pbJosephSent = pbJoseph.push_note(
    #     "Order Placed", orderNotificationMessage)
    # pbJamieSent = pbJamie.push_note(
    #     "Order Placed", orderNotificationMessage)
    # print(orderNotificationMessage)
    # preBuyOrder("AAPL", buyInPriceStr, targetPriceFinalStr)
    preBuyOrder(tickerSymbol, buyInPriceStr, targetPriceFinalStr)


async def main():
    # # Getting information about yourself
    # me = await client.get_me()

    # # "me" is a user object. You can pretty-print
    # # any Telegram object with the "stringify" method:
    # print(me.stringify())

    # # When you print something, you see a representation of it.
    # # You can access all attributes of Telegram objects with
    # # the dot operator. For example, to get the username:
    # username = me.username
    # print(username)
    # print(me.phone)

    # # You can print all the dialogs/conversations that you are part of:
    # async for dialog in client.iter_dialogs():
    #     print(dialog.name, 'has ID', dialog.id)

    # # You can send messages to yourself...
    # await client.send_message('me', 'Hello, myself!')
    # # ...to some chat ID
    # await client.send_message(-100123456, 'Hello, group!')
    # # ...to your contacts
    # await client.send_message('+34600123123', 'Hello, friend!')
    # # ...or even to any username
    # await client.send_message('username', 'Testing Telethon!')
    
    # Get messages by ID:
    # message_channel_id_test = 93372553
    message_channel_id = -1001400330692
    # message_1337 = await client.get_messages(client, ids=message_channel)
    # print(message_1337)
    last_message_id = "3944"
    # last_message_id = '0' #3944
    messagesList = ''
    fileNameLastMessageId = 'latest_message_id.txt'
    fileNameLastMessageStr = 'latest_message_str.txt'
    filterStrPost = "\U0001f4b0 I'll buy "
    filterStr = "\U0001f4b0 I'll"
    waitTimeSeconds=1
    
    with open(fileNameLastMessageId) as f:
        last_message_id = f.read()
        f.close()
    
    print("Last Message ID: " + last_message_id)
    
    isFirstMessage = True
    while True:
        time.sleep(1)
        currentTimeNowEST = (datetime.now(timezone.utc) - timedelta(hours=4)).strftime('%Y-%m-%dT%H:%M:%S.%f%z')  # Set to same timezone
        print("Date Pre: ", currentTimeNowEST)
        # async for message in client.iter_messages(message_channel_id, limit=1):
        async for message in client.iter_messages(message_channel_id, limit=1, min_id=int(last_message_id)):
        # async for message in client.iter_messages(message_channel_id, limit=1, min_id=int(last_message_id), 
        #     search=filterStr):
        # async for message in client.iter_messages(message_channel_id_test, limit=1, min_id=int(last_message_id), wait_time=waitTimeSeconds):
            
            # Continue filtering
            msgStr = message.text
            msgStrSplitFirst = msgStr.split(filterStrPost)
            last_message_id=message.id
            with open(fileNameLastMessageId, 'w') as fileLastMessageid:
                fileLastMessageid.write(str(message.id))
                fileLastMessageid.close()
            if len(msgStrSplitFirst) > 1:
                print(message.id, msgStr)
                print("Last Message ID: " + str(last_message_id))
                # print(message.id, msgStr)
                with open(fileNameLastMessageStr, 'w', encoding='utf-8') as fileLastMessageText:
                    fileLastMessageText.write(msgStr)
                    fileLastMessageText.close()
                # if isFirstMessage == True:
                #     isFirstMessage = False
                
                print(len(msgStrSplitFirst))
                msgStrSplit = msgStrSplitFirst[1].split(' ')
                if len(msgStrSplit) > 0:
                    tickerSymbol = msgStrSplit[0]
                    if len(tickerSymbol) <= 5 and len(tickerSymbol) > 0:
                        print("...............................TICKERSYMBOL: ", tickerSymbol)
                        currentTimeNowEST = (datetime.now(timezone.utc) - timedelta(hours=4)).strftime('%Y-%m-%dT%H:%M:%S.%f%z')  # Set to same timezone
                        print("Date: ", currentTimeNowEST)
                        upperCaseSymbol = tickerSymbol.upper()
                        # Find the Together "Buy Stop" with a "Sell Limit" at 0.5% before entry price. 0.5% down from target.
                        # Key strings:
                        # "last shares of "
                        # "target 
                        msgStrFindPriceEntry = msgStr.split(filterStrPost + tickerSymbol)
                        if len(msgStrFindPriceEntry) > 1:
                            msgStrFindPriceEntrySpace = msgStrFindPriceEntry[1].split()
                            if len(msgStrFindPriceEntrySpace) > 0:
                                buyInPriceStrFirst = msgStrFindPriceEntrySpace[0]
                                buyInPriceStrSecond = msgStrFindPriceEntrySpace[1]
                                buyInPriceStrThird = msgStrFindPriceEntrySpace[2]
                                if buyInPriceStrFirst.isdigit():
                                    buyInPriceStr = buyInPriceStrFirst
                                elif buyInPriceStrSecond.isdigit():
                                    buyInPriceStr = buyInPriceStrSecond
                                elif buyInPriceStrThird.isdigit():
                                    buyInPriceStr = buyInPriceStrThird
                                print("Price Found: ", buyInPriceStr)
                                # getReadyToBuy(upperCaseSymbol, buyInPriceStr, buyInPriceStr)
                                # targetPriceStrSplit = msgStrFindPriceEntry[1].split('target ')
                                # if len(targetPriceStrSplit) > 0:
                                #     targetPriceStrSplitSpace = targetPriceStrSplit[1].split(' ')
                                #     if len(targetPriceStrSplitSpace) > 0:
                                #         targetPriceFinalStr = targetPriceStrSplitSpace[0]
                                #         print("buyInPriceStr", buyInPriceStr)
                                #         print("targetPriceFinalStr", targetPriceFinalStr)
                                        # getReadyToBuy(upperCaseSymbol, buyInPriceStr, targetPriceFinalStr)
        

    # # Sending a message returns the sent message object, which you can use
    # print(message.raw_text)

    # # You can reply to messages directly if you have a message object
    # await message.reply('Cool!')

    # # Or send files, songs, documents, albums...
    # await client.send_file('me', '/home/me/Pictures/holidays.jpg')

    # # You can print the message history of any chat:
    # async for message in client.iter_messages('me'):
    #     print(message.id, message.text)

    #     # You can download media from messages, too!
    #     # The method will return the path where the file was saved.
    #     if message.photo:
    #         path = await message.download_media()
    #         print('File saved to', path)  # printed after download is done

with client:
    client.loop.run_until_complete(main())