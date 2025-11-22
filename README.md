# Volatility Skew Trading Strategy

## 📊 Overview
A quantitative trading strategy that predicts future market direction using options volatility skew. The strategy analyzes the difference between OTM put and call implied volatilities to generate trading signals.

## 🎯 Overview

This project implements a systematic trading strategy based on implied volatility skew patterns in S&P 500 options. The strategy identifies mispricing opportunities by analyzing the relationship between put and call option volatilities across different strike prices.

**Key Result:** Sharpe Ratio of **3.47** with minimal drawdown (-1.68%)

## 📁 Project Structure

volatility_skew_prediction/
├── src/
│   └── volatility_skew_prediction/
│       ├── data_loader.py          # Data ingestion & preprocessing
│       ├── iv_calculator.py        # Implied volatility calculations
│       ├── skew_calculator.py      # Skew metrics computation
│       ├── strategy.py             # Trading signal generation
│       └── perf_metrics.py         # Performance analytics
├── notebooks/
│   ├── 01_data_collection.ipynb    # Data exploration
│   └── outputs/                     # Generated charts & results
├── data/
│   └── skew_data.csv               # Historical options data
└── requirements.txt


## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/CodWithRyan/volatility_skew_prediction.git
cd volatility_skew_prediction

# Create virtual environment
python -m venv .vsp_env
source .vsp_env/bin/activate  

# Install dependencies
pip install -r requirements.txt
```
## 🔍 Strategy Logic
The volatility skew is calculated as:
```
Volatility Skew = (OTM Put IV - OTM Call IV) / ATM IV
```

📈 Performance Metrics

Metric              Value

Strategy Return     2.70%

Market Return       11.29%

Sharpe Ratio        3.47

Max Drawdown        -1.68%

Number of Trades        15

Transaction Costs       0.032% per trade


## 🔑 Key Features

- Low Frequency: ~15 trades over test period
- Risk-Adjusted Excellence: Sharpe > 3 indicates consistent risk-adjusted returns
- Minimal Drawdown: -1.68% maximum loss
- Transaction Cost Aware: Realistic slippage & commission modeling

## 📊 Strategy Logic

- Calculate Implied Volatility using Black-Scholes model
- Compute Skew Metrics (25-delta put/call spread)
- Generate Signals when skew exceeds statistical thresholds
- Execute Trades with proper risk management
- Apply Realistic Costs (commission + slippage)

## ⚙️ Configuration
Key parameters in strategy.py:

SKEW_THRESHOLD = 2.0      # Standard deviations for signal
DTE_MIN = 7               # Minimum days to expiration
DTE_MAX = 30              # Maximum days to expiration
COMMISSION =  $ 1.50        # Per contract
SLIPPAGE =  $ 0.10          # Bid-ask spread assumption

## 📝 Requirements

Python 3.8+
pandas, numpy, scipy
matplotlib, seaborn
jupyter (for notebooks)

See requirements.txt for complete list

## ⚠️ Disclaimer
This project is for educational and research purposes only. Past performance does not guarantee future results. Options trading involves substantial risk of loss. Always conduct thorough due diligence and consider consulting a financial advisor before implementing any trading strategy.


## 👤 Author

**Bonny Ryan FN**

## 🙏 Acknowledgments

Inspired by options trading research and volatility smile analysis


