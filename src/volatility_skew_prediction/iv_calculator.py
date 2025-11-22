import pandas as pd
import numpy as np 
import mibian 
from collections import Counter


# calculate ATM & OTM Strike Price 

def find_strike_difference(options_data):
    """
    Trouve la différence de strike la plus commune dans les données
    """
    
    sample_date = options_data['date'].iloc[0]
    sample_options = options_data[options_data['date'] == sample_date]
    strikes = sorted(sample_options['strike_price'].unique())
    differences = [strikes[i+1] - strikes[i] for i in range(len(strikes)-1)]
  
    strike_diff = Counter(differences).most_common(1)[0][0]
    
    print(f"✅ Strike difference détecté : {strike_diff}")
    print(f"📊 Exemples de strikes : {strikes[:10]}")

    return strike_diff

def calculate_atm_strike_p(futures_data, strike_diff):
    """ calculate ATM Strike Price """
    futures_data['atm_strike_price'] = strike_diff * round(futures_data['futures_close'] / strike_diff)
    futures_data['otm_call_strike_price'] = futures_data.atm_strike_price + strike_diff*2
    futures_data['otm_put_strike_price'] = futures_data.atm_strike_price - strike_diff*2

    return futures_data












