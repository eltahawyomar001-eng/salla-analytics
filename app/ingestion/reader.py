"""XLSX reader with chunked processing and Arabic digit normalization."""

import logging
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
import re
from datetime import datetime
import numpy as np

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False

from ..config import (
    CHUNK_SIZE_ROWS, 
    MAX_ROWS_PREVIEW, 
    ARABIC_TO_ENGLISH_DIGITS,
    DATE_PATTERNS
)

logger = logging.getLogger(__name__)

class XLSXReader:
    """Handles XLSX file reading with chunked processing and normalization."""
    
    def __init__(self):
        self.arabic_digit_pattern = re.compile(r'[٠-٩]')
        
    def normalize_arabic_digits(self, text: str) -> str:
        """Convert Arabic digits to English digits."""
        if not isinstance(text, str):
            return text
            
        result = text
        for arabic, english in ARABIC_TO_ENGLISH_DIGITS.items():
            result = result.replace(arabic, english)
        return result
    
    def normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize Arabic digits in all string columns."""
        df_normalized = df.copy()
        
        # Normalize column names
        df_normalized.columns = [
            self.normalize_arabic_digits(str(col)) 
            for col in df_normalized.columns
        ]
        
        # Normalize string data
        for col in df_normalized.columns:
            if df_normalized[col].dtype == 'object':
                df_normalized[col] = df_normalized[col].astype(str).apply(
                    self.normalize_arabic_digits
                )
        
        return df_normalized
    
    def detect_date_column(self, series: pd.Series) -> bool:
        """Detect if a series contains date values."""
        if series.dtype == 'datetime64[ns]':
            return True
            
        # Sample some non-null values
        sample = series.dropna().head(100)
        if len(sample) == 0:
            return False
            
        date_count = 0
        for value in sample:
            if self._is_date_like(str(value)):
                date_count += 1
                
        return date_count / len(sample) > 0.7
    
    def _is_date_like(self, value: str) -> bool:
        """Check if a string value looks like a date."""
        value = value.strip()
        
        # Common date patterns
        date_patterns = [
            r'\d{4}-\d{1,2}-\d{1,2}',  # YYYY-MM-DD
            r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY or DD/MM/YYYY
            r'\d{1,2}-\d{1,2}-\d{4}',  # MM-DD-YYYY or DD-MM-YYYY
            r'\d{4}/\d{1,2}/\d{1,2}',  # YYYY/MM/DD
        ]
        
        for pattern in date_patterns:
            if re.match(pattern, value):
                return True
                
        return False
    
    def parse_dates(self, df: pd.DataFrame, date_columns: List[str]) -> pd.DataFrame:
        """Parse date columns with multiple format attempts."""
        df_parsed = df.copy()
        
        for col in date_columns:
            if col in df_parsed.columns:
                df_parsed[col] = self._parse_date_column(df_parsed[col])
                
        return df_parsed
    
    def _parse_date_column(self, series: pd.Series) -> pd.Series:
        """Parse a date column trying multiple formats."""
        if series.dtype == 'datetime64[ns]':
            return series
            
        # Try pandas automatic parsing first
        try:
            return pd.to_datetime(series, errors='coerce')
        except:
            pass
        
        # Try specific patterns
        for pattern in DATE_PATTERNS:
            try:
                parsed = pd.to_datetime(series, format=pattern, errors='coerce')
                if parsed.notna().sum() > len(series) * 0.7:  # 70% success rate
                    return parsed
            except:
                continue
                
        # Return original if nothing worked
        logger.warning(f"Could not parse dates in column, keeping as string")
        return series
    
    def read_excel_file(
        self, 
        file_path: Union[str, Path], 
        sheet_name: Optional[str] = None,
        use_chunking: bool = True
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Read Excel file with optional chunking and return data + metadata.
        
        Args:
            file_path: Path to XLSX file
            sheet_name: Sheet name to read (None for first sheet)
            use_chunking: Whether to use chunked reading for large files
            
        Returns:
            Tuple of (DataFrame, metadata_dict)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.suffix.lower() == '.xlsx':
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        metadata = {
            'file_path': str(file_path),
            'file_size_mb': file_path.stat().st_size / (1024 * 1024),
            'read_timestamp': datetime.now(),
            'chunks_used': False,
            'total_rows': 0,
            'columns': [],
            'sheet_names': []
        }
        
        try:
            # Get sheet names
            excel_file = pd.ExcelFile(file_path)
            metadata['sheet_names'] = excel_file.sheet_names
            
            if sheet_name is None:
                sheet_name = str(excel_file.sheet_names[0])
            
            # Preview read to get shape and structure
            preview_df = pd.read_excel(
                file_path, 
                sheet_name=sheet_name, 
                nrows=MAX_ROWS_PREVIEW
            )
            
            metadata['columns'] = list(preview_df.columns)
            
            # Get total row count (approximate)
            full_df = pd.read_excel(file_path, sheet_name=sheet_name)
            metadata['total_rows'] = len(full_df)
            
            # Decide on chunking strategy
            if use_chunking and metadata['total_rows'] > CHUNK_SIZE_ROWS:
                logger.info(f"Using chunked reading for {metadata['total_rows']} rows")
                df = self._read_in_chunks(file_path, sheet_name, metadata)
                metadata['chunks_used'] = True
            else:
                df = full_df
            
            # Normalize Arabic digits
            df = self.normalize_dataframe(df)
            
            # Detect and parse date columns
            date_columns = [
                col for col in df.columns 
                if self.detect_date_column(df[col])
            ]
            
            if date_columns:
                logger.info(f"Detected date columns: {date_columns}")
                df = self.parse_dates(df, date_columns)
                
            metadata['date_columns'] = date_columns
            metadata['final_shape'] = df.shape
            
            return df, metadata
            
        except Exception as e:
            logger.error(f"Error reading Excel file: {e}")
            raise
    
    def _read_in_chunks(
        self, 
        file_path: Path, 
        sheet_name: str, 
        metadata: Dict[str, Any]
    ) -> pd.DataFrame:
        """Read large Excel file in chunks using polars for efficiency."""
        try:
            # Use polars for better performance on large files
            if POLARS_AVAILABLE:
                df_polars = pl.read_excel(file_path, sheet_name=sheet_name)  # type: ignore
                df = df_polars.to_pandas()
                logger.info(f"Successfully read {len(df)} rows using polars")
                return df
            else:
                logger.info("Polars not available, using pandas")
                
        except Exception as e:
            logger.warning(f"Polars reading failed, falling back to pandas: {e}")
            
        # Fallback to pandas chunked reading
        chunks = []
        chunk_size = CHUNK_SIZE_ROWS
        
        for start_row in range(0, metadata['total_rows'], chunk_size):
            chunk = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                skiprows=range(1, start_row + 1) if start_row > 0 else None,
                nrows=chunk_size
            )
            chunks.append(chunk)
            logger.info(f"Read chunk {len(chunks)}: rows {start_row} to {start_row + len(chunk)}")
        
        return pd.concat(chunks, ignore_index=True)
    
    def get_file_preview(
        self, 
        file_path: Union[str, Path], 
        sheet_name: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Get a preview of the file with basic statistics."""
        file_path = Path(file_path)
        
        try:
            excel_file = pd.ExcelFile(file_path)
            
            if sheet_name is None:
                sheet_name = str(excel_file.sheet_names[0])
            
            # Read preview
            preview_df = pd.read_excel(
                file_path, 
                sheet_name=sheet_name, 
                nrows=MAX_ROWS_PREVIEW
            )
            
            # Normalize for preview
            preview_df = self.normalize_dataframe(preview_df)
            
            # Basic statistics
            stats = {
                'sheet_names': excel_file.sheet_names,
                'selected_sheet': sheet_name,
                'total_columns': len(preview_df.columns),
                'column_names': list(preview_df.columns),
                'preview_rows': len(preview_df),
                'data_types': preview_df.dtypes.to_dict(),
                'null_counts': preview_df.isnull().sum().to_dict(),
                'sample_values': {}
            }
            
            # Sample values for each column
            for col in preview_df.columns:
                non_null_values = preview_df[col].dropna()
                if len(non_null_values) > 0:
                    stats['sample_values'][col] = list(non_null_values.head(3).astype(str))
                else:
                    stats['sample_values'][col] = []
            
            return preview_df, stats
            
        except Exception as e:
            logger.error(f"Error getting file preview: {e}")
            raise

def read_salla_export(file_path: Union[str, Path]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Convenience function to read Salla export files.
    
    Args:
        file_path: Path to the Salla XLSX export file
        
    Returns:
        Tuple of (DataFrame, metadata)
    """
    reader = XLSXReader()
    return reader.read_excel_file(file_path)

def get_preview(file_path: Union[str, Path]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Convenience function to get file preview.
    
    Args:
        file_path: Path to the XLSX file
        
    Returns:
        Tuple of (preview_DataFrame, stats)
    """
    reader = XLSXReader()
    return reader.get_file_preview(file_path)