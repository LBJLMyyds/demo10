"""Raw file ingestion helpers."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.pipeline.config import RAW_DATASETS, RAW_DIR


logger = logging.getLogger(__name__)


def read_csv_dataset(filename: str, raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Read one raw CSV file from the project raw data directory."""
    path = raw_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing raw dataset: {path}")
    return pd.read_csv(path)


def load_raw_datasets(raw_dir: Path = RAW_DIR) -> dict[str, pd.DataFrame]:
    """Load all configured raw datasets into memory."""
    return {
        dataset["source_id"]: read_csv_dataset(dataset["filename"], raw_dir)
        for dataset in RAW_DATASETS
    }


def build_data_sources(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Create the data_sources table from configured metadata and local files."""
    rows = []
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for dataset in RAW_DATASETS:
        path = raw_dir / dataset["filename"]
        rows.append(
            {
                "source_id": dataset["source_id"],
                "filename": dataset["filename"],
                "description": dataset["description"],
                "license": dataset["license"],
                "origin": dataset["origin"],
                "file_size_bytes": path.stat().st_size if path.exists() else None,
                "ingested_at": now,
            }
        )
    return pd.DataFrame(rows)

def run_ingestion(raw_dir: Path = RAW_DIR) -> dict[str, pd.DataFrame]:
    """
    Data Ingestion 主入口函数 
    
    1. 确保 data/raw 目录存在
    2. 校验配置的所有 Raw 数据集是否存在
    3. 生成并打印/记录 data_sources 元数据表
    4. 返回读取好的 DataFrames 字典
    """
    logger.info("=== [Step 1] Starting Data Ingestion ===")
    
    # 确保原始数据目录存在
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 构建并记录元数据表
    df_sources = build_data_sources(raw_dir)
    logger.info(f"Ingested metadata for {len(df_sources)} datasets:\n{df_sources[['source_id', 'filename', 'file_size_bytes']]}")
    
    # 2. 读取并载入所有数据集
    datasets = load_raw_datasets(raw_dir)
    logger.info("Successfully loaded all raw datasets into memory.")
    logger.info("=== Data Ingestion Completed ===\n")
    
    return datasets


if __name__ == "__main__":
    # 独立运行该脚本时的测试入口
    run_ingestion()
