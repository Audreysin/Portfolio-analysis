import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date
import io
import sys
import matplotlib.pyplot as plt

# Global variables
tickers = [] # Stores the ticker symbols in alphabetical order
weights = [] # Stores the weights, order depends on the tickers list
portfolioDict = {} # Stores key value pairs of [Symbol:weight], a dictionary is used to improve the efficiecy of weight lookup

def introOutput():
    #  Prints the introduction instrustion line
    print("Please enter the stock symbol followed by its weight in the portfolio. Please enter \"Done\" your portfolio is complete.")

def isValidTicker(_ticker):
    #  Checks if the symbol _ticker is a valid ticker
    data = yf.Ticker(_ticker)
    return not(data.history(period="max").empty)

def processInput(input):
    # Reads through the input and extracts the stock symbol and the percentage. 
    # Any character input after the % sign or the numerical input is ignored.
    # Arg: 
    #   Input: String consisting of a sequence of letter-characters and a number 
    #          possibly followed by % symbol. They may be separated by space characters.
    # Returns:
    #   a tuple (a, b, c) 
    #   a is true if the input is a valid input in terms of format. Otherwise it is false.
    #   b is the stock symbol (string)
    #   c is the portfolio weight (float)
    stockSym = ""
    weightStr = "0"
    divisor = 1.0
    index = 0

    # Extracting the stock symbol
    while index < len(input):
        if ((input[index] >= 'A' and input[index] <= 'Z') or (input[index] >= 'a' and input[index] <= 'z')):
             stockSym += input[index]
        elif (input[index] == " "):
            if (stockSym == ""):
                index += 1
                continue
            else:
                break
        elif (input[index] >= '0' and input[index] <= '9'):
            break
        else:
            return (False, stockSym, float(weightStr)/divisor)

        index += 1

    if stockSym == "":
        return (False, stockSym, float(weightStr)/divisor)


    # Extracting the weight
    for char in input[index::]:
        if (char == ' '):
            continue
        elif (char == '%'):
                divisor = 100.0
                break
        elif (char >= '0' and char <= '9'):
            weightStr += char
        elif (char == '.'):
            if (char in weightStr):
                break
            else:
                weightStr += char
        else:
            if (weightStr == "0"):
                return(False, stockSym, float(weightStr)/divisor)
            else:
                break

    return(True, stockSym, float(weightStr)/divisor)

def addToList(ticker, weight):
    # Adds the ticker and its weight to the list of Ticker objects "portfolio" if the ticker was entered for the first time
    # Otherwise, increments the existing weight by the amount "weight"
    
    if ticker in portfolioDict:
        portfolioDict[ticker] += weight
    else:
        portfolioDict[ticker] = weight

def getPortfolioInput():
    # Takes input from the user. If the input is valid, the ticker is added to the portfolio.
    # Otherwise, an appropriate message is output to std io
    print("Enter new ticker:")
    lineInput = input()
    if (lineInput == "Done"):
        return
    tupleInput = processInput(lineInput)
    if tupleInput[0]:
        text_trap = io.StringIO()
        sys.stdout = text_trap
        if isValidTicker(tupleInput[1]):
            sys.stdout = sys.__stdout__
            if (tupleInput[2] == 0):
                print("The weight provided for " + tupleInput[1].upper() + " is zero. So, the ticker was not added.")
            else:
                addToList(tupleInput[1].upper(), tupleInput[2])
                print(tupleInput[1].upper() + " has been added")
        else:
            sys.stdout = sys.__stdout__
            print("The ticker you entered is not valid...")
    else:
        print("Your input is invalid...")
    getPortfolioInput()

def fillList(portfolioDictionary):
    # Fills the lists "tickers", "weights", "portfolioDict". Sorts "tickers" in alphabetical order.
    tickers.clear()
    weights.clear()

    for tkr in portfolioDictionary:
        tickers.append(tkr)
    tickers.sort()
    for index in range(len(tickers)):
        weights.append(portfolioDictionary[tickers[index]])
    

def adjustWeights():
    # If the sum of the weights given is not "1"/"100%" this functions adjust the weights to make the sum 100% while keep the same proportion
    theSum = sum(weights)
    for i in range(len(weights)):
        weights[i] /= theSum

def getPriceChart(lst, fromDate):
    # Plots the stock price chart
    df = yf.download(lst,fromDate)['Adj Close']
    df.plot()
    plt.legend()
    plt.title("Prices", fontsize=16)
    plt.ylabel('Price', fontsize=14)
    plt.xlabel('Date', fontsize=14)
    plt.grid(which="major", color='k', linestyle='-.', linewidth=0.5)
    plt.show()

def getCummulativePortfolioReturn(ticker_lst, weight_lst, fromDate):
    # Plots the cumulative return chart and returns the dataframe containing the daily returns
    prices = yf.download(ticker_lst, fromDate)['Adj Close']
    dailyReturns = prices.pct_change()[1:]
    weighted_returns = dailyReturns * weight_lst
    dailyReturns['Portfolio'] = weighted_returns.sum(axis=1)
    CumulativeReturns = (((1+dailyReturns['Portfolio']).cumprod())-1)
    CumulativeReturns = CumulativeReturns * 100
    CumulativeReturns.plot()
    plt.title("Cumulative Portfolio Return", fontsize=16)
    plt.ylabel('Return (%)', fontsize=14)
    plt.xlabel('Date', fontsize=14)
    plt.grid(which="major", color='k', linestyle='-.', linewidth=0.5)
    plt.show()
    return dailyReturns

def getAvgReturn(dailyReturnsdf):
    # returns the average returns of the portfolio
    return np.mean(dailyReturnsdf['Portfolio'])

def getStd(dailyReturnsdf):
    # returns the standard deviation of the daily returns
    return np.std(dailyReturnsdf['Portfolio'])

def getPortfolioVolatilty(dailyReturnsdf):
    # returns the volatility of the portfolio
    cov_matrix = dailyReturnsdf[tickers].cov()
    print(cov_matrix)
    weight_arr = np.array(weights)
    return np.sqrt(np.dot(weight_arr.T, np.dot(cov_matrix, weight_arr)))

introOutput()
getPortfolioInput()
fillList(portfolioDict)
adjustWeights()
getPriceChart(tickers, "2020-01-01")
returnDf = getCummulativePortfolioReturn(tickers, weights, '2020-01-01')
print("Average daily return over the period: " + str(round(getAvgReturn(returnDf) * 100, 4)) + "%")
print("Average annualized return: " + str(round((((1 + getAvgReturn(returnDf)) ** 252) - 1) * 100, 4)) + "%")
print("Portfolio volatility:  " + str(round(getPortfolioVolatilty(returnDf), 4)))