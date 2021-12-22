



def percentage_change(initial, final):
    return ((final-initial)/final)*100

def percentage_leveraged_change(initial, final, leverage):
    return ((final-initial)/final)*100*leverage


print(percentage_leveraged_change(1.3,1.3688,20))


