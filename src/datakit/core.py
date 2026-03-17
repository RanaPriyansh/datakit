"""
Core data conversion and manipulation toolkit.
"""

import json
import csv
import yaml
import toml
import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
import io
import sys


@dataclass
class Dataset:
    """Represents a dataset with metadata."""
    data: Union[List[Dict], pd.DataFrame]
    format: str  # csv, json, yaml, toml, xml, parquet
    schema: Optional[Dict] = None
    source_path: Optional[Path] = None
    
    @property
    def as_dataframe(self) -> pd.DataFrame:
        """Convert to pandas DataFrame."""
        if isinstance(self.data, pd.DataFrame):
            return self.data
        return pd.DataFrame(self.data)
    
    @property
    def as_dicts(self) -> List[Dict]:
        """Convert to list of dictionaries."""
        if isinstance(self.data, pd.DataFrame):
            return self.data.to_dict('records')
        return self.data


class DataConverter:
    """Convert between data formats."""
    
    @staticmethod
    def detect_format(file_path: str) -> str:
        """Detect data format from file extension or content."""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        format_map = {
            '.csv': 'csv',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.xml': 'xml',
            '.parquet': 'parquet',
            '.xlsx': 'excel',
            '.xls': 'excel',
        }
        
        return format_map.get(ext, 'unknown')
    
    @staticmethod
    def load(file_path: str, format: Optional[str] = None) -> Dataset:
        """Load data from file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if format is None:
            format = DataConverter.detect_format(str(path))
        
        data = None
        schema = None
        
        if format == 'csv':
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
                schema = {field: 'string' for field in reader.fieldnames}
        
        elif format == 'json':
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    schema = {k: type(v).__name__ for k, v in data[0].items()}
        
        elif format == 'yaml':
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if isinstance(data, list) and len(data) > 0:
                    schema = {k: type(v).__name__ for k, v in data[0].items()}
        
        elif format == 'toml':
            with open(path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
                # Convert to list of dicts if it's a dict
                if isinstance(data, dict):
                    data = [data]
        
        elif format == 'xml':
            tree = ET.parse(path)
            root = tree.getroot()
            data = []
            for child in root:
                record = {}
                for elem in child:
                    record[elem.tag] = elem.text
                data.append(record)
        
        elif format == 'parquet':
            df = pd.read_parquet(path)
            data = df.to_dict('records')
            schema = {col: str(df[col].dtype) for col in df.columns}
        
        elif format == 'excel':
            df = pd.read_excel(path)
            data = df.to_dict('records')
            schema = {col: str(df[col].dtype) for col in df.columns}
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return Dataset(
            data=data,
            format=format,
            schema=schema,
            source_path=path
        )
    
    @staticmethod
    def save(dataset: Dataset, output_path: str, format: Optional[str] = None) -> str:
        """Save dataset to file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format is None:
            format = DataConverter.detect_format(str(path))
        
        if format == 'csv':
            data = dataset.as_dicts
            if not data:
                raise ValueError("No data to save")
            
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        
        elif format == 'json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(dataset.as_dicts, f, indent=2, ensure_ascii=False)
        
        elif format == 'yaml':
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(dataset.as_dicts, f, default_flow_style=False)
        
        elif format == 'toml':
            # Convert list of dicts to dict of dicts for TOML
            data = dataset.as_dicts
            if len(data) == 1:
                toml_data = data[0]
            else:
                toml_data = {'record': data}
            
            with open(path, 'w', encoding='utf-8') as f:
                toml.dump(toml_data, f)
        
        elif format == 'parquet':
            df = dataset.as_dataframe
            df.to_parquet(path, index=False)
        
        elif format == 'excel':
            df = dataset.as_dataframe
            df.to_excel(path, index=False)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return str(path)
    
    @staticmethod
    def convert(input_path: str, output_path: str, 
                input_format: Optional[str] = None,
                output_format: Optional[str] = None) -> str:
        """Convert data from one format to another."""
        dataset = DataConverter.load(input_path, input_format)
        return DataConverter.save(dataset, output_path, output_format)


class DataValidator:
    """Validate data against schemas."""
    
    @staticmethod
    def validate_schema(data: List[Dict], schema: Dict[str, str]) -> Dict[str, Any]:
        """Validate data against a schema."""
        if not data:
            return {'valid': True, 'errors': [], 'warnings': ['No data to validate']}
        
        errors = []
        warnings = []
        
        # Check all records have all fields
        for i, record in enumerate(data):
            for field_name in schema.keys():
                if field_name not in record:
                    errors.append(f"Record {i}: Missing field '{field_name}'")
                else:
                    # Type checking
                    value = record[field_name]
                    expected_type = schema[field_name]
                    
                    if expected_type == 'string' and not isinstance(value, str):
                        warnings.append(f"Record {i}, field '{field_name}': Expected string, got {type(value).__name__}")
                    elif expected_type == 'number' and not isinstance(value, (int, float)):
                        errors.append(f"Record {i}, field '{field_name}': Expected number, got {type(value).__name__}")
                    elif expected_type == 'boolean' and not isinstance(value, bool):
                        errors.append(f"Record {i}, field '{field_name}': Expected boolean, got {type(value).__name__}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'records_checked': len(data)
        }
    
    @staticmethod
    def infer_schema(data: List[Dict]) -> Dict[str, str]:
        """Infer schema from data."""
        if not data:
            return {}
        
        schema = {}
        for field_name in data[0].keys():
            # Find first non-None value to determine type
            for record in data:
                if field_name in record and record[field_name] is not None:
                    value = record[field_name]
                    if isinstance(value, bool):
                        schema[field_name] = 'boolean'
                    elif isinstance(value, (int, float)):
                        schema[field_name] = 'number'
                    elif isinstance(value, str):
                        schema[field_name] = 'string'
                    elif isinstance(value, list):
                        schema[field_name] = 'array'
                    elif isinstance(value, dict):
                        schema[field_name] = 'object'
                    else:
                        schema[field_name] = 'unknown'
                    break
            else:
                schema[field_name] = 'unknown'
        
        return schema


class DataFilter:
    """Filter and transform data."""
    
    @staticmethod
    def filter(data: List[Dict], conditions: Dict[str, Any]) -> List[Dict]:
        """Filter data by conditions."""
        result = []
        for record in data:
            match = True
            for field, condition in conditions.items():
                if field not in record:
                    match = False
                    break
                
                value = record[field]
                
                # Handle different condition types
                if isinstance(condition, dict):
                    if 'eq' in condition and value != condition['eq']:
                        match = False
                    if 'ne' in condition and value == condition['ne']:
                        match = False
                    if 'gt' in condition and not (isinstance(value, (int, float)) and value > condition['gt']):
                        match = False
                    if 'lt' in condition and not (isinstance(value, (int, float)) and value < condition['lt']):
                        match = False
                    if 'in' in condition and value not in condition['in']:
                        match = False
                elif value != condition:
                    match = False
            
            if match:
                result.append(record)
        
        return result
    
    @staticmethod
    def select(data: List[Dict], fields: List[str]) -> List[Dict]:
        """Select specific fields from data."""
        result = []
        for record in data:
            new_record = {}
            for field in fields:
                if field in record:
                    new_record[field] = record[field]
            result.append(new_record)
        return result
    
    @staticmethod
    def transform(data: List[Dict], transformations: Dict[str, Any]) -> List[Dict]:
        """Apply transformations to data."""
        result = []
        for record in data:
            new_record = record.copy()
            
            for field, transform in transformations.items():
                if field not in new_record:
                    continue
                
                value = new_record[field]
                
                if transform == 'uppercase' and isinstance(value, str):
                    new_record[field] = value.upper()
                elif transform == 'lowercase' and isinstance(value, str):
                    new_record[field] = value.lower()
                elif transform == 'strip' and isinstance(value, str):
                    new_record[field] = value.strip()
                elif isinstance(transform, dict):
                    if 'add' in transform and isinstance(value, (int, float)):
                        new_record[field] = value + transform['add']
                    if 'multiply' in transform and isinstance(value, (int, float)):
                        new_record[field] = value * transform['multiply']
            
            result.append(new_record)
        
        return result


class DataMerger:
    """Merge datasets."""
    
    @staticmethod
    def merge(data1: List[Dict], data2: List[Dict], 
              on: Optional[str] = None, how: str = 'outer') -> List[Dict]:
        """Merge two datasets."""
        if not on:
            # Simple concatenation
            return data1 + data2
        
        # Create dictionaries for fast lookup
        dict1 = {record[on]: record for record in data1 if on in record}
        dict2 = {record[on]: record for record in data2 if on in record}
        
        result = []
        
        if how == 'inner':
            # Only keep records that exist in both
            for key in set(dict1.keys()) & set(dict2.keys()):
                merged = {**dict1[key], **dict2[key]}
                result.append(merged)
        
        elif how == 'left':
            # Keep all from data1, add matching from data2
            for key, record in dict1.items():
                if key in dict2:
                    merged = {**record, **dict2[key]}
                else:
                    merged = record
                result.append(merged)
        
        elif how == 'right':
            # Keep all from data2, add matching from data1
            for key, record in dict2.items():
                if key in dict1:
                    merged = {**dict1[key], **record}
                else:
                    merged = record
                result.append(merged)
        
        else:  # outer
            # Keep all records
            all_keys = set(dict1.keys()) | set(dict2.keys())
            for key in all_keys:
                if key in dict1 and key in dict2:
                    merged = {**dict1[key], **dict2[key]}
                elif key in dict1:
                    merged = dict1[key]
                else:
                    merged = dict2[key]
                result.append(merged)
        
        return result
    
    @staticmethod
    def concat(datasets: List[List[Dict]]) -> List[Dict]:
        """Concatenate multiple datasets."""
        result = []
        for dataset in datasets:
            result.extend(dataset)
        return result


class DataSampler:
    """Sample and analyze data."""
    
    @staticmethod
    def sample(data: List[Dict], n: int = 10, method: str = 'random') -> List[Dict]:
        """Sample n records from data."""
        if n >= len(data):
            return data
        
        if method == 'random':
            import random
            return random.sample(data, n)
        elif method == 'first':
            return data[:n]
        elif method == 'last':
            return data[-n:]
        else:
            raise ValueError(f"Unknown sampling method: {method}")
    
    @staticmethod
    def summary(data: List[Dict]) -> Dict[str, Any]:
        """Generate summary statistics for data."""
        if not data:
            return {'records': 0, 'fields': []}
        
        df = pd.DataFrame(data)
        
        summary = {
            'records': len(data),
            'fields': list(df.columns),
            'field_types': {col: str(df[col].dtype) for col in df.columns},
            'missing_values': df.isnull().sum().to_dict(),
        }
        
        # Numeric summary
        numeric_cols = df.select_dtypes(include=[int, float]).columns
        if len(numeric_cols) > 0:
            summary['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        return summary
