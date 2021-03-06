import json
import datetime
import urllib2
import math
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def input():
  return render_template('home.html')

@app.route("/map_stocks", methods=['POST'])
def mapStock():
  amount = request.form.get('amount')
  strategy = request.form.get('strategy')
  amount = float(amount)

  stockAmounts = []
  partAmount = math.floor(amount/3)
  stockAmounts.append(partAmount)
  stockAmounts.append(partAmount)
  stockAmounts.append(amount - partAmount * 2)

  stocks = getMapStocks(strategy)
  stocks[0]['amount'] = stockAmounts[0]
  stocks[1]['amount'] = stockAmounts[1]
  stocks[2]['amount'] = stockAmounts[2]

  return render_template('map_stocks.html', stock1=stocks[0], stock2=stocks[1], stock3=stocks[2])

@app.route("/calculate", methods=['POST'])
def calculate():
  stock1Amount = float(request.form.get('stock1Amount'))
  stock2Amount = float(request.form.get('stock2Amount'))
  stock3Amount = float(request.form.get('stock3Amount'))

  print('stock1Amount = ' + str(stock1Amount));
  print('stock2Amount = ' + str(stock2Amount));
  print('stock3Amount = ' + str(stock3Amount));

  stock1Symbol = request.form.get('stock1Symbol')
  stock2Symbol = request.form.get('stock2Symbol')
  stock3Symbol = request.form.get('stock3Symbol')

  print('stock1Symbol = ' + stock1Symbol);
  print('stock2Symbol = ' + stock2Symbol);
  print('stock3Symbol = ' + stock3Symbol);

  # get buy number of each stock
  stock1 = {'symbol': stock1Symbol, 'amount': stock1Amount, 'buyNumber': 0}
  stock2 = {'symbol': stock2Symbol, 'amount': stock2Amount, 'buyNumber': 0}
  stock3 = {'symbol': stock3Symbol, 'amount': stock3Amount, 'buyNumber': 0}
  getBuyNumber(stock1, stock2, stock3)

  print('buyNumber1 = ' + str(stock1['buyNumber']));
  print('buyNumber2 = ' + str(stock2['buyNumber']));
  print('buyNumber3 = ' + str(stock3['buyNumber']));

  # get historic data
  history = getHistoricData(stock1Symbol, stock2Symbol, stock3Symbol)

  print(history)

  stock1['history'] = history[stock1Symbol]['chart']
  stock2['history'] = history[stock2Symbol]['chart']
  stock3['history'] = history[stock3Symbol]['chart']

  print('======= history of three stocks =========')
  print(stock1['history'])
  print(stock2['history'])
  print(stock3['history'])

  setHistoryTodayValue(stock1, stock2, stock3)
  print('======= TOTAL VALUE of three stocks =========')
  print(stock1['history'][0]['total'])
  print(stock1['history'][1]['total'])
  print(stock1['history'][2]['total'])
  print(stock1['history'][3]['total'])
  print(stock1['history'][4]['total'])
  

  #output
  totalValueNow = stock1Amount + stock2Amount + stock3Amount

  print('totalValueNow = ' + str(totalValueNow))

  date1 = stock1['history'][0]['date']
  date2 = stock1['history'][1]['date']
  date3 = stock1['history'][2]['date']
  date4 = stock1['history'][3]['date']
  date5 = stock1['history'][4]['date']

  print('date1 = ' + date1)
  print('date2 = ' + date2)
  print('date3 = ' + date3)
  print('date4 = ' + date4)
  print('date5 = ' + date5)

  date1Total = stock1['history'][0]['total'] + stock2['history'][0]['total'] + stock3['history'][0]['total']
  date2Total = stock1['history'][1]['total'] + stock2['history'][1]['total'] + stock3['history'][1]['total']
  date3Total = stock1['history'][2]['total'] + stock2['history'][2]['total'] + stock3['history'][2]['total']
  date4Total = stock1['history'][3]['total'] + stock2['history'][3]['total'] + stock3['history'][3]['total']
  date5Total = stock1['history'][4]['total'] + stock2['history'][4]['total'] + stock3['history'][4]['total']
  print('date1Total = ' + str(date1Total))
  print('date2Total = ' + str(date2Total))
  print('date3Total = ' + str(date3Total))
  print('date4Total = ' + str(date4Total))
  print('date5Total = ' + str(date5Total))

  return render_template('dashboard.html', 
    totalValueNow=totalValueNow,
    stock1Symbol=stock1Symbol,
    stock2Symbol=stock2Symbol,
    stock3Symbol=stock3Symbol, 
    stock1Amount=stock1Amount, 
    stock2Amount=stock2Amount, 
    stock3Amount=stock3Amount, 
    date1=date1, 
    date2=date2, 
    date3=date3, 
    date4=date4, 
    date5=date5, 
    date1Total=round(date1Total, 4), 
    date2Total=round(date2Total, 4), 
    date3Total=round(date3Total, 4), 
    date4Total=round(date4Total, 4), 
    date5Total=round(date5Total, 4))

############################ FUNCTIONS ############################
def getMapStocks(strategy):
  if strategy == 'ethical':
    return [
      {'name': 'Apple', 'symbol': 'AAPL'},
      {'name': 'Adobe', 'symbol': 'ADBE'},
      {'name': 'Walmart Inc', 'symbol': 'WMT'}
    ]
  elif strategy == 'growth':
    return [
      {'name': 'WPX Energy', 'symbol': 'WPX', 'amount': 0},
      {'name': 'Square', 'symbol': 'SQ', 'amount': 0},
      {'name': 'Helmerich & Payne', 'symbol': 'HP', 'amount': 0}
    ]
  elif strategy == 'index':
    return [
      {'name': 'Vanguard Total Stock Market ETF', 'symbol': 'VTI', 'amount': 0},
      {'name': 'iShares Core MSCI Total Intl Stk', 'symbol': 'IXUS', 'amount': 0},
      {'name': 'iShares Core 10+ Year USD Bond', 'symbol': 'ILTB', 'amount': 0}
    ]
  elif strategy == 'quality':
    return [
      {'name': 'National Oilwell Varco', 'symbol': 'NOV', 'amount': 0},
      {'name': 'JD.com', 'symbol': 'JD', 'amount': 0},
      {'name': 'ServiceNow', 'symbol': 'NOW', 'amount': 0}
    ]
  elif strategy == 'value':
    return [
      {'name': 'Western Digital', 'symbol': 'WDC', 'amount': 0},
      {'name': 'Lam Research', 'symbol': 'LRCX', 'amount': 0},
      {'name': 'Micron Technology, Inc.', 'symbol': 'MU', 'amount': 0}
    ]

def getHistoricData(symbol1, symbol2, symbol3):
  url = 'https://api.iextrading.com/1.0/stock/market/batch?symbols=' + symbol1 + ',' + symbol2 + ',' + symbol3 + '&types=chart&range=5d&last=5&filter=date,close'
  req = urllib2.Request(url)
  response = urllib2.urlopen(req)
  json_str = response.read()
  print(json_str)
  data = json.loads(json_str);
  return data;

def getBuyNumber(obj1, obj2, obj3):
  url1 = 'https://api.iextrading.com/1.0/stock/' + obj1['symbol'] + '/price'
  print('rul1 = ' + url1)
  req1 = urllib2.Request(url1)
  response1 = urllib2.urlopen(req1)
  obj1['price'] = float(response1.read())
  obj1['buyNumber'] = obj1['amount'] / obj1['price']

  url2 = 'https://api.iextrading.com/1.0/stock/' + obj2['symbol'] + '/price'
  print('rul2 = ' + url2)
  req2 = urllib2.Request(url2)
  response2 = urllib2.urlopen(req2)
  obj2['price'] = float(response2.read())
  obj2['buyNumber'] = obj2['amount'] / obj2['price']

  url3 = 'https://api.iextrading.com/1.0/stock/' + obj3['symbol'] + '/price'
  print('rul3 = ' + url3)
  req3 = urllib2.Request(url3)
  response3 = urllib2.urlopen(req3)
  obj3['price'] = float(response3.read())
  obj3['buyNumber'] = obj3['amount'] / obj3['price']

def setHistoryTodayValue(obj1, obj2, obj3):
  for i in range(5):
    obj1['history'][i]['total'] = obj1['buyNumber'] * obj1['history'][i]['close']
    obj2['history'][i]['total'] = obj2['buyNumber'] * obj2['history'][i]['close']
    obj3['history'][i]['total'] = obj3['buyNumber'] * obj3['history'][i]['close']

if __name__ == '__main__':
    app.run(debug=True)