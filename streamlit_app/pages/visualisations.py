import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

st.set_page_config(page_title='Portfolio Visualisations', layout='wide')

st.title('Portfolio Visualisations')

if 'results' not in st.session_state:
    st.info('Run a simulation from the main page to see results here.')
else:
    results = st.session_state['results']
    optimal_ports = st.session_state['optimal_ports']
    optimiser = st.session_state['optimiser']

    # Convert results into DataFrame
    df = pd.DataFrame({
        'Returns': results['returns'],
        'Volatility': results['volatility'],
        'Sharpe': results['sharpe']
    })
    df['Returns'] *= 100
    df['Volatility'] *= 100

    # Tabs 
    tab1, tab2, tab3 = st.tabs(["Efficient Frontier", "Optimal Portfolios", "Download Results"])

    #  Efficient Frontier Tab 
    with tab1:
        st.subheader("Efficient Frontier")

        # benchmark S&P500
        sp500 = yf.download("^GSPC", start=optimiser.returns.index[0], end=optimiser.returns.index[-1])['Close']
        sp500_ret = sp500.pct_change().dropna()
        sp500_mean = sp500_ret.mean() * 252
        sp500_vol = sp500_ret.std() * (252**0.5)

        fig = px.scatter(
            df, x='Volatility', y='Returns', color='Sharpe', size='Sharpe',
            color_continuous_scale='Viridis',
            labels={'Volatility': 'Volatility (%)', 'Returns': 'Returns (%)', 'Sharpe': 'Sharpe Ratio'},
            hover_data={'Volatility': ':.2f', 'Returns': ':.2f', 'Sharpe': ':.2f'}
        )

        # Highlight optimal portfolios
        for port, label, color in zip(
            optimal_ports, ['Max Sharpe', 'Min Vol', 'Min CVaR'], ['red','blue','green']
        ):
            fig.add_scatter(
                x=[port['volatility']*100],
                y=[port['returns']*100],
                mode='markers',
                marker=dict(size=15, color=color, symbol='star'),
                name=label
            )

        # Add benchmark
        fig.add_scatter(
            x=[sp500_vol*100], y=[sp500_mean*100],
            mode='markers',
            marker=dict(size=15, color='orange', symbol='diamond'),
            name='S&P 500'
        )

        fig.update_layout(
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- Optimal Portfolios Tab ---
    with tab2:
        for port, label in zip(optimal_ports, ['Max Sharpe', 'Min Vol', 'Min CVaR']):
            st.subheader(f"{label} Portfolio")

            col1, col2 = st.columns(2)

            # Metrics table
            with col1:
                st.markdown("**Metrics**")
                st.table(pd.DataFrame({
                    "Metric": ["Expected Return", "Volatility", "Sharpe Ratio", "VaR", "CVaR"],
                    "Value": [
                        f"{port['returns']:.2%}",
                        f"{port['volatility']:.2%}",
                        f"{port['sharpe']:.3f}",
                        f"{port['var']:.2%}",
                        f"{port['cvar']:.2%}"
                    ]
                }))

            # Allocation pie chart
            with col2:
                st.markdown("**Asset Allocation**")
                alloc_df = pd.DataFrame({
                    "Asset": optimiser.data.columns,
                    "Weight": port['weights']
                })
                fig_alloc = px.pie(alloc_df, values='Weight', names='Asset',
                                title=f"{label} Portfolio Allocation",
                                hole=0.3)
                st.plotly_chart(fig_alloc, use_container_width=True)

    # --- Download Tab ---
    with tab3:
        st.subheader("Download Simulation Results")
        results_df = pd.DataFrame({
            "Returns": results["returns"],
            "Volatility": results["volatility"],
            "Sharpe": results["sharpe"],
            "VaR": results["var"],
            "CVaR": results["cvar"]
        })

# Expand weights into columns named after assets
        weights_df = pd.DataFrame(results["weights"], columns=optimiser.data.columns)

# Concatenate
        results_df = pd.concat([results_df, weights_df], axis=1)
        st.download_button(
            label="Download Results as CSV",
            data=results_df.to_csv(index=False).encode('utf-8'),
            file_name='portfolio_simulation_results.csv',
            mime='text/csv'
        )
