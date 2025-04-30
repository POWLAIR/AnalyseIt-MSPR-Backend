import pandas as pd
from datetime import datetime

def clean_date_string(date_str):
    """Convertit une chaîne de date en format ISO."""
    try:
        if pd.isna(date_str):
            return None

        if isinstance(date_str, (pd.Timestamp, datetime)):
            return date_str.strftime('%Y-%m-%d')

        formats = [
            '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y',
            '%d-%m-%Y', '%m-%d-%Y', '%Y/%m/%d'
        ]

        for fmt in formats:
            try:
                return pd.to_datetime(date_str, format=fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue

        return pd.to_datetime(date_str).strftime('%Y-%m-%d')
    except ValueError:
        return None

def clean_numeric_value(value):
    """Convertit une valeur en entier de manière sécurisée."""
    try:
        if pd.isna(value):
            return 0
        if isinstance(value, (int, float)):
            return int(value)
        cleaned = str(value).strip().replace(',', '')
        return int(float(cleaned))
    except (ValueError, TypeError):
        return 0

def handle_special_cases(df: pd.DataFrame, dataset_type: str, file_name: str) -> pd.DataFrame:
    """Gère les cas particuliers selon le type de dataset."""
    if dataset_type == "covid19" and "total_confirmed" in df.columns and not any('date' in col.lower() for col in df.columns):
        df["date"] = "2022-05-14"
    if dataset_type == "corona" and file_name in ["worldometer_data.csv", "country_wise_latest.csv"]:
        df["date"] = "2020-01-21"
    if dataset_type == "corona" and file_name == "day_wise.csv" and "Date" in df.columns:
        df["location"] = "Global"
    return df

def map_columns(df: pd.DataFrame, dataset_type: str) -> pd.DataFrame:
    """Mappe les colonnes standardisées selon le type de dataset."""
    if dataset_type == 'mpox':
        column_mapping = {
            'cases': ['total_cases', 'cases'],
            'deaths': ['total_deaths', 'deaths'],
            'new_cases': ['new_cases'],
            'new_deaths': ['new_deaths']
        }
    elif dataset_type == 'covid19':
        column_mapping = {
            'cases': ['total_cases', 'cases'],
            'deaths': ['total_deaths', 'deaths'],
            'recovered': ['total_recovered', 'recovered'],
            'active': ['active_cases', 'active'],
            'new_cases': ['new_cases'],
            'new_deaths': ['new_deaths']
        }
    else:
        column_mapping = {
            'cases': ['Confirmed', 'confirmed', 'cases'],
            'deaths': ['Deaths', 'deaths'],
            'recovered': ['Recovered', 'recovered'],
            'active': ['Active', 'active'],
            'new_cases': ['New cases', 'new_cases'],
            'new_deaths': ['New deaths', 'new_deaths']
        }

    for target_col, possible_names in column_mapping.items():
        for name in possible_names:
            if name in df.columns:
                df[target_col] = df[name]
                break
    return df

def clean_dataset(df: pd.DataFrame, dataset_type: str = None, file_name: str = "") -> pd.DataFrame:
    """
    Nettoie et normalise le dataset en fonction de son type.
    """
    df = handle_special_cases(df, dataset_type, file_name)

    date_columns = [col for col in df.columns if 'date' in col.lower()]
    if not date_columns:
        raise ValueError("Aucune colonne de date trouvée dans le dataset")
    date_col = date_columns[0]

    df['date'] = df[date_col].apply(clean_date_string)
    df = df.dropna(subset=['date'])

    location_columns = [
        col for col in df.columns
        if any(keyword in col.lower() for keyword in ['country', 'location', 'region', 'state'])
    ]
    if not location_columns:
        raise ValueError("Aucune colonne de localisation trouvée dans le dataset")
    location_col = location_columns[0]
    df['location'] = df[location_col]

    df = map_columns(df, dataset_type)

    numeric_columns = ['cases', 'deaths', 'recovered', 'active', 'new_cases', 'new_deaths']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        else:
            df[col] = 0

    if 'active' not in df.columns or df['active'].isna().all():
        df['active'] = df['cases'] - df['deaths'] - df['recovered']
        df['active'] = df['active'].clip(lower=0)

    if 'new_cases' not in df.columns or df['new_cases'].isna().all():
        df['new_cases'] = df.groupby('location')['cases'].diff().fillna(0).astype(int)
    if 'new_deaths' not in df.columns or df['new_deaths'].isna().all():
        df['new_deaths'] = df.groupby('location')['deaths'].diff().fillna(0).astype(int)

    required_columns = ['date', 'location', 'cases', 'deaths', 'recovered', 'active', 'new_cases', 'new_deaths']
    for col in required_columns:
        if col not in df.columns:
            df[col] = 0

    df = df.sort_values('date')
    return df
