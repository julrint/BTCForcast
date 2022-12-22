# -*- coding: utf-8 -*-
"""Authoring BTC forecaster

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1582ja7vccR1_MfRM0cpvLC9wIH7c6n5C

# Bitcoin forecasting with Tensorflow and Facebook Prophet
## Nicholas Stewart, Nada Aly, Julian Rintha

In this project we used several libraries to obtain, process and create models to forecast bitcoin prices. The goal was to be able to use this model to attempt to predict a 30-day forecast of bitcoin prices from 11/01/2021 to 12/01/2021. Using Twint, Yahoo Finace, Flair, Tensorflow, Pandas, Numpy, Facebook Prophet and other standard libraries we created 2 models that attempt this forecast.

# Data

Here is where all of the preprocessing is done. We first get tweets to be converted into vectors for sentiment analysis. We plan on including this with closing prices obtained from the Yahoofinance library to get the features for our model.
"""

import pandas as pd

# Commented out IPython magic to ensure Python compatibility.
# %pip install twint
# %pip install git+https://github.com/twintproject/twint.git@origin/master#egg=twint
import twint
import nest_asyncio

"""Below is code for retreiving tweets using Twint. Twint is a webscrapping library for twitter."""

import datetime
import time

def runSearch():
  #time.sleep(30)
  try:
    twint.run.Search(c)
  except Exception:
    #time.sleep(10)
    try: twint.run.Search(c)
    except Exception: pass


start_date = datetime.datetime(2021,1,1)
first_date = datetime.datetime(2021,1,1)
start_end_date = start_date + datetime.timedelta(days=1)
end_date = datetime.datetime(2021,2,1)

df = twint.storage.panda.Tweets_df;
df_temp = twint.storage.panda.Tweets_df;

while (start_date != end_date):
  c = twint.Config()
  c.Search = "bitcoin"
  c.Limit = 1
  c.Lang = 'en'
  c.Since = start_date.strftime("%Y-%m-%d")
  c.Until = start_end_date.strftime("%Y-%m-%d")
  c.Pandas = True
  nest_asyncio.apply()
  if (start_date == first_date):
    runSearch()
    df = twint.storage.panda.Tweets_df
  else:
    runSearch()
    df_temp = twint.storage.panda.Tweets_df
    if (df_temp.empty):
      runSearch()
    df_temp = twint.storage.panda.Tweets_df
    df = pd.concat([df, df_temp], ignore_index=True)
  start_date = start_end_date
  start_end_date += datetime.timedelta(days=1)

"""This code should get a single tweet from everyday in the window. However, there is a compounding problem here. Firstly, we chose to use twint because tweepy no longer works. Tweepy no longer works due to Twitter developing an official API to search and view twitter data. To get access to this official API we needed to create a developer account. We did such but were unpleasantly surprised to find that the twitter API relied on YAML files to make requests to it. A file format that we simply can not incorporate into this environment without significant errors. The grader would need to install the YAML files in their local drive for this notebook to run. Secondly, the basic access only gave us tweets from the last 30 days. To get full archive access we would need to be approved as an institution or research organization.
 
With this method out of the question we moved to third party applications. We found twint, a web scraper that will allow us to get some tweets. There are issues here as well. Firstly, twint is not behaving properly. The above code block asks for just a single tweet from a given day. This library returns a few tweets it can find for that day. Secondly, Twitter itself sometimes blocks this bot from grabbing tweets. The webscraper generates a fake user agent to access Twitter. Twitter has been progressively becoming more resistant to passive attacks like this so it will deny the bot access. Twitter has a new model that you can not view content unless you are logged in. To bypass this twint creates a fake user. However, Twitter is wise to this sometimes and will deny the fake user access. This means the web scraper can't obtain any information from the webpage as it can not get onto the page it needs. You can see above it skips whole days at a time. This leads to a sparse matrix for the tweets. This means some days in our predictor would be missing sentiment.
 
A work around we figured would be to just create a list of sentiment out of random days and call them the sentiment for the specific day we are looking at.
The logic there being, the average sentiment for the day is very volatile. The result is essentially a coin flip. However, since this list is a 'fake' list, the sentiments will have no actual correlation with the day it is associated with.
 
We have concluded there is no reliable way to get the tweets for a given day and that any list we do make will skew the results of the predictor as they will not be accurate/actually associated with the closing price of the coin. For these reasons we have decided to exclude the sentiment in the price predictor development.
"""

df.info()

"""# Tweet Sentiment Analysis"""

# Commented out IPython magic to ensure Python compatibility.
# %pip install importlib-metadata
# %pip install flair
import flair

from flair.models import TextClassifier
from flair.data import Sentence

#make a classifier that will later test if phrase is positive or negative
sentiment_model = flair.models.TextClassifier.load('en-sentiment')

#create sentiment and confidence list
sentiment = []
confidence = []

#loop through tweets
for sentence in df['tweet']:  #tokenizing our sentence (Phrase should be changed to what ehe colum with tweets is called)
  if sentence.strip() == "":  #if there is an empty tweet or phrase there will be an empty sentiment and confidence analysis
    sentiment.append("")
    confidence.append("")
  
  else:
    sample = flair.data.Sentence(sentence)    #splits samples into tokens
    sentiment_model.predict(sample)

    sentiment.append(sample.labels[0].value)
    confidence.append(sample.labels[0].score)

data = {}
df = pd.DataFrame(data)
#make the new columns in the table to show sentiment and confidence of the tweet then show table
df['sentiment'] = sentiment
print(df['sentiment'])

"""The above is the sentiment analysis of all of the tweets that twint was able to grab. Again, this is a 'sparse' list and the values here DO NOT correlate 1 to 1 with the days of the year/window we want to create a model for. This list will not be used in the predictor development because it will skew the model based on fake data.

Importing libraries to load in BTC-USD prices and build a TF model
"""

# Commented out IPython magic to ensure Python compatibility.
# %pip install yfinance
# %pip install yahoofinancials
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard

import os
import pandas as pd
import numpy as np
import yfinance as yf
import datetime
import random

bitcoin_df = yf.download('BTC-USD', start = '2020-01-01', end='2021-10-31', progress=False)
pricedf = bitcoin_df.reset_index()['Close']
import matplotlib.pyplot as plt
plt.plot(pricedf)

"""This is the plot of the closing prices from the specified window. These values must be normalized to be used by the predictor."""

from sklearn.preprocessing import MinMaxScaler
normal = MinMaxScaler(feature_range=(0,1))
pricedf = normal.fit_transform(np.array(pricedf).reshape(-1,1))

plt.plot(pricedf)

"""This is the graph after the values have been normalized from 0-1"""

training_size=int(len(pricedf)*0.7)
test_size= len(pricedf) - training_size
train_data = pricedf[0:training_size,:]
test_data = pricedf[training_size:len(pricedf), :1]

"""Splitting the data into training and test sets. The training data is 70% of the data and the test data is the remaining 30%."""

print(train_data.shape)

#consider timesteps needed to predict a future price
#the predictions at timestep +1 will be the y_train(label)
#x_train is the previous timesteps we have considered
def create_dataset(dataset, timestep):
  x_data, y_data = [], []
  for i in range(len(dataset) - timestep-1):
    element = dataset[i:(i+timestep), 0]
    x_data.append(element)
    y_data.append(dataset[i + timestep, 0])
  return np.array(x_data), np.array(y_data)

timestep = 100
x_train, y_train = create_dataset(train_data, timestep)
x_test, y_test = create_dataset(test_data, timestep)

"""The above code creates a large dataset for everyday in the training/test set. The x array is the previous days considered and the y array is the label(next day) we are trying to find the price for."""

x_test.shape

x_train.shape

y_train.shape

x_train = x_train.reshape(x_train.shape[0],x_train.shape[1], 1)
x_test = x_test.reshape(x_test.shape[0],x_test.shape[1], 1)

"""# Price Predictor Development

Below is a Long Short Term Memory Recurrent Neural Network, built in tensorflow. Each LSTM layer consists of 100 neurons and is followed by a dropout. All of these LSTM layers lead to 1 dense layer, the price. After predicting a price we can invert the normal transform to get back a predicted price in USD.
"""

RNN_model = Sequential([
    LSTM(100, return_sequences=True,input_shape=(100,1),activation='relu'),
    Dropout(0.2),
    LSTM(100, return_sequences=True,activation='relu'),
    Dropout(0.2),
    LSTM(100, activation='relu'),
    Dense(1)
])
RNN_model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])
RNN_model.summary()

"""We then train the model on the modified data set retrieved from Yahoofinance. We use the test data as validation to see how well the network is learning. """

RNN_model.fit(x_train, y_train, validation_data=(x_test, y_test), epochs=20)

"""The network is now trained. We will use the network to predict prices in the test set as well as the training set. By doing this, we can ensure the model has at least a baseline concept of what it is trying to accomplish. The problem here is that, unless we test against a real open-ended data set we will not know how well it is predicting. This is the case of over-fitting. That is when the model has memorized the dataset and seems to be performing well when in reality it is just copying the dataset it was given."""

train_predict=RNN_model.predict(x_train)
test_predict=RNN_model.predict(x_test)

"""Using the model to predict values from the training set and values from the test set."""

train_predict=normal.inverse_transform(train_predict)
test_predict=normal.inverse_transform(test_predict)

"""Reverting the normalization back into the price format so we can view the predicted prices."""

import math
from sklearn.metrics import mean_squared_error
print(math.sqrt(mean_squared_error(y_train, train_predict)))
print(math.sqrt(mean_squared_error(y_test, test_predict)))

"""Loss metrics

The code below displays the actual prices of BTC in blue and then the predicted values for the training set in orange and the predicted values of the test set in green. It does a decent job predicting data it has seen at least once. The real test will be generating the 30 day forecast.
"""

timesteps = 100
train_predict_plot = np.empty_like(pricedf)
train_predict_plot[:, :] = np.nan
train_predict_plot[timesteps:len(train_predict) + timesteps, :] = train_predict

test_predict_plot = np.empty_like(pricedf)
test_predict_plot[:,:] = np.nan
test_predict_plot[len(train_predict)+(timesteps * 2)+1:len(pricedf)-1, :] = test_predict

plt.plot(normal.inverse_transform(pricedf))
plt.plot(train_predict_plot)
plt.plot(test_predict_plot)
plt.show()

"""### Formatting and reshaping the initial test data to be used to forecast several days.

The last 100 elements of the test data will be used to create a forecast list. Since the model does not have data from the days we are trying to forecast over, the list will need to progressively add and drop values. It will be adding previous predictions to the tail and removing a value from the head. This way the model is continuously using the previous 100 days to predict.
"""

len(test_data)

x_input=test_data[100:].reshape(1,-1)
x_input.shape

forecast_input=list(x_input)
forecast_input=forecast_input[0].tolist()

forecast_input

"""Given a day in the future, the forecast code  looks at the previous 100 days and uses the RNN model to generate a prediction. In the case where we start to run out of days to pull from as the future gets further away, the previous predictions start being added to the list to the model will predict with. """

forecast_output = []
timesteps = 100
i=0
while(i<30):
  if(len(forecast_input)>100):
    x_input=np.array(forecast_input[1:])
    print("{} day input {}".format(i,x_input))
    x_input=x_input.reshape(1,-1)
    x_input = x_input.reshape((1, timesteps, 1))
    yhat = RNN_model.predict(x_input, verbose=0)
    print("{} day output {}".format(i,yhat))
    forecast_input.extend(yhat[0].tolist())
    forecast_input=forecast_input[1:]
    forecast_output.extend(yhat.tolist())
    i=i+1
  else:
    x_input = x_input.reshape((1, timesteps, 1))
    yhat = RNN_model.predict(x_input, verbose=0)
    print(yhat[0])
    forecast_input.extend(yhat[0].tolist())
    print(len(forecast_input))
    forecast_output.extend(yhat.tolist())
    i=i+1
print(forecast_output)

day_data = np.arange(1,101)
day_predicted = np.arange(101,131)

plt.plot(day_data, normal.inverse_transform(pricedf[566:]))
plt.plot(day_predicted, normal.inverse_transform(forecast_output))
plt.show()

"""After the predictions have been made and stored, we use np arange to create a structure containing the real price data and one containing the predicted prices. Using pyplot the two structures are plotted showing the 100 days from end of the test set and the predicted 30 days.

This is the output of the price prediction over the next 30 days. This is the time frame from 11/01/2021 - 12/01/2021.

# Facebook Prophet (15 points)
"""

# Commented out IPython magic to ensure Python compatibility.
# %pip install pystan==2.19.1.1
# %pip install prophet
from prophet import Prophet

m = Prophet()
bitcoin_df.info()

import plotly.express as px

px.area(bitcoin_df,
        x= bitcoin_df.index, y='Close')

bitcoin_df = bitcoin_df.reset_index()
dates = bitcoin_df['Date']

prophet_df = bitcoin_df.rename(columns={'Date': 'ds', 'Close':'y'})
prophet_df.head()

#initialize
model = Prophet()

#fit
model.fit(prophet_df)

#forecast for the next 31 days
future = model.make_future_dataframe(periods=30)

#predict
forecast = model.predict(future)

forecast.tail()

#visualize with Facebook internal tool
figure_1 = model.plot(forecast,
                    xlabel='Date',
                    ylabel='Price')
#NOTE: Black dots = actual data
#Blue line = prediction
#Blue shaded area = upper and lower limit
#The predicted window size is from Nov. 1st to Nov. 30th, 
#seen displayed at the end of the graph

#visualize forecast
figure_2 = model.plot_components(forecast)

"""# Results

The real prices from 11/01/2021 12/01/2021
"""

real_bitcoin_df = yf.download('BTC-USD', start = '2021-11-01', end='2021-12-01', progress=False)
realpricedf = real_bitcoin_df.reset_index()['Close']
import matplotlib.pyplot as plt
plt.plot(realpricedf)

plt.plot(day_predicted, normal.inverse_transform(forecast_output))
plt.show()

"""The model predicts in such a way due to the data we have given it, it has seen the price jump several thousands of dollars in a short amount of time. The crypto market is so volatile. The predictor is confident the price of the coin will continue to go up. In reality, the price of the coin has dropped overtime. This is due to a multitude of factors the predictor does not consider. The coin price does not move only due to the closing price of the previous 100 days. However, this is the only data the model considers leading to the incredibly wrong prediction displayed here.
 
However, it is worth noting that the actual price of bitcoin surpasses the maximum price predicted with the model. After that point it declines down as people cash out on the price spike and a million other factors. Perhaps the predictors recognize the coin is on an up trend but fail to accurately model the velocity at which the code can be in price.

"""

#Table of prediction vs actual price for prophet
#visualize with Facebook internal tool
figure_1 = model.plot(forecast,
                    xlabel='Date',
                    ylabel='Price')
#NOTE: Black dots = actual data
#Blue line = prediction
#Blue shaded area = upper and lower limit

"""The Prophet does not do much better. The algorithm again only relies on closing prices as data. This leads to the wildly wrong prediction we see over the target window. Much like the Keras model, the prophet model is confident the price of bitcoin will continue to rise. This is not surprising as the model has been exposed to the volatile dataset that is the closing prices of Bitcoin. It has seen the price skyrocket in short amounts of time. It can recognize an uptrend but fails to properly model the velocity the coin can have. Due to this, both predictors are confident the price will continue to rise but not at the pace it did in real life.

#Predictor Documentation
##Price Predictor Method 1 TensorFlow
Estimating the probability distribution of a time series future given its past is a very important aspect of modern business models. So many companies today rely on machine learning algorithms to give them an edge in understanding various information related to their business. For instance, a financial forecaster that could predict stock prices given the previous time series at input has a lot of fantastic implications. If the model is reliable it could guide investment firms in their decision-making. It could also help novice investors understand market trends and possible outcomes. These models provide a massive door to the fintech industry.
	To create our model that accomplished this we built a Long Short Term Memory Recurrent Neural Network using Tensorflow. This network takes in financial data on Bitcoin from the YahooFinance library. This library allows us to get the closing prices on bitcoin everyday for as long as we would like. We planned on also including sentiment analysis of tweets for those days as input to the model. However, with restrictions in place by Twitter we could only get at best a sparse matrix of tweets for the same window we had prices for. This left us with an option to construct a faux dataset but we opted against it because in most if not most cases the twitter sentiment would have no correlation to the actual prices.
	After processing the financial data using pandas and numpy we create the RNN model. This model has 3 100 neuron LSTM layers with dropout and they all feed into a single dense neuron. After computing the inverse of the normalization we are left with the closing price for that day. This is the price we are predicting. The network considers the previous 100 days and makes a prediction as to what the next day’s closing price will be. After training and testing the model, we observed that the model was either behaving well or it was overfitting. We moved to attempt to forecast a 30 day window with this model.
	To forecast 30 days into the future the predictor considers it’s previous predictions as input. So, in training, the model would take in the previous 100 days and make a prediction. In this use case, the output prediction for 1 day in the future will be appended to the input for the day 2 prediction. These predictions will be considered for day 3 etc etc until we reach 30 days. The complete list of predictions will be the model’s forecast for the 11/01/2021-12/01/2021 window.
	Overall the predictor works decently well. We hypothesize the model can accurately model the uptrends in the coin but it fails to model the velocity at which the price can move. For instance the actual price for early november actually peaks at around 68,000 dollars. The model predicted the price will rise slowly and steadily over the whole month and end at 65,000 dollars. The actual price did start to increase from 10/31 but it increased with such a velocity the predictor can not ‘keep up’ and gets left in this zone where it starts heavily relying on it’s previous predictions being accurate. This leads the prediction to start to become completely incorrect as time goes on.


##Facebook Prophet
Facebook Prophet is a forecasting procedure library that automates the process for data scientists/analysts. It forecasts time-series data based on an additive model where non-linear trends can be fit into yearly, weekly, and daily graph representations. It also will not just predict the future prices of bitcoin but also provide the upper limit and lower limit of predicted prices allowing us to give us a little more wiggle room and more accurate predictions. Including limits will give us more accurate predictions because if the price drops below the lower limit, then there’s a chance that the price will come up and that means it's good to buy now. Vice versa if the price goes above the upper limit, it will be best for selling bitcoin. If you’d like to add additional variables in Prophet for predict, you can do it by using the add_regressor method. We attempted to add sentiment tweet analysis data as a regressor, but unfortunately it was unable to be done with the method we were using and got unexpected results. So as a last minute resort, we decided to not add it and just display the sentiment data separately. We used the Prophet Python API in Google Colab. 
The Prophet always uses a data frame that has two columns: ds and y. The ds is the date stamp column and y is the close price. Close price was chosen because it is the most accurate price that tells how much bitcoin cost that day. If you look at the fourth code block under the “Facebook Prophet” section, from January 2020 to October 2021, the price of Bitcoin skyrocketed around Feb. 2021 to 57k, dipped back to 30k in July 2021, and then skyrocketed again to 66k in October. The next following code block renames date and close price as ‘ds’ and ‘y’ correspondingly because again, the prophet needs those columns to be named those labels. Afterwards, we just need to initialize Prophet() and fit the model with the dataframe. Then, by using the make_future_dataframe function to predict the next 31 days. 

The eighth code block displays the new dataframe with date, yhat_lower, yhat_upper, trend_lower, trend_upper, additive_terms, additive_terms_lower, additive_terms_upper, weekly, weekly_lower, weekly_upper, and yhat. The dates added are November 1st to November 30th 2021. What’s important is that yhat is the predicted value, and the yhat_lower/yhat_upper is the upper/lower limits. The following code blocks after will help visualize the predicted bitcoin price. For example, the first graph has the blue line as the prediction, the shaded area is the lower and upper limit, and the black dots are the actual price up to October 2021. There other two graphs display the trends with the plot_component function. The first shows the trend of the predicted period from the previous graph and then weekly trends. As you can see, the price of Bitcoin rises in the middle of week and then dips after the weekend, which concludes that the price is generally constant.
"""