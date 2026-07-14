import logging
import pandas as pd
from typing import List, Dict, Any
from utils.preprocessing import validate_and_clean_dataframe

logger = logging.getLogger(__name__)

import streamlit as st

def load_from_csv(filepath: str) -> List[Dict[str, Any]]:
    """
    Loads influencer data from a CSV or Excel file and cleans it.
    
    Args:
        filepath (str): Path to the uploaded or local CSV/Excel file.
        
    Returns:
        List[Dict[str, Any]]: A list of validated influencer records.
    """
    try:
        skipped_rows = 0
        if filepath.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        else:
            try:
                df = pd.read_csv(filepath)
            except pd.errors.ParserError:
                logger.warning(f"ParserError encountered on {filepath}. Retrying with Python engine and skipping bad lines.")
                
                # Calculate total data lines to find out how many were skipped
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    total_lines = sum(1 for _ in f) - 1  # exclude header
                
                df = pd.read_csv(filepath, engine="python", on_bad_lines="skip")
                skipped_rows = max(0, total_lines - len(df))
                
        cleaned_df = validate_and_clean_dataframe(df)
        
        if skipped_rows > 0:
            st.warning(f"Imported {len(cleaned_df)} rows successfully. {skipped_rows} malformed rows were skipped.")
            
        return cleaned_df.to_dict(orient="records")
        
    except ValueError as ve:
        logger.error(f"Validation error for {filepath}: {ve}")
        raise ve
    except Exception as e:
        logger.error(f"Failed to load data from {filepath}: {e}")
        raise ValueError(f"Could not read the file format correctly. Error: {e}")
