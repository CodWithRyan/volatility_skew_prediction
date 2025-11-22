import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt 
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_trading_signals(skew_data, long_threshold=-0.55, short_threshold=0.18, 
                           use_percentile=True, long_pct=30, short_pct=70,
                           target_dte=30): 
    """ Génère des signaux de trading basés sur le volatility skew"""

    df = skew_data.copy()
    if 'Date' not in df.columns:
        raise KeyError(f'❌❌ : {df.columns}')

    if 'days_to_expiry' not in df.columns:
        df['days_to_expiry'] = (pd.to_datetime(df['Expiry']) - pd.to_datetime(df['Date'])).dt.days
    
    df['dte_diff'] = abs(df['days_to_expiry'] - target_dte)
    df = df.sort_values(['Date', 'dte_diff'])
    df = df.groupby('Date').first().reset_index()

    df.index = pd.to_datetime(df['Date'])
    
    # Option 1: Seuils fixes 
    if not use_percentile:
        df['long_signal'] = np.where(df['volatility_skew'] < long_threshold, -1, 0)
        df['short_signal'] = np.where(df['volatility_skew'] > short_threshold, 1, 0)
    else:
        # Option 2: Seuils dynamiques 
        df['skew_20d_low'] = df['volatility_skew'].rolling(20).quantile(long_pct/100)
        df['skew_20d_high'] = df['volatility_skew'].rolling(20).quantile(short_pct/100)
        df['long_signal'] = np.where(df['volatility_skew'] < df['skew_20d_low'], -1, 0)
        df['short_signal'] = np.where(df['volatility_skew'] > df['skew_20d_high'], 1, 0)

  
    df['signal'] = df['long_signal'] + df['short_signal']

    if 'Expiry' in df.columns:
        df.loc[df.index == df['Expiry'], 'signal'] = 0

    df['position'] = df['signal'].replace(0, np.nan).ffill().fillna(0)

    # Stats
    print("\n📊 Statistiques des signaux:")
    print(f"  Signaux Long  : {(df['signal'] == 1).sum()}")
    print(f"  Signaux Short : {(df['signal'] == -1).sum()}")
    print(f"  Sans position : {(df['signal'] == 0).sum()}")
    print(f"  DTE moyen utilisé : {df['days_to_expiry'].mean():.1f} jours")

    return df


def plot_signals_and_skew(df, figsize=(15, 10)):
    """
    Visualise les signaux et le skew
    """
    output_dir = Path('./outputs')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)
    
    # Graphique 1: Volatility Skew avec zones
    ax1.plot(df.index, df['volatility_skew'], label='Volatility Skew', color='blue', linewidth=1.5)
    ax1.axhline(y=-0.05, color='green', linestyle='--', alpha=0.5, label='Long Threshold')
    ax1.axhline(y=0.10, color='red', linestyle='--', alpha=0.5, label='Short Threshold')
    ax1.fill_between(df.index, -1, -0.4, alpha=0.1, color='green', label='Zone Long')
    ax1.fill_between(df.index, 0.3, 1, alpha=0.1, color='red', label='Zone Short')
    ax1.set_ylabel('Volatility Skew')
    ax1.set_title('Volatility Skew et Zones de Trading')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Graphique 2: Signaux
    colors = {1: 'red', 0: 'gray', -1: 'green'}
    positions = df['signal'].map(colors)
    ax2.scatter(df.index, df['signal'], c=positions, alpha=0.6, s=10)
    ax2.plot(df.index, df['position'], label='Position', color='black', linewidth=1)
    ax2.set_ylabel('Signal/Position')
    ax2.set_xlabel('Date')
    ax2.set_title('Signaux de Trading')
    ax2.set_ylim(-1.5, 1.5)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    fig_path = output_dir / 'signal_skew.png'
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.show()
    
    return fig