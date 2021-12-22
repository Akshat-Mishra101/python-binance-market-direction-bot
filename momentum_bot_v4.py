from formulas import *
import time
from binance import Client
from decimal import Decimal
import threading


api_key = ''
api_secret = ''


lever = 20
quant = 13
order_point = 1.3

ticker = 'ALGOUSDT'

trigger = True #if true, we perform a buy when the price reaches the order point, if not then the bot follows its usual process


zones = [[2800,2700]] #Two Zones Defined

#Fixed Declarations
live_price = 0
clock_speed = .2
inside_the_zone = False
position_long_open = False
position_short_open = False
initial = False

#Profit Systems
intermediate_order_point = order_point
trailing_long_target = 5
trailing_long_base = 3

trailing_long_shift = trailing_long_target - trailing_long_base


trailing_short_target = 5
trailing_short_base = 3

trailing_short_shift = trailing_short_target - trailing_short_base

long_order_point_shifted = False
short_order_point_shifted = False



#Fixed Declarations End





#Connecting To The Binance Server
print("Connecting To The Binance Server")
client = Client(api_key,api_secret)
print("Connection Successful")
#Connection Complete


#profit trailing mechanism

def target_chaser():
    global intermediate_order_point
    
    global order_point
    global live_price
    global lever

    global trailing_long_target
    global trailing_long_base

    global trailing_short_target
    global trailing_short_base

    global position_long_open
    global position_short_open
    
    global trailing_long_shift
    global trailing_short_shift
    
    while True:

        profit = abs(percentage_leveraged_change(intermediate_order_point,live_price,lever))
        
        print(f'Profit on {intermediate_order_point} and {live_price} with leverge {lever} is {profit}')


        if position_long_open and profit >= 1:
            print(f"Leveraged Profit on long is {profit}")
        if position_short_open and profit >= 1:
            print(f"Leveraged Profit on short is {profit}")

        if position_long_open and profit > trailing_long_target and profit == (trailing_long_target + trailing_long_shift): #Price Has Reached The Profit Target
            
            trailing_long_target = trailing_long_target + trailing_long_shift
            trailing_long_base = trailing_long_base + trailing_long_shift
            
            print(f"short targets shifted to, current {trailing_long_target} and cutoff {trailing_long_base}")
            
        if position_short_open and profit > trailing_short_target and profit == (trailing_short_target + trailing_short_shift):
            
            trailing_short_target = trailing_short_target + trailing_short_shift
            trailing_short_base = trailing_short_base + trailing_short_shift
            
            print(f"short targets shifted to, current {trailing_short_target} and cutoff {trailing_short_base}")
      
            
            
            
def profit_taker():
    
    global order_point
    global live_price
    global lever
    global intermediate_order_point

    global long_order_point_shifted
    global short_order_point_shifted

    global trailing_long_target
    global trailing_long_base

    global trailing_short_target
    global trailing_short_base

    global trailing_long_shift
    global trailing_short_shift
    
    long_order_point_shift = trailing_long_shift/lever
    short_order_point_shift = trailing_short_shift/lever
    
    while True:
        
        
        profit = round(abs(percentage_leveraged_change(intermediate_order_point,live_price,lever)))
        print(f'Profit is {profit} in profit taker')
        if position_long_open and profit == trailing_long_target:
            
            order_point = order_point + ((long_order_point_shift/100)*order_point)
            long_order_point_shifted = True
            
            print("Order Point Shifted For Long")
            
        if position_short_open and profit == trailing_short_target:
            
            order_point = order_point - ((short_order_point_shift/100)*order_point)
            short_order_point_shifted = True
            
            print("Order Point Shifted For Short")
        
            



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
    global intermediate_order_point
    
    while True:
       data = (client.futures_symbol_ticker(symbol=ticker))
       live_price = float(data['price'])
       print(f'The Current Price is {live_price} and The Order Point is {order_point} and the intermediate order point is {intermediate_order_point}')
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

#Tested
def order_execution():
    
    
    global order_point
    global live_price
    global intermediate_order_point

    global clock_speed

    global position_long_open
    global position_short_open

    global long_order_point_shifted
    global short_order_point_shifted

    global trailing_long_base
    global trailing_short_base

    global initial
    
    
    
    while True:

        
        if live_price > order_point:
            
            if position_long_open != True:
                
                
                if position_short_open:

                    if short_order_point_shifted:
                        reset()
                        short_order_point_shifted = False
                        print(f'Profits Booked And Positions Closed at {trailing_long_base} percent profit')
                        
                    
                    CloseOrder('SELL')
                    position_short_open = False

                

                openOrder('BUY')
                order_point = live_price
                intermediate_order_point  = order_point
                position_long_open  = True

        elif live_price < order_point:
            
            
            if position_short_open != True:
                
                if position_long_open:

                    if long_order_point_shifted:
                        reset()
                        long_order_point_shifted = False
                        print(f'Profits Booked And Positions Closed at {trailing_short_base} percent profit')
                        
                    
                    CloseOrder('BUY')
                    position_long_open = False

                
                    
                openOrder('SELL')
                order_point = live_price
                intermediate_order_point  = order_point
                position_short_open = True

        else:
            print("Price At BreakEven")
        
                

                
                    

def reset():
    global order_point
    global intermediate_order_point

    global trailing_long_target
    global trailing_long_base

    global trailing_short_target
    global trailing_short_base

    intermediate_order_point = order_point

    trailing_long_target = 5
    trailing_long_base = 3

    trailing_short_target = 5
    trailing_short_base = 3
    print("Values Reset")
    

if __name__ == '__main__':
    

    print('Starting The Bot')
    Price_Updater = threading.Thread(target = getLivePrice)
    Price_Updater.start()
    time.sleep(2)
    Zone_Identifier_Thread = threading.Thread(target = zone_identifier_process)
    Zone_Identifier_Thread.start()
    Order_Executor_Thread = threading.Thread(target = order_execution)
    Order_Executor_Thread.start()
    time.sleep(.2)

    Profit_Target_Shifter = threading.Thread(target = target_chaser)
    Profit_Target_Shifter.start()
    Profit_Executor = threading.Thread(target = profit_taker)
    Profit_Executor.start()

    



    

#print(percentage_leveraged_change(1,1.1,10))
