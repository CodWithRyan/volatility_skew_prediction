import pandas as pd
import os
from pathlib import Path
import logging


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
def download_data():
    """Download SPX options data from OptionsDX"""

    try:
        base_path = Path('/Users/nkeniryanbonny/Desktop/projet_fama_french/spx_eod_2023q4-ai4uc9')
        if not base_path.exists():
            logger.error(f"{base_path} doesn't exist")
            base_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"directory created : {base_path}")
    
        dir_list = os.listdir(base_path)
        spx_options_data = pd.DataFrame()

        for file_name in dir_list:
            if not file_name.endswith(('.csv', '.txt', '.parquet')):
                continue
                #file_path = os.path.join(base_path, file_name)
            file_path = base_path / file_name
            monthly_data = pd.read_csv(file_path, sep=',', encoding='utf-8')
            spx_options_data = pd.concat([spx_options_data, monthly_data], ignore_index=True)

        return spx_options_data
        
    except Exception as e:
        logger.error(f"error : {e}")

def create_futures_data(spx_options_data, min_dte=10, max_dte=180):
    """
    Crée futures_data avec TOUTES les expirations disponibles
    entre min_dte et max_dte pour chaque date
    """
    
    clean_data = spx_options_data[
        (spx_options_data[' [DTE]'] >= min_dte) &
        (spx_options_data[' [DTE]'] <= max_dte)
    ].copy()
    
    clean_data[' [C_IV]'] = pd.to_numeric(clean_data[' [C_IV]'], errors='coerce')
    clean_data[' [P_IV]'] = pd.to_numeric(clean_data[' [P_IV]'], errors='coerce')
    clean_data[' [UNDERLYING_LAST]'] = pd.to_numeric(clean_data[' [UNDERLYING_LAST]'], errors='coerce')
    clean_data[' [DTE]'] = pd.to_numeric(clean_data[' [DTE]'], errors='coerce')
    
    clean_data = clean_data.dropna(subset=[' [C_IV]', ' [P_IV]', ' [UNDERLYING_LAST]'])
    
    futures = clean_data.groupby([' [QUOTE_DATE]', ' [EXPIRE_DATE]']).agg({
        ' [UNDERLYING_LAST]': 'first',
        ' [DTE]': 'first',
        ' [C_IV]': 'mean',
        ' [P_IV]': 'mean'
    }).reset_index()
    
    futures.columns = ['Date', 'Expiry', 'futures_close', 'days_to_expiry', 'c_iv', 'p_iv']
    
    futures['Date'] = pd.to_datetime(futures['Date'])
    futures['Expiry'] = pd.to_datetime(futures['Expiry'])
    
    futures = futures.set_index(['Date', 'Expiry'])
    
    print(f"✅ futures_data créé : {futures.shape}")
    print(f"   📅 Dates uniques : {futures.index.get_level_values('Date').nunique()}")
    print(f"   📆 Expirations par date (moyenne) : {futures.groupby(level='Date').size().mean():.1f}")
    print(f"\n📊 Types de données :")
    print(futures.dtypes)
    
    return futures

def create_options_data(spx_options_data, min_dte=10, max_dte=180):
    """
    Crée options_data avec : date, expiry, strike_price, last, option_type
    """
    
    options = spx_options_data[
        (spx_options_data[' [DTE]'] >= min_dte) &
        (spx_options_data[' [DTE]'] <= max_dte)
    ].copy()
    
    # CE (Call Options)
    options_ce = options[[' [QUOTE_DATE]', ' [EXPIRE_DATE]', ' [STRIKE]', ' [C_LAST]']].copy()
    options_ce['option_type'] = 'CE'
    options_ce.columns = ['date', 'expiry', 'strike_price', 'last', 'option_type']
    
    # PE (Put Options)
    options_pe = options[[' [QUOTE_DATE]', ' [EXPIRE_DATE]', ' [STRIKE]', ' [P_LAST]']].copy()
    options_pe['option_type'] = 'PE'
    options_pe.columns = ['date', 'expiry', 'strike_price', 'last', 'option_type']
    
    options_data = pd.concat([options_ce, options_pe], ignore_index=True)
    
    options_data['date'] = pd.to_datetime(options_data['date'])
    options_data['expiry'] = pd.to_datetime(options_data['expiry'])
    options_data['strike_price'] = pd.to_numeric(options_data['strike_price'], errors='coerce')
    options_data['last'] = pd.to_numeric(options_data['last'], errors='coerce')
    
    options_data = options_data[
        (options_data['last'].notna()) & 
        (options_data['last'] > 0)
    ]
    
    print(f"✅ options_data créé : {options_data.shape}")
    print(f"   📅 Dates uniques : {options_data['date'].nunique()}")
    print(f"   📆 Expirations uniques : {options_data['expiry'].nunique()}")
    print(f"   🎯 Strikes uniques : {options_data['strike_price'].nunique()}")
    print(f"\n📊 Distribution CE vs PE :")
    print(options_data['option_type'].value_counts())
    
    return options_data





