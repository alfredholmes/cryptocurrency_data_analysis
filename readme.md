# Cryptocurrency Market Analysis
### Binance and Coinbase Individual Trade Data preliminary analysis and modeling

This repository is a collection of python scripts for and documentation on a research project preforming statistical analysis on Cryptocurrency Markets.

The working report can be found at [Documentation/mircomoedlling.pdf](https://github.com/alfredholmes/cryptocurrency_data_analysis/blob/master/Documentation/micromodelling.pdf)


### Current Progress

#### Data access and storage

+ Scripts to manage downloading individual trade data from Binance and Coinbase APIs (found in [/Download/](https://github.com/alfredholmes/cryptocurrency_data_analysis/tree/master/Download))
+ Scripts to record web sockets (previous versions work, the current implementation in is yet to be implemented using asynchronous style python)
+ [/lib/](https://github.com/alfredholmes/cryptocurrency_data_analysis/tree/master/lib) Simple Library for order management, stores trades in a SQLite database and can be used to get orders (collections of trades that we can assume to be part of the same order).

#### Statistical Analysis

+ See [/PreliminaryAnalysis/](https://github.com/alfredholmes/cryptocurrency_data_analysis/tree/master/PreliminaryAnalysis) For quick scripts not ordered very well performing basic analysis
+ Analysis of order rates - seem to follow a Weibull distribution, indicating a sort of short term reaction
+ BTC models - modelling the order states as Markovian (see report) and changes to this

#### Current Work (Todo)

+ Testing statistical significance of markov model (given parameters are the predicted price distributions seen?)
+ Application of Recurrent Neural Networks to calculate the statistical distribution of parameters given previous market data. (Use neural network to predict parameters of a multivariate distribution rather than values themselves). This will be achieved by altering the error function to be a measure of the predictive accuracy. 
+ Developing statistical models that have less of a dependence on the predicted parameters as current markov model just gives a normal distribution with the expectation and variance given by (functions of) the parameters predicted through linear regression. The models should be more dependent on the initial market state.