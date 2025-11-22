import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_ivs(futures_data, options_data):
    """
    Calcule otm_call_iv, otm_put_iv et atm_iv en mergant avec options_data
    """
    result = futures_data.copy()

    result = result.reset_index()
    options_data = options_data.reset_index(drop=True)

    column_mapping = {
        'date': 'Date',
        'expiry': 'Expiry',
        'strike_price': 'strike_price',
        'option_type': 'option_type',
        'last': 'last'
    }
    
    for old_name, new_name in column_mapping.items():
        if old_name in options_data.columns:
            options_data[new_name] = options_data[old_name]
    
 
    if 'option_type' in options_data.columns:
        
        options_data['option_type'] = options_data['option_type'].str.upper().map({
            'CE': 'call',
            'PE': 'put'
        })
    
    date_col = next((col for col in result.columns if 'date' in col.lower()), 'Date')
    expiry_col = next((col for col in result.columns if 'expiry' in col.lower()), 'Expiry')
    
    print(f"🔍 Colonnes détectées : date={date_col}, expiry={expiry_col}")
    
    result['atm_iv'] = np.nan
    result['otm_call_iv'] = np.nan
    result['otm_put_iv'] = np.nan
    
    for idx, row in result.iterrows():
        date = row[date_col]
        expiry = row[expiry_col]
        
        mask = (options_data['date'] == date) & (options_data['expiry'] == expiry)
        day_options = options_data[mask]
        
        if len(day_options) == 0:
            continue
        
        # --- ATM IV (moyenne Call + Put) ---
        atm_strike = row['atm_strike_price']
        atm_calls = day_options[(day_options['strike_price'] == atm_strike) & 
                                (day_options['option_type'] == 'call')]
        atm_puts = day_options[(day_options['strike_price'] == atm_strike) & 
                               (day_options['option_type'] == 'put')]
        
        if not atm_calls.empty and not atm_puts.empty:
            result.at[idx, 'atm_iv'] = (atm_calls['last'].iloc[0] + atm_puts['last'].iloc[0]) / 2
        
        # --- OTM Call IV ---
        otm_call_strike = row['otm_call_strike_price']
        otm_calls = day_options[(day_options['strike_price'] == otm_call_strike) & 
                                (day_options['option_type'] == 'call')]
        
        if not otm_calls.empty:
            result.at[idx, 'otm_call_iv'] = otm_calls['last'].iloc[0]
        
        # --- OTM Put IV ---
        otm_put_strike = row['otm_put_strike_price']
        otm_puts = day_options[(day_options['strike_price'] == otm_put_strike) & 
                               (day_options['option_type'] == 'put')]
        
        if not otm_puts.empty:
            result.at[idx, 'otm_put_iv'] = otm_puts['last'].iloc[0]
    
    # Calculer la volatility skew
    result['volatility_skew'] = (result['otm_put_iv'] - result['otm_call_iv']) / result['atm_iv']
    
    print(f"\n✅ IV calculées : {result['atm_iv'].notna().sum()}/{len(result)} lignes")
    print(f"\n📊 Aperçu :")
    print(result[[date_col, expiry_col, 'atm_iv', 'otm_call_iv', 'otm_put_iv', 'volatility_skew']].head(10))
    
    return result


def save_analysis_results(clean_data):
    """save data and visualisation"""
    try:
        output_dir = Path('./outputs')
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f'📁 repertoires créés')

        csv_path = output_dir / 'skew_data.csv'
        clean_data.to_csv(csv_path, index=False)

        logger.info(f"✅ Données sauvegardées : {csv_path}")

        fig, axes = plt.subplots(2 ,2, figsize=(14, 10))

        # Skew Volatility distribution
        axes[0, 0].hist(clean_data['volatility_skew'].dropna(),
                        bins=50, edgecolor='black', color='purple')
        axes[0, 0].set_title('Volatility Skew Distribution')
        axes[0, 0].set_xlabel('Skew')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].grid(True, alpha=0.3)

        # Temporal Evolutioon
        daily_skew = clean_data.groupby('Date')['volatility_skew'].mean()
        daily_skew.plot(ax=axes[0, 1], color='red', linewidth=2)
        axes[0, 1].set_title('Average daily skew volatility')
        axes[0, 1].set_ylabel('Average skew')
        axes[0, 1].grid(True, alpha=0.3)

        # ATM IV vs Skew
        axes[1, 0].scatter(clean_data['atm_iv'], 
                          clean_data['volatility_skew'], 
                          alpha=0.5, s=10, color='coral')
        axes[1, 0].set_xlabel('ATM IV')
        axes[1, 0].set_ylabel('Volatility Skew')
        axes[1, 0].set_title('ATM IV vs Volatility Skew')
        axes[1, 0].grid(True, alpha=0.3)

        # DTE vs Skew
        axes[1, 1].scatter(clean_data['days_to_expiry'], 
                          clean_data['volatility_skew'], 
                          alpha=0.5, s=10, color='green')
        axes[1, 1].set_xlabel('Days to Expiry')
        axes[1, 1].set_ylabel('Volatility Skew')
        axes[1, 1].set_title('DTE vs Volatility Skew')
        axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()

        fig_path = output_dir / 'iv_skew_analysis.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.show()

        logger.info(f"✅ Visualisations sauvegardées : {fig_path}")

        # Statistics
        print("\n" + "="*60)
        print("📊 ANALYSIS REPORT")
        print("="*60)
        print(f"Données nettoyées : {len(clean_data)} lignes")
        print(f"Période : {clean_data['Date'].min()} à {clean_data['Date'].max()}")
        print(f"average Skew : {clean_data['volatility_skew'].mean():.4f}")
        print(f"median Skew : {clean_data['volatility_skew'].median():.4f}")
        print(f"Skew std : {clean_data['volatility_skew'].std():.4f}")
        print("="*60)
        print("If the value of volatility skew is positive, it implies that the IV of OTM put is greater than the IV of OTM call and the price of the underlying is expected to fall.")
        print("If the value of volatility skew is negative, it implies that the IV of OTM call is greater than the IV of OTM put and the price of the underlying is expected to rise.")

        return True
    except Exception as e:
        logger.error(f'❌❌❌ Erreur : {e}')
        return False
