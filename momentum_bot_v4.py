from formulas import *
import time
from binance import Client
from decimal import Decimal
import threading


api_key = 'BLFgpfDI6Sw8dDwmKiemq4M75FaCJjs2gIhVANKNyNfj5KRbZOEbeLinwJzpfx0b'
api_secret = 'jdhTwrB1d5q9MEdohdqPUXQRCMGwp04kkEZPbUrY37GZI4GKfoNi9n1zxe30xiny'


lever = 20
quant = 0.015
order_point = 2743

ticker = 'YFIIUSDT'

trigger = True #if true, we perform a buy when the price reaches the order point, if not then the bot follows its usual process


zones = [[2800,2700]] #Two Zones Defined

#Fixed Declarations
live_price = 0
clock_speed = .2
inside_the_zone = False
position_long_open = False
position_short_open = False
#Fixed Declarations End





#Connecting To The Binance Server
print("Connecting To The Binance Server")
client = Client(api_key,api_secret)
print("Connection Successful")
#Connection Complete

#Tested
def CloseOrder(OrderType:str):
    global ticker
    global lever
    global quant
    orderBuy = client.futures_change_leverage(symbol=ticker, leverage=lever)
   
    #reversing the order type to close the position
   
    if OrderType == 'BUY':
       OrderType = 'SELL'
    else:
       OrderType = 'BUY'
    try:
       print(client.futures_create_order(
       symbol=ticker,
       type='MARKET',
       side=OrderType,
       quantity=quant,
       reduceOnly=True))
       print(OrderType+" Closed Successfuly")
    #Reduce Only Ensures This Does Not Open A New Order And Only Closes The Existing Order
    except:
       print("No "+OrderType+" Order To Close")
   



#Tested
def openOrder(OrderType:str):
    
    global ticker
    global lever
    global quant
    orderBuy = client.futures_change_leverage(symbol=ticker, leverage=lever)
    print(client.futures_create_order(
       symbol=ticker,
       type='MARKET',
       side=OrderType,
       quantity=quant))
    print(OrderType+" Placed Successfuly")

#Tested
def getLivePrice():
    
    global live_price
    global clock_speed
    global order_point
    
    while True:
       data = (client.futures_symbol_ticker(symbol=ticker))
       live_price = float(data['price'])
       print(f'The Current Price is {live_price}')
       print(f'The Order Point is {order_point}')
       time.sleep(clock_speed)



#Tested
def zone_identifier_process():
    
    global zones
    global live_price
    global inside_the_zone
    while True:
        c = len(zones)
        counter = 0
        found  = False
        while counter != c:
            zone = zones[counter]
            if live_price <= zone[0] and live_price >= zone[1]:
                found = True
            counter = counter + 1
            
        if found:
            inside_the_zone = True
        else:
            inside_the_zone = False


def order_execution:
    
    global order_point
    global live_price

    
    
    while True:

        
        if live_price >= order_point:
            
            if position_long_open != True:
                
                if position_short_open:
                    
                    CloseOrder('SELL')
                    position_short_open = False

                openOrder('BUY')
                order_point = live_price

        else:
            
            if position_short_open != True:
                
                if position_long_open:
                    
                    CloseOrder('BUY')
                    position_long_open = False
                    
                openOrder('SELL')
                order_point = live_price
                
        time.sleep(.2)
                    



    

if __name__ == '__main__':

    print('Starting The Bot')
    Price_Updater = threading.Thread(target = getLivePrice)
    Price_Updater.start()
    time.sleep(.2)
    Zone_Identifier_Thread = threading.Thread(target = zone_identifier_process)
    Zone_Identifier_Thread.start()

print(percentage_leveraged_change(1,1.1,10))
