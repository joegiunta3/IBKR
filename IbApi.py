import time
import threading
# import requests
import math
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order_condition import Create, OrderCondition
from ibapi.order import *
from ibapi.common import MarketDataTypeEnum
# from Testbed.ContractSamples import ContractSamples
# from Testbed.OrderSamples import OrderSamples


# IB API
IB_IP_ADDRESS = '127.0.0.1'
IB_SOCKET_PORT = 7497
IB_CLIENT_ID = 123

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print('The next valid order id is: ', self.nextorderId)

    def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        print('orderStatus - orderid:', orderId, 'status:', status, 'filled',
              filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice)

    def openOrder(self, orderId, contract, order, orderState):
        print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange,
              ':', order.action, order.orderType, order.totalQuantity, orderState.status)

    def execDetails(self, reqId, contract, execution):
        print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency,
              execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)

    def updateAccountValue(self, key: str, val: str, currency: str, accountName: str):
        if key == 'BuyingPower':
            print("UpdateAccountValue. Key:", key, "Value:", val, "Currency:", currency, "AccountName:", accountName)

    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
        # Limit to total cash balance
        if ('TotalCashBalance' == tag and self.tickPriceIsRunning == True):
            print('Got account summary')
            print("AccountSummary. ReqId:", reqId, "Account:", account, "Tag: ", tag, "Value:", value, "Currency:", currency)
            print('account value:')
            print(value)
            self.accountInfo = value

    def accountSummaryEnd(self, reqId: int):
        print("AccountSummaryEnd. ReqId:", reqId)
        # Trigger end of fetching account
        if (self.isBuyRunning == True):
            self.isBuyRunning = False
            if self.accountInfo:
                self.accountSummaryFuncEnd(self.accountInfo)
            else:
                print("Can't find account price of account")
        
    def tickPrice(self, reqId, tickType, price, attrib):
        # if tickType == 2 and reqId == 1:
        # https://interactivebrokers.github.io/tws-api/tick_types.html
        print('Check Account info and symbol:', self.accountInfo, self.currentSymbol)
        # buyInPriceStr, targetPriceFinalStr
        print('Testing all ticker attributes:', self.currentSymbol, self.buyInPriceStr, self.targetPriceFinalStr, price, reqId, tickType)
        # if tickType and tickType == 9 and self.tickPriceIsRunning == True:
        if tickType and tickType == 4 and self.tickPriceIsRunning == True:
            self.tickPriceIsRunning = False
            print('Fetched Stock Price:', price)
            print('Check Account info and symbol:', self.accountInfo, self.currentSymbol)
            print('Testing all ticker attributes:', self.currentSymbol, price, reqId, tickType)
            # if self.tickPriceIsRunning == True:
            # self.tickPriceFuncEnd(price, self.accountInfo, self.currentSymbol)
            buyOrderRecivedStockPrice(price, self.accountInfo, self.currentSymbol, self.buyInPriceStr, self.targetPriceFinalStr)
            # if (self.tickPriceFuncEnd and price and self.accountInfo and self.currentSymbol):
            # else:
            #     print('Something went wrong, check queque construction')

    # def BracketOrder(parentOrderId:int, action:str, quantity:float, limitPrice:float, takeProfitLimitPrice:float, stopLossPrice:float):
    #     # This will be our main or "parent" order
    #     parent = Order()
    #     parent.orderId = parentOrderId
    #     parent.action = action
    #     parent.orderType = "STP LMT"
    #     parent.totalQuantity = quantity
    #     parent.lmtPrice = limitPrice * 1.01
    #     parent.auxPrice = limitPrice
    #     #The parent and children orders will need this attribute set to False to prevent accidental executions.
    #     #The LAST CHILD will have it set to True, 
    #     parent.transmit = False

    #     takeProfit = Order()
    #     takeProfit.orderId = parent.orderId + 1
    #     takeProfit.action = "SELL" if action == "BUY" else "BUY"
    #     takeProfit.orderType = "LMT"
    #     takeProfit.totalQuantity = quantity
    #     takeProfit.lmtPrice = takeProfitLimitPrice
    #     takeProfit.parentId = parentOrderId
    #     takeProfit.transmit = True

    #     # stopLoss = Order()
    #     # stopLoss.orderId = parent.orderId + 2
    #     # stopLoss.action = "SELL" if action == "BUY" else "BUY"
    #     # stopLoss.orderType = "STP"
    #     # #Stop trigger price
    #     # stopLoss.auxPrice = stopLossPrice
    #     # stopLoss.totalQuantity = quantity
    #     # stopLoss.parentId = parentOrderId
    #     # #In this case, the low side order will be the last child being sent. Therefore, it needs to set this attribute to True 
    #     # #to activate all its predecessors
    #     # stopLoss.transmit = True

    #     bracketOrder = [parent, takeProfit]
    #     return bracketOrder

def run_loop():
    app.run()

# intially set class
app = IBapi()
app.connect(IB_IP_ADDRESS, IB_SOCKET_PORT, IB_CLIENT_ID)
app.nextorderId = None

# Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

# Check if the API is connected via orderid
while True:
    if isinstance(app.nextorderId, int):
        print('connected')
        break
    else:
        print('waiting for connection')
        time.sleep(0.4)

# Proceed with order creation once stock price comes in
def buyOrderRecivedStockPrice(stockPrice, accountBalance, symbol, buyInPriceStr, targetPriceFinalStr):
    print("buyOrderRecivedStockPrice: stockPrice recieved")
    # print(stockPrice, accountBalance, symbol)
    print(accountBalance, symbol)
    # Cancel/Unsubscribe reqAccountSummary and reqMktData
    app.cancelMktData(app.nextorderId)
    app.cancelAccountSummary(app.nextorderId)
    #Debug to check arg
    
    # print("<<DEBUGGING buyOrderReceivedStockPrice>> targetPriceFinalStr:",targetPriceFinalStr, type(targetPriceFinalStr))
    # targetPriceFinalFLT = targetPriceFinalStr
    
    
    # try:
    #     targetPriceFinalFLT = float(targetPriceFinalStr)
    #     # check if targetPriceFinalStr%2 = 0
    #     # if true then price+targetPriceFinalStr/100 cents
    #     # else takeProfitLimitPriceNum can take targetPriceFinalFLT explicitly
    #     if (targetPriceFinalFLT%2 == 0):
    #         targetPriceFinalFLT = float(buyInPriceStr)+(targetPriceFinalFLT/100)
    #         print("Calculation of cents:", targetPriceFinalFLT)
    #         takeProfitLimitPriceNum = round(targetPriceFinalFLT * 0.996, 2)
    #     else:
    #         print("<<< not a cent increase, take the target >>>")
    #         takeProfitLimitPriceNum = round(targetPriceFinalFLT * 0.996, 2)
    #         if (takeProfitLimitPriceNum <= buyInPriceStr):
    #             print("<<< detected target lower than buy-in")
    #             takeProfitLimitPriceNum = round(float(buyInPriceStr)*1.03, 2)
    # except:
    #     takeProfitLimitPriceNum=round(buyInPriceStr*0.998,2)
    #     #takeProfitLimitPriceNum=round(stockPrice*1.03,2)
    #     print("Can't convert targetPriceFinalStr to float, default to 3% PT:",takeProfitLimitPriceNum)
    
    # try:
    #     targetPriceFinalFLT = float(targetPriceFinalStr)
    #     # check if targetPriceFinalStr%2 = 0
    #     # if true then price+targetPriceFinalStr/100 cents
    #     # else takeProfitLimitPriceNum can take targetPriceFinalFLT explicitly
    #     if (targetPriceFinalFLT%2 == 0):
    #         targetPriceFinalFLT = float(buyInPriceStr)+(targetPriceFinalFLT/100)
    #         print("Calculation of cents:", targetPriceFinalFLT)
    #         takeProfitLimitPriceNum = round(targetPriceFinalFLT * 0.996, 2)
    #     else:
    #         takeProfitLimitPriceNum = round(targetPriceFinalFLT * 0.996, 2)
    # except:
    #     takeProfitLimitPriceNum=round(stockPrice*1.03,2)
    #     print("Can't convert targetPriceFinalStr to float, default to 3% PT:",takeProfitLimitPriceNum)
        #takeProfitLimitPriceNum=round(stockPrice*1.03,2)
    
    # print("<<DEBUGGING buyOrderReceivedStockPrice>> targetPriceFinalStr:",targetPriceFinalStr, type(targetPriceFinalStr))
    # targetPriceFinalFLT = float(targetPriceFinalStr)
    # print("Is this a float or not?:", type(targetPriceFinalFLT))
    # try:
    #     targetPriceFinalFLT = float(targetPriceFinalStr)
    #     takeProfitLimitPriceNum = round(targetPriceFinalFLT * 0.996, 2)
    # except:
    #     print("Can't convert targetPriceFinalStr to float")
    #     takeProfitLimitPriceNum=round(stockPrice*1.03,2)
    
    #limitPriceBuyStopNum = float(buyInPriceStr)
    # limitPriceBuyStopNumOrg = float(buyInPriceStr)
    # limitPriceBuyStopNumTrailLimitStop = float(buyInPriceStr)
    # limitPriceBuyStopNumTrailLimitStopLimitOffset = float(buyInPriceStr)
    #I commented these out...Should be fine
    
    #stopLossPrice = float(targetPriceFinalStr)
    
    # Discount value, Together "Buy Stop" with a "Sell Limit" at 0.5% before entry price. 0.5% down from target.
    # limitPriceBuyStopNum = round((limitPriceBuyStopNum), 2)
    # limitPriceBuyStopNum = round(limitPriceBuyStopNum * 0.985, 2)
    #limitPriceBuyStopNum = round(limitPriceBuyStopNum * 0.995, 2)
    # limitPriceBuyStopNumLimit = round((limitPriceBuyStopNum * 1.04), 2)
    # limitPriceBuyStopNumTrailLimitStop = round((limitPriceBuyStopNumTrailLimitStop * 1.015), 2)
    # limitPriceBuyStopNumTrailLimitStopLimitOffset = round((limitPriceBuyStopNumTrailLimitStopLimitOffset * 0.003), 2)
    # limitPriceBuyStopNum = round((limitPriceBuyStopNum - 0.01), 2)
    
    #takeProfitLimitPriceNum = round(limitPriceBuyStopNum * 1.08, 2)
    # stopLossPriceAUX = round(limitPriceBuyStopNum * 0.9865, 2)
    #takeProfitLimitPriceNum = round(float(buyInPriceStr * 0.998, 2))
    takeProfitLimitPriceNum = buyInPriceStr
    stopLossPrice = round(stockPrice * 0.965, 2)
    #stopLossPrice = round(limitPriceBuyStopNum * 0.985, 2)
    # takeProfitLimitPriceNum =  round(takeProfitLimitPriceNum * 0.995, 2)
    
    # Math for discount value, needed for order to be filled
    # priceStock = stockPrice
    # Either 50 dollars or 1% discount for charges
    accountFeePreventionProgramTotal = float(accountBalance) * 0.08
    
    
    #Orginal Math
    
    # print("<<DEBUGGING buyOrderReceivedStockPrice>> targetPriceFinalStr:",targetPriceFinalStr)

    # #limitPriceBuyStopNum = float(buyInPriceStr)
    # # limitPriceBuyStopNumOrg = float(buyInPriceStr)
    # # limitPriceBuyStopNumTrailLimitStop = float(buyInPriceStr)
    # # limitPriceBuyStopNumTrailLimitStopLimitOffset = float(buyInPriceStr)
    # #I commented these out...Should be fine
    # takeProfitLimitPriceNum = float(targetPriceFinalStr)
    # stopLossPrice = float(targetPriceFinalStr)
    
    # # Discount value, Together "Buy Stop" with a "Sell Limit" at 0.5% before entry price. 0.5% down from target.
    # # limitPriceBuyStopNum = round((limitPriceBuyStopNum), 2)
    # # limitPriceBuyStopNum = round(limitPriceBuyStopNum * 0.985, 2)
    # #limitPriceBuyStopNum = round(limitPriceBuyStopNum * 0.995, 2)
    # # limitPriceBuyStopNumLimit = round((limitPriceBuyStopNum * 1.04), 2)
    # # limitPriceBuyStopNumTrailLimitStop = round((limitPriceBuyStopNumTrailLimitStop * 1.015), 2)
    # # limitPriceBuyStopNumTrailLimitStopLimitOffset = round((limitPriceBuyStopNumTrailLimitStopLimitOffset * 0.003), 2)
    # # limitPriceBuyStopNum = round((limitPriceBuyStopNum - 0.01), 2)
    # takeProfitLimitPriceNum = round(targetPriceFinalStr * 0.996, 2)
    # #takeProfitLimitPriceNum = round(limitPriceBuyStopNum * 1.08, 2)
    # # stopLossPriceAUX = round(limitPriceBuyStopNum * 0.9865, 2)
    # stopLossPrice = round(stockPrice * 0.95, 2)
    # #stopLossPrice = round(limitPriceBuyStopNum * 0.985, 2)
    # # takeProfitLimitPriceNum =  round(takeProfitLimitPriceNum * 0.995, 2)
    
    # # Math for discount value, needed for order to be filled
    # # priceStock = stockPrice
    # # Either 50 dollars or 1% discount for charges
    # accountFeePreventionProgramTotal = float(accountBalance) * 0.08
    # # accountFeePreventionProgramTotal = float(accountBalance) * 0.88
    # print('Discount Value:')
    print(accountFeePreventionProgramTotal)
    availableBalance = float(accountBalance) - accountFeePreventionProgramTotal
    print('availableBalance after discount value')
    print(availableBalance)
    
    # Override amount to put in
    #availableBalance = 1050

    # # Math for quantity
    orderQuantity = math.floor(float(availableBalance) / float(stockPrice))
    #orderQuantity = math.floor(float(availableBalance) / float(limitPriceBuyStopNum))
    print('orderQuantity: rounded')
    print(orderQuantity)
    
    # rounded to two decimal places price
    # priceStock = round(priceStock, 2)
    # print('price: rounded')
    # print(priceStock)

    order = Order()
    order.action = 'BUY'
    # order.totalQuantity = 1
    order.totalQuantity = orderQuantity
    order.orderType = 'MKT'
    # order.orderType = 'LMT'
    # order.lmtPrice = priceStock
    # order.sweepToFill = True

    contract = Contract()
    contract.symbol = symbol
    contract.secType = 'STK'
    contract.currency = "USD"
    contract.exchange = 'SMART'
    contract.primaryExchange = "ISLAND"
    # contract.exchange = 'ISLAND'
    
    
    # contract.symbol = 'EUR'
    # contract.secType = 'CASH'
    # contract.exchange = 'IDEALPRO'
    # contract.currency = "USD"
    
    # Place order
    # app.placeOrder(app.nextorderId, contract, order)
    # app.nextorderId += 1
    # print("BUY............................................................................................")

    
    print("buyOrderRecivedStockPrice : stockPrice recieved")
    # print(stockPrice, accountBalance, symbol, orderQuantity, limitPriceBuyStopNum, takeProfitLimitPriceNum, 0)
    print(accountBalance, symbol, orderQuantity, targetPriceFinalStr, takeProfitLimitPriceNum, 0)
    #print(accountBalance, symbol, orderQuantity, limitPriceBuyStopNum, takeProfitLimitPriceNum, 0)
    # print("round(limitPriceBuyStopNum * 1.01, 2):", round(limitPriceBuyStopNum * 1.01, 2))
    
    
    # bracket = OrderSamples.BracketOrder(app.nextOrderId(), "BUY", quantityAtBuy, limitPriceBuyStopNum, takeProfitLimitPriceNum, 0)
    
    # Place order Braket 
    # app.placeOrder(app.nextorderId, contract, order)
    # app.nextorderId += 1
    
    # action = "BUY"
    # parent = Order()
    # parent.orderId = app.nextorderId
    # parent.action = action
    # parent.orderType = "STP"
    # parent.totalQuantity = orderQuantity
    # parent.auxPrice = limitPriceBuyStopNum
    # 
    if stockPrice >= 3:
        action = "BUY"
        parent = Order()
        parent.orderId = app.nextorderId
        parent.action = action
        parent.hidden = True
        print("stockPrice > limitPriceBuyStopNum")
        print(stockPrice)
        #print(limitPriceBuyStopNum)
        parent.orderType = "MKT"
        parent.totalQuantity = orderQuantity
        #if stockPrice >= limitPriceBuyStopNum:
            # Buy at market if above the 2% plank
            #parent.orderType = "MKT"
            #parent.totalQuantity = orderQuantity
        #else:
            # Buy with stop order if below the 2% plank
            #parent.orderType = "STP"
            #parent.totalQuantity = orderQuantity
            #parent.auxPrice = limitPriceBuyStopNum
            
        
        # parent.lmtPrice = round(limitPriceBuyStopNum * 1.01, 2)
        # parent.orderType = "STP LMT"
        # parent.totalQuantity = orderQuantity
        # parent.lmtPrice = round(limitPriceBuyStopNum * 1.01, 2)
        # parent.auxPrice = limitPriceBuyStopNum
        #The parent and children orders will need this attribute set to False to prevent accidental executions.
        #The LAST CHILD will have it set to True, 
        parent.transmit = False

        takeProfit = Order()
        takeProfit.orderId = parent.orderId + 1
        takeProfit.action = "SELL" if action == "BUY" else "BUY"
        takeProfit.orderType = "LMT"
        takeProfit.hidden = True
        takeProfit.totalQuantity = orderQuantity
        takeProfit.lmtPrice = takeProfitLimitPriceNum
        takeProfit.parentId = app.nextorderId
        takeProfit.transmit = False

        stopLoss = Order()
        stopLoss.orderId = parent.orderId + 2
        stopLoss.action = "SELL"
        stopLoss.orderType = "STP"
        # stopLoss.lmtPrice = stopLossPrice
        stopLoss.hidden = True
        #Stop trigger price
        stopLoss.auxPrice = stopLossPrice
        stopLoss.totalQuantity = orderQuantity
        stopLoss.parentId = app.nextorderId
        stopLoss.transmit = True
        #In this case, the low side order will be the last child being sent. Therefore, it needs to set this attribute to True 
        #to activate all its predecessors
        # stopLoss.transmit = True
        
        
        
        
        # //Attached order is a conventional STP order
        # Order order = Stop(parent.Action.Equals("BUY") ? "SELL" : "BUY", parent.TotalQuantity, attachedOrderStopPrice);
        # order.ParentId = parent.OrderId;
        # # //When trigger price is penetrated
        # order.TriggerPrice = triggerPrice;
        # # //The parent order will be turned into a TRAIL order
        # order.AdjustedOrderType = "TRAIL";
        # # //With a stop price of...
        # order.AdjustedStopPrice = adjustedStopPrice;
        # # //traling by and amount (0) or a percent (100)...
        # order.AdjustableTrailingUnit = trailUnit;
        # # //of...
        # order.AdjustedTrailingAmount = adjustedTrailAmount;
        
        # Order order = new Order();
        # order.Action = action;
        # order.OrderType = "TRAIL LIMIT";
        # order.TotalQuantity = quantity;
        # order.TrailStopPrice = trailStopPrice;
        # order.LmtPriceOffset = lmtPriceOffset;
        # order.AuxPrice = trailingAmount;
        
        # stopTrailingLoss = Order()
        # stopTrailingLoss.orderId = parent.orderId + 3
        # stopTrailingLoss.action = "SELL"
        # stopTrailingLoss.orderType = "TRAIL LIMIT"
        # # stopTrailingLoss.trailStopPrice = stopLossPriceAUX
        # stopTrailingLoss.trailingPercent = 1.5
        # # stopTrailingLoss.auxPrice = limitPriceBuyStopNum
        # stopTrailingLoss.trailStopPrice = limitPriceBuyStopNumTrailLimitStop
        # # Needed for trail limit https://interactivebrokers.github.io/tws-api/basic_orders.html#trailingstop
        # stopTrailingLoss.lmtPriceOffset = limitPriceBuyStopNumTrailLimitStopLimitOffset #Important: the 'limit offset' field is set by default in the TWS/IBG settings in v963+.
        # # This setting either needs to be changed in the Order Presets, the default value accepted, or the limit price offset sent from the API as in the example below. Not both the 'limit price' and 'limit price offset' fields can be set in TRAIL LIMIT orders.
        
        # # stopTrailingLoss.auxPrice = limitPriceBuyStopNum * 0.015
        # # stopTrailingLoss.lmtPrice = stopLossPrice
        # # stopTrailingLoss.adjustedStopPrice = stopLossPrice
        # # stopTrailingLoss.adjustableTrailingUnit = stopLossPrice
        # # stopTrailingLoss.adjustedTrailingAmount = stopLossPrice
        # stopTrailingLoss.hidden = True
        # #Stop trigger price
        # # stopTrailingLoss.auxPrice = stopLossPriceAUX
        # stopTrailingLoss.totalQuantity = orderQuantity
        # stopTrailingLoss.parentId = app.nextorderId
        # #In this case, the low side order will be the last child being sent. Therefore, it needs to set this attribute to True 
        # #to activate all its predecessors
        # stopTrailingLoss.transmit = True

        #bracketOrder = [parent, takeProfit]
        
        #Uncomment below to send buy order
        
        bracketOrder = [parent, takeProfit, stopLoss]
        # bracketOrder = [parent, takeProfit, stopLoss, stopTrailingLoss]
        
        # bracket = OrderSamples.BracketOrder(app.nextOrderId(), "BUY", orderQuantity, limitPriceBuyStopNum, takeProfitLimitPriceNum, 0)
        for o in bracketOrder:
            app.placeOrder(o.orderId, contract, o)
            app.nextorderId += 1  # need to advance this we'll skip one extra oid, it's fine
            # app.nextOrderId()  # need to advance this we'll skip one extra oid, it's fine
        print("BUY............................................................................................")
        
        
        ########################################
        #<< Profit taker of 8% of buyin price >>#
        ########################################
        # takeProfitSafe = Order()
        # takeProfitSafe.action = "SELL"
        # takeProfitSafe.orderType = "LMT"
        # takeProfitSafe.hidden = True
        # takeProfitSafe.totalQuantity = orderQuantity
        # takeProfitSafe.lmtPrice = round(float(stockPrice) * 1.08, 2)
        # app.nextorderId + 3
        # time.sleep(5)
        # app.placeOrder(app.nextorderId, contract, takeProfitSafe)

        
        # time.sleep(4)
        # sell_order_low = Order()
        # sell_order_low.action = 'SELL'
        # sell_order_low.totalQuantity = orderQuantity
        # sell_order_low.orderType = 'STP LMT'
        # # rounded to two decimal places price
        # sell_order_low.auxPrice = round((priceStock * 0.995), 2)
        # sell_order_low.lmtPrice = round((priceStock * 0.99), 2)
        # # sell_order.orderId = app.nextorderId

        # #Place Order
        # app.placeOrder(app.nextorderId, contract, sell_order_low)
        # app.nextorderId += 1

        # print("SEll LOW............................................................................................")
        
        # sell_order = Order()
        # sell_order.action = 'SELL'
        # sell_order.totalQuantity = orderQuantity
        # sell_order.orderType = 'LMT'
        # # rounded to two decimal places price
        # sell_order.lmtPrice = round((priceStock * 1.08), 2)
        # # sell_order.orderId = app.nextorderId

        # #Place Order
        # app.placeOrder(app.nextorderId, contract, sell_order)
        # app.nextorderId += 1
    else:
        print("AVOID Buying into lower than 3 dolars..................................................................")
        # print("SEll HIGH............................................................................................")
    

# Proceed with order creation once account balance to comes in
def buyOrderRecivedTotalCashValue(accountBalance):
    print('accountBalance')
    print(accountBalance)
    
    contract = Contract()
    # Stock price check example
    contract.symbol = app.currentSymbol
    contract.secType = 'STK'
    contract.exchange = 'ISLAND'
    contract.currency = "USD"
    
    # # Foreign exchange example
    # # contract.symbol = 'EUR'
    # # contract.secType = 'CASH'
    # # contract.exchange = 'IDEALPRO'
    # # contract.currency = "USD"
    
    # # app.reqMarketDataType(MarketDataTypeEnum.DELAYED) # delay market data, avoid live data
    app.tickPriceIsRunning = True
    app.tickPriceFuncEnd = buyOrderRecivedStockPrice
    print('start fetching stock price')
    # app.reqMktData(1, contract, '', False, False, [])
    app.reqMktData(app.nextorderId, contract, '', False, False, [])
    
    # buyOrderRecivedStockPrice(app.accountInfo, app.currentSymbol, app.buyInPriceStr, app.targetPriceFinalStr)

    
    # getaPriceApiUrl = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=' + app.currentSymbol + '&apikey=' + 'IYEH6893HJY7QYMA'
    
    # upperCaseSymbol = app.currentSymbol.upper()
    # getaPriceApiUrl = 'https://finnhub.io/api/v1/quote?symbol=' + upperCaseSymbol + '&token=' + 'c2i5ntqad3idsa35ii5g'
    # print("getaPriceApiUrl")
    # print(getaPriceApiUrl)
    # r = requests.get(getaPriceApiUrl)
    # jsonReturnPrice = r.json()
    # print(jsonReturnPrice)
    # print('Current Price Finnhub')
    # stockPriceCurrent = jsonReturnPrice['c']
    # print(stockPriceCurrent)
    # buyOrderRecivedStockPrice(float(stockPriceCurrent), app.accountInfo, app.currentSymbol)

# Function to fetch account balance
def buyOrder(symbol, buyInPriceStr, targetPriceFinalStr):
    app.isBuyRunning = True
    app.currentSymbol = symbol
    # buyInPriceStr, targetPriceFinalStr
    app.buyInPriceStr = buyInPriceStr
    app.targetPriceFinalStr = targetPriceFinalStr
    app.tickPriceIsRunning = True
    app.accountSummaryFuncEnd = buyOrderRecivedTotalCashValue
    app.reqAccountSummary(app.nextorderId, "All", "$LEDGER:USD")
    # app.reqAccountSummary(app.nextorderId, "All", "TotalCashValue")
    
    # app.reqAccountSummary(app.nextorderId, "All", "TotalCashValue")
    
    # Test runs
    # app.reqAccountUpdates(True, 'DUC00074')
    # app.reqAccountUpdates(True, 'DU3939851')
