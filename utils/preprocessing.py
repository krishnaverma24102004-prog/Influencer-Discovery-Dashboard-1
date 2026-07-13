import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def validate_and_clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates the schema of the uploaded dataframe (case-insensitive), 
    cleans missing values, and normalizes text fields.
    
    Args:
        df (pd.DataFrame): The raw dataframe from CSV or Excel.
        
    Returns:
        pd.DataFrame: Cleaned and normalized dataframe.
        
    Raises:
        ValueError: If essential columns are missing.
    """
    required_columns = [
        "Name", "Handle", "Platform", 
        "Followers", "Language", "Bio", "Recent Posts"
    ]
    
    # Map uploaded column names (case-insensitive) to required names
    df_columns_lower = {str(col).lower().strip(): col for col in df.columns}
    
    missing_cols = []
    rename_mapping = {}
    
    for required in required_columns:
        req_lower = required.lower()
        if req_lower not in df_columns_lower:
            missing_cols.append(required)
        else:
            rename_mapping[df_columns_lower[req_lower]] = required
            
    if missing_cols:
        error_msg = f"Missing required columns: {', '.join(missing_cols)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
        
    # Standardize column names to required format
    cleaned_df = df.rename(columns=rename_mapping)
    
    # Fill missing values with sensible defaults
    cleaned_df["Name"] = cleaned_df["Name"].fillna("Unknown")
    cleaned_df["Handle"] = cleaned_df["Handle"].fillna("Unknown")
    cleaned_df["Platform"] = cleaned_df["Platform"].fillna("Unknown")
    
    # Convert Followers to numeric and set invalid values to 0
    cleaned_df["Followers"] = pd.to_numeric(
        cleaned_df["Followers"].astype(str).str.replace(',', ''), 
        errors='coerce'
    ).fillna(0).astype(int)
    
    cleaned_df["Language"] = cleaned_df["Language"].fillna("Unknown")
    cleaned_df["Bio"] = cleaned_df["Bio"].fillna("")
    cleaned_df["Recent Posts"] = cleaned_df["Recent Posts"].fillna("")
    
    # Normalize text fields for consistency
    cleaned_df["Platform"] = cleaned_df["Platform"].astype(str).str.strip().str.title()
    cleaned_df["Language"] = cleaned_df["Language"].astype(str).str.strip().str.title()
    
    logger.info(f"Successfully cleaned dataframe with {len(cleaned_df)} rows.")
    return cleaned_df

def extract_combined_text(row: pd.Series) -> str:
    """
    Combines Bio and Recent Posts into a single string for AI/Keyword analysis.
    """
    bio = str(row.get("Bio", ""))
    posts = str(row.get("Recent Posts", ""))
    
    # Clean up whitespace
    combined = f"{bio} {posts}".strip()
    return combined
