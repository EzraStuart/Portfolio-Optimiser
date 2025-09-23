import streamlit as st
from optimiserr import PortfolioOptimiser
import pandas as pd
import yfinance  as yf


st.set_page_config(page_title='Portfolio Optimiser Dashboard', layout='wide')
st.title('Interactive Portfolio Optimiser')

# Option 1: predefined universes:
universes = {
    'Custom':[],
    'FAANG': ['AAPL', 'AMZN', 'GOOGL', 'META', 'NFLX'],
    'BANKS': ['JPM', 'GS', 'MS', 'BAC']
}

st.sidebar.header('Portfolio Settings')
universe_choice = st.sidebar.selectbox('Choose a stock universe:', list(universes.keys()))

if universe_choice != 'Custom':

    my_portfolio = st.sidebar.multiselect(
        'Select tickers:',
        options = universes[universe_choice],
        default = universes[universe_choice]
    )
else:
# Ticker selection:
    ticker_input = st.text_input(
        'Enter tickers(comma-seperated):', value = 'AAPL, MSFT, NVDA'
)
    my_portfolio = [t.strip().upper() for t in ticker_input.split(',') if t.strip()]

#Date selection
start_date = st.sidebar.date_input('Start date', pd.to_datetime('2020-01-01'))
end_date = st.sidebar.date_input('End date', pd.to_datetime('today'))
num_simulations = st.slider('Number of Simulations', min_value=1000, max_value=100000)
weights = st.slider('Weight Constraints (%)', value= [0,100])
min_weight = weights[0] /100
max_weight = weights[1]/100
alpha = st.slider('Alpha (%)', 0, 10)
alpha = alpha / 100
risk_free_rate = st.slider('Risk Free Rate (%)', 0, 10)
risk_free_rate = risk_free_rate / 100


#Simulation button
if st.button('Run Simulation'):
    if my_portfolio:
        st.write(f"fetching data for: {','.join(my_portfolio)}")
        # Data collection from yfinance
        try:
            data = yf.download(my_portfolio, start=start_date, end=end_date)['Close']
        #Drop Columns with all missing 
            available_tickers = [t for t in my_portfolio if t in data.columns and data[t].notna().any()]

            if not available_tickers:
                st.error('No valid tickers found. Please check your inputs')
            elif len(available_tickers) < len(my_portfolio):
                missing = set(my_portfolio) - set(available_tickers)
                st.warning(f'The following tickers had no data and were removed:{','.join(missing)}')
                my_portfolio = available_tickers
                data = data[my_portfolio]

            with st.spinner('Running Monte Carlo Simulations...'):
        # Run simulation
                optimiser = PortfolioOptimiser(data, my_portfolio, risk_free_rate=risk_free_rate)
                results = optimiser.portfoliosim(500, alpha = alpha, max_weight=max_weight, min_weight=min_weight)
        
        #Optimised portfolios
                max_sharpe, min_vol, min_cvar = optimiser.Optimise(results)
                optimal_ports = [max_sharpe, min_vol, min_cvar]
            st.session_state['results'] = results
            st.session_state['optimal_ports'] = optimal_ports
            st.session_state['optimiser'] = optimiser

            st.success('Simulation Complete!')

        except ValueError as e:
                    # Check if it's the "argmax of empty sequence" error
                if "argmax of an empty sequence" in str(e):
                        st.error("Error: Please enter valid weight constraints.")
                else:
                        st.error(f"Simulation error: {e}")

    else:
        st.warning('Please select at least one ticker')
    
