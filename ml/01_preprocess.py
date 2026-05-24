import pandas as pd
import numpy as np
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "nps_visitation.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
THRESHOLDS_PATH = PROCESSED_DIR / "park_thresholds.csv"
FEATURES_PATH = PROCESSED_DIR / "features.csv"

# Ensure processed directory exists
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def preprocess():
    # LOADING
    print(f"Loading data from {RAW_DATA_PATH}...")
    try:
        # Try tab-separated first as per user instructions
        df = pd.read_csv(RAW_DATA_PATH, sep='\t', thousands=',')
        # Heuristic to check if it worked: check if we have more than one column
        # or if the first column name looks like it's actually comma-separated
        if df.shape[1] <= 1:
            print("Tab-separated failed, trying comma-separated...")
            df = pd.read_csv(RAW_DATA_PATH, sep=',', thousands=',')
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    # Immediately drop all columns whose name ends with 'Total'
    cols_to_drop = [c for c in df.columns if c.endswith('Total')]
    df = df.drop(columns=cols_to_drop)

    print(f"Columns found: {df.columns.tolist()}")
    print("First 3 rows after loading:")
    print(df.head(3))

    # FILTERING
    # Ensure Year and RecreationVisits are numeric
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df['RecreationVisits'] = pd.to_numeric(df['RecreationVisits'], errors='coerce')
    
    df = df.dropna(subset=['Year', 'RecreationVisits'])
    df = df[(df['Year'] >= 2010) & (df['RecreationVisits'] > 0)].copy()

    # FEATURE ENGINEERING
    # Normalize UnitCode -> park_code
    df['park_code'] = df['UnitCode'].str.strip().str.lower()

    # Normalize Region
    def normalize_region(r):
        if not isinstance(r, str):
            return 'other'
        r = r.strip().lower().replace(' ', '_')
        valid_regions = [
            'southeast', 'northeast', 'midwest', 'alaska', 
            'pacific_west', 'intermountain', 'national_capital'
        ]
        return r if r in valid_regions else 'other'

    df['region_norm'] = df['Region'].apply(normalize_region)

    # month
    df['month'] = df['Month'].astype(int)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    # is_summer (6, 7, 8)
    df['is_summer'] = df['month'].isin([6, 7, 8]).astype(int)
    
    # is_holiday_month (7, 11, 12)
    df['is_holiday_month'] = df['month'].isin([7, 11, 12]).astype(int)
    
    # is_weekend (placeholder)
    df['is_weekend'] = 0

    # ONE-HOT ENCODE region
    regions = [
        'southeast', 'northeast', 'midwest', 'alaska', 
        'pacific_west', 'intermountain', 'national_capital', 'other'
    ]
    for r in regions:
        df[f'region_{r}'] = (df['region_norm'] == r).astype(int)

    # CROWD LABEL (per-park quartile)
    # Group by park_code, compute q25/q50/q75 of RecreationVisits
    thresholds = df.groupby('park_code')['RecreationVisits'].quantile([0.25, 0.5, 0.75]).unstack()
    thresholds.columns = ['q25', 'q50', 'q75']
    thresholds = thresholds.reset_index()
    
    # Save thresholds
    thresholds.to_csv(THRESHOLDS_PATH, index=False)
    print(f"Saved thresholds to {THRESHOLDS_PATH}")

    # Merge thresholds back to df to compute labels
    df = df.merge(thresholds, on='park_code')

    def get_crowd_label(row):
        visits = row['RecreationVisits']
        if visits < row['q25']:
            return 0 # Low
        elif visits < row['q50']:
            return 1 # Moderate
        elif visits < row['q75']:
            return 2 # High
        else:
            return 3 # Very High

    df['crowd_label'] = df.apply(get_crowd_label, axis=1)

    # SAVE
    output_cols = [
        'park_code', 'month', 'month_sin', 'month_cos', 'is_summer', 'is_holiday_month',
        'is_weekend', 'region_southeast', 'region_northeast', 'region_midwest',
        'region_alaska', 'region_pacific_west', 'region_intermountain',
        'region_national_capital', 'region_other', 'crowd_label'
    ]
    features_df = df[output_cols]
    features_df.to_csv(FEATURES_PATH, index=False)
    print(f"Saved features to {FEATURES_PATH}")

    # Final prints
    print(f"Shape: {features_df.shape}")
    print("Class distribution:")
    print(features_df['crowd_label'].value_counts(normalize=True).sort_index())
    print(f"Unique park count: {features_df['park_code'].nunique()}")
    print("Sample of 5 rows:")
    print(features_df.sample(5))

if __name__ == "__main__":
    preprocess()
