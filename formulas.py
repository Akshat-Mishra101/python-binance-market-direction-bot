import time
from binance import Client
from decimal import Decimal
import threading



def percentage_change(initial, final):
    return ((final-initial)/initial)*100

def percentage_leveraged_change(initial, final, leverage):
    return ((final-initial)/initial)*100*leverage

