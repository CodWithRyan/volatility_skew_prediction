# Volatility Skew Trading Strategy

## 📊 Overview
A quantitative trading strategy that predicts future market direction using options volatility skew. The strategy analyzes the difference between OTM put and call implied volatilities to generate trading signals.

## 🎯 Project Objectives
- Calculate ATM and OTM strike prices from futures data
- Compute implied volatility for various strike prices
- Calculate volatility skew metric
- Develop and backtest a directional trading strategy
- Analyze performance with risk metrics (Sharpe ratio, max drawdown)

## 🔍 Strategy Logic
The volatility skew is calculated as:
```
Volatility Skew = (OTM Put IV - OTM Call IV) / ATM IV
```

**Trading Signals:**
- **Long Signal**: When skew < -0.05 (calls more expensive than puts → bullish sentiment)
- **Short Signal**: When skew > 0.1 (puts more expensive than calls → bearish sentiment)

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip

### Setup
```bash
# Clone the repository
git clone https://github.com/codwithryan/volatility-skew-prediction.git
cd volatility-skew-prediction

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 📊 Data Sources

This project uses options and futures data from the following free sources:

### Recommended Free Data Sources:
1. **Yahoo Finance** (via yfinance)
   - SPY, QQQ options (US markets)
   - Limited historical depth but reliable

2. **CBOE DataShop**
   - Free delayed data
   - SPX options data
   - URL: http://www.cboe.com/delayedquote/quote-table

3. **Alpha Vantage**
   - Free API (500 calls/day)
   - Options data for US stocks
   - URL: https://www.alphavantage.co/

4. **Polygon.io**
   - Free tier available
   - Options and futures data
   - URL: https://polygon.io/

5. **Interactive Brokers (IBKR)**
   - Free paper trading account
   - Real-time data access via API
   - Requires ib_insync library

See `data/DATA_SOURCES.md` for detailed instructions on data collection.

## 🚀 Usage

### Quick Start
```python
from src.data_loader import load_options_data
from src.strategy import VolatilitySkewStrategy

# Load data
options_data, futures_data = load_options_data('SPY', '2023-01-01', '2023-12-31')

# Initialize strategy
strategy = VolatilitySkewStrategy(
    strike_difference=5,
    long_threshold=-0.05,
    short_threshold=0.1
)



## 📈 Results

### Backtest Performance (Example)
- **Period**: 2023-01-01 to 2023-12-31
- **Sharpe Ratio**: 1.42
- **Max Drawdown**: -8.5%
- **Total Return**: 23.4%
- **Win Rate**: 58%

*Note: Results will vary based on the underlying asset and time period.*

## 🛠️ Project Structure
```
├── notebooks/          # Jupyter notebooks for analysis
├── src/               # Source code modules
├── data/              # Data storage (raw and processed)
├── results/           # Output figures and metrics
├── tests/             # Unit tests
└── config/            # Configuration files
```

## 📚 Key Modules

- **data_loader.py**: Functions to fetch and clean options/futures data
- **iv_calculator.py**: Implied volatility calculations using Black-Scholes
- **skew_calculator.py**: Volatility skew computation
- **strategy.py**: Trading strategy logic and signal generation
- **performance_metrics.py**: Sharpe ratio, max drawdown, etc.

## 🔬 Methodology

1. **Data Collection**: Fetch options and futures data
2. **Strike Selection**: Calculate ATM, OTM call, and OTM put strikes
3. **IV Calculation**: Use Black-Scholes model to compute implied volatility
4. **Skew Computation**: Calculate normalized volatility skew
5. **Signal Generation**: Generate long/short signals based on thresholds
6. **Backtesting**: Simulate strategy performance with realistic assumptions
7. **Performance Analysis**: Calculate risk-adjusted metrics


## 📊 Performance Metrics

The strategy evaluates:
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Worst peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profits / Gross losses
- **Sortino Ratio**: Downside risk-adjusted returns

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request


## 👤 Author

**Bonny Ryan FN**

## 🙏 Acknowledgments

- Black-Scholes model implementation using `mibian` library
- Inspired by options trading research and volatility smile analysis

## ⚠️ Disclaimer

This project is for educational purposes only. It does not constitute financial advice. Trading options involves significant risk and may not be suitable for all investors. Always do your own research and consult with a financial advisor before making investment decisions.

## 📖 References

- [CBOE Volatility Index Methodology](http://www.cboe.com/vix)
- [Black-Scholes Model](https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model)
