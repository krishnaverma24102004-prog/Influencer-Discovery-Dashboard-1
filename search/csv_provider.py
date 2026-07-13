import logging
import pandas as pd
from typing import List, Dict, Any
from utils.preprocessing import validate_and_clean_dataframe

logger = logging.getLogger(__name__)

def load_from_csv(filepath: str) -> List[Dict[str, Any]]:
    """
    Loads influencer data from a CSV or Excel file and cleans it.
    
    Args:
        filepath (str): Path to the uploaded or local CSV/Excel file.
        
    Returns:
        List[Dict[str, Any]]: A list of validated influencer records.
    """
    try:
        if filepath.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        else:
            df = pd.read_csv(filepath)
            
        cleaned_df = validate_and_clean_dataframe(df)
        return cleaned_df.to_dict(orient="records")
        
    except ValueError as ve:
        logger.error(f"Validation error for {filepath}: {ve}")
        raise ve
    except Exception as e:
        logger.error(f"Failed to load data from {filepath}: {e}")
        raise ValueError(f"Could not read the file format correctly. Error: {e}")
