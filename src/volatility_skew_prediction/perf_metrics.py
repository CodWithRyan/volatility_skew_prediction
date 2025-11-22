import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


output_dir = Path('./outputs')

def analyse_strat_perf(df, apply_costs=False):
    """Calculation of Strategy return, Sharpe Ratio & Maximum Drawdown """
    dt_f = df.copy()
    
    dt_f = dt_f.sort_index()


    dt_f['market_returns'] = dt_f['futures_close'].pct_change()
    dt_f['strategy_returns'] = dt_f['market_returns'] * dt_f['signal']

    if apply_costs:
        COMMISSION = 1.50
        SLIPPAGE = 0.10
        CAPITAL_PER_TRADE = 10000
        COST_PER_TRADE = (COMMISSION + SLIPPAGE) * 2
        COST_PERCENTAGE = COST_PER_TRADE / CAPITAL_PER_TRADE
        
        dt_f['trade_costs'] = 0.0
        dt_f.loc[dt_f['signal'] != 0, 'trade_costs'] = COST_PERCENTAGE
        dt_f['strategy_returns'] = dt_f['strategy_returns'] - dt_f['trade_costs']
        
        logger.info(f"💰 Coûts appliqués : {COST_PERCENTAGE*100:.3f}% par trade")

    dt_f['market_returns'] = dt_f['market_returns'].replace([np.inf, -np.inf], np.nan).fillna(0)
    dt_f['strategy_returns'] = dt_f['strategy_returns'].replace([np.inf, -np.inf], np.nan).fillna(0)

    dt_f['compound_market_returns'] = (dt_f['market_returns'] + 1).cumprod()
    dt_f['compound_strategy_returns'] = (dt_f['strategy_returns'] + 1).cumprod()

    valid_returns = dt_f['strategy_returns'][dt_f['strategy_returns'] != 0]
    # Sharpe Ratio
    if len(valid_returns) > 1 and valid_returns.std() > 0:
        sharpe_ratio = valid_returns.mean() / valid_returns.std() * np.sqrt(252)
    else:
        sharpe_ratio = 0
        logger.warning("⚠️ Sharpe Ratio = 0 : pas assez de returns valides")
    
    logger.info(f'Sharpe Ratio: {sharpe_ratio:.4f}')
    
    # Maximum Drawdown (avec protection)
    if dt_f['compound_strategy_returns'].max() > 0:
        dt_f['peak'] = dt_f['compound_strategy_returns'].cummax()
        dt_f['Drawdown'] = ((dt_f['compound_strategy_returns'] - dt_f['peak']) / dt_f['peak']) * 100
        max_drawdown = dt_f['Drawdown'].min()
    else:
        dt_f['Drawdown'] = 0
        max_drawdown = 0
        logger.warning("⚠️ Max Drawdown = 0 : pas de performance positive")
    
    logger.info(f'Maximum Drawdown: {max_drawdown:.2f}%')

    # max_drawdown
    dt_f['peak'] = dt_f['compound_strategy_returns'].cummax()
    dt_f['Drawdown'] = ((dt_f['compound_strategy_returns'] - dt_f['peak']) / dt_f['peak']) * 100
    max_drawdown = (dt_f['Drawdown'].min())

    # Métriques additionnelles
    total_return = (dt_f['compound_strategy_returns'].iloc[-1] - 1) * 100
    market_return = (dt_f['compound_market_returns'].iloc[-1] - 1) * 100
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS DE PERFORMANCE")
    print("=" * 60)
    print(f"📈 Strategy Total Return : {total_return:>10.2f}%")
    print(f"📊 Market Total Return   : {market_return:>10.2f}%")
    print(f"🎯 Alpha                 : {(total_return - market_return):>10.2f}%")
    print(f"⚡ Sharpe Ratio          : {sharpe_ratio:>10.4f}")
    print(f"📉 Max Drawdown          : {max_drawdown:>10.2f}%")
    print(f"📊 Nombre de trades      : {len(valid_returns):>10.0f}")
    print("=" * 60)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

    # Compound Returns
    ax1.plot(dt_f.index, dt_f['compound_strategy_returns'], label='Strategy', color='darkgreen', linewidth=2)
    ax1.set_title('Compound Strategy Returns')
    ax1.set_ylabel('Compound Returns')
    ax1.legend(loc='best')
    ax1.grid(alpha=0.3)

    # Maximum drawdown
    ax2.fill_between(dt_f.index, dt_f['Drawdown'], 0, alpha=0.5, color='darkred')
    ax2.plot(dt_f.index, dt_f['Drawdown'], color='darkred', linewidth=1.5)
    ax2.set_title('Drawdowns')
    ax2.set_ylabel('drawdowns (%)')
    ax2.grid(alpha=0.3)
    
    
    plt.tight_layout()
    fig_path = output_dir / 'strategy_performance.png'
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.show()

    return dt_f




