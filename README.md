# Portfolio-Optimiser

An interactive portfolio optimisation tool built in Python using Streamlit, Plotly and yfinance.

Simulates thousands of random portfolios via Monte Carlo methods, computes financial risk metrics, and identifies optimal allocations under different criteria

## Features
- Interactive Simulation:
  - Generates 1000 - 100,000 portfolios randomly
  - User inputted weight constraints
  - User inputted alpha and risk free rate
- Risk & Return Metrics
  - Annualised Return & Volatility
  - Sharpe Ratio
  - Value at Risk (VaR) & Conditional VaR (CVaR)
- Optimal Portfolios
  - Maximum Sharpe Ratio
  - Minimum Volatility
  - Minimum CVaR
- Interactive Visualisations
  - Effecient Frontier Scatter Plot with colour coded Sharpe ratios
  - Asset Allocation shown as pie charts

## Screenshots
<img width="937" height="476" alt="Dashboard" src="https://github.com/user-attachments/assets/114f9c8c-83cc-4794-8ce4-9b538e36e816" />

<img width="960" height="474" alt="EfficientFrontier" src="https://github.com/user-attachments/assets/7d32e7de-aa58-420e-ab57-6a5ea4925a90" />

<img width="856" height="314" alt="Portvis1" src="https://github.com/user-attachments/assets/b890cfc1-4df0-4ae8-9221-defb627640c4" />

<img width="862" height="472" alt="portvis2" src="https://github.com/user-attachments/assets/946aeb93-d542-42a3-8704-1983d86b06f6" />


## Requirements
- Python
- Streamlit - Interactive Dashboard
- Plotly Express - Data Visulaisations
- yfinance - Market Data API
- Pandas  / NumPy - Data Handling

  ## Use

  streamlit run Dashboard.py
