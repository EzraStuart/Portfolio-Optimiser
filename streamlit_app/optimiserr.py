import pandas as pd
import os
import numpy as np



class PortfolioOptimiser:
    
    #Define Objeccts in class
    def __init__(self, input, port, risk_free_rate):
        self.input = input
        self.port = [stock.upper() for stock in port]
        self.risk_free_rate = risk_free_rate
        self.data = None
        self.returns = None
        self.mean_returns = None
        self.covmatrix = None

    def load_file(self):
        self.input = self.input[self.input.columns].apply(pd.to_numeric, errors='coerce')
        # Check for existence
        
        port_data = []
        # Filter the dataframe for our portfoloio
        for stock in self.port:
            matching_cols = [col for col in self.input.columns if col.upper() == stock.upper()]
            if matching_cols:
                port_data.append(matching_cols[0])
            else:
                print(f"Stock {stock} not found")

        self.data = self.input[port_data]
        print(f'Loading Portfolio analysis for stocks: {",".join(self.data.columns)}')
        

        # calculatate daily reutrns
        self.returns = self.data.pct_change().dropna() 
        #annual  
        self.mean_returns = self.returns.mean() * 252
        self.covmatrix = self.returns.cov() *252

        print(f"Data loaded successfully: {len(self.returns)} trading days")
        print(f"Date range: {self.returns.index[0].date()} to {self.returns.index[-1].date()}")


    # Now we want to gather portfolio metrics from data
    def single_portfolio_metrics(self, weights, alpha):
        #Calculate annualised return, volatility, sharpe ratio
        port_return = np.sum(weights * self.mean_returns)
        port_volatility = np.sqrt((np.dot(weights.T, np.dot(self.covmatrix, weights))))
        port_sharpe = (port_return - self.risk_free_rate) / port_volatility 

        #calculate CVaR
        #Portfolio Daily ruturns
        port_daily_ret = np.dot(self.returns, weights)

        # Sort
        sorted_ret = np.sort(port_daily_ret)
        #Var at alpha
        index = int(alpha * len(sorted_ret))
        port_var = sorted_ret[index]

        # CVaR
        port_cvar = sorted_ret[:index].mean()

        return port_return, port_volatility, port_sharpe, port_var, port_cvar
    
    # Run Simulations
    def portfoliosim(self, simulations, alpha, min_weight, max_weight):
        print(f'Simulating {simulations} Portfolios')
        if self.mean_returns is None:
            self.load_file()
        
        n_assets = len(self.mean_returns)

        results = {
            'returns':  [],
            'volatility': [],
            'sharpe': [],
            'var': [],
            'cvar': [],
            'weights': []
        }

        # Set seed for reproducible results
        np.random.seed(72)

        #Generate random weights:
        weights = np.random.rand(simulations*5, n_assets)
        weights /= weights.sum(axis = 1)[:, np.newaxis]

        #Constraints
        valid_mask = np.all((weights>= min_weight) & (weights <= max_weight), axis = 1)
        valid_weights = weights[valid_mask][:simulations]

        #portfolio returns
        port_returns = valid_weights @ self.mean_returns.values

        #annualised volatility
        cov = self.covmatrix.values
        port_vol = np.sqrt(np.einsum('ij,jk,ik->i',valid_weights,cov,valid_weights))

        #sharpe
        port_sharpe = (port_returns - self.risk_free_rate)/ port_vol

        #Daily returns for cvar /var
        daily_returns = self.returns.values @ valid_weights.T
        sorted_returns = np.sort(daily_returns, axis = 0)
        idx = max(1,int(alpha * sorted_returns.shape[0]))
        port_var = sorted_returns[idx, :]
        port_cvar = sorted_returns[:idx, :].mean(axis= 0)

        results["returns"] = port_returns
        results["volatility"] = port_vol
        results["sharpe"] = port_sharpe
        results["var"] = port_var
        results["cvar"] = port_cvar
        results["weights"] = valid_weights

        return results
    
    def Optimise(self, results):
        returns = np.array(results['returns'])
        volatility = np.array(results['volatility'])
        sharpe = np.array(results['sharpe'])
        var = np.array(results['var'])
        cvar = np.array(results['cvar'])
        weights = np.array(results['weights'])

        #find optimal sharpe

        optimal_sharpe = np.argmax(sharpe)
        optimal_sharpe_portfolio = {
            'returns': returns[optimal_sharpe],
            'volatility': volatility[optimal_sharpe],
            'sharpe': sharpe[optimal_sharpe],
            'var': var[optimal_sharpe],
            'cvar': cvar[optimal_sharpe],
            'weights': weights[optimal_sharpe] 
        }
        # find minimal volatility
        min_vol = np.argmin(volatility)
        min_vol_portfolio = {
            'returns': returns[min_vol],
            'volatility': volatility[min_vol],
            'sharpe': sharpe[min_vol],
            'var': var[min_vol],
            'cvar': cvar[min_vol],
            'weights': weights[min_vol] 
        }
        #Find minimum cvar portfolio
        min_cvar = np.argmax(cvar)
        min_cvar_portfolio = {
            'returns': returns[min_cvar],
            'volatility': volatility[min_cvar],
            'sharpe': sharpe[min_cvar],
            'var': var[min_cvar],
            'cvar': cvar[min_cvar],
            'weights': weights[min_cvar] 
        } 

        return optimal_sharpe_portfolio, min_vol_portfolio, min_cvar_portfolio