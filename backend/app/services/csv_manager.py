"""
app/services/csv_manager.py
────────────────────────────────────────────
1. 수집한 데이터를 CSV로 저장하는 함수(save_to_csv)
2. CSV 파일 불러오기(load_from_csv)
3. API 응답 백업 및 파일 정리(sqve_api_response, cleanup_old_files)
"""

import csv
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path


class CSVManager:
    """CSV 파일 저장 및 관리 클래스"""
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, data_type: str, timestamp: str = None) -> Path:
        """저장할 파일의 경로와 이름을 자동으로 생성"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # data 폴더에 바로 저장: data/leisure_20241012_143022.csv
        filename = f"{data_type}_{timestamp}.csv"
        return self.base_dir / filename
    
    def save_to_csv(self, data: List[Dict[str, Any]], data_type: str, timestamp: str = None) -> str:
        """데이터를 CSV 파일로 저장하는 함수"""
        if not data:
            raise ValueError("저장할 데이터가 없습니다")
        
        file_path = self._get_file_path(data_type, timestamp)
        
        # CSV 헤더는 첫 번째 데이터의 키들로 설정
        fieldnames = list(data[0].keys())
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"CSV 저장 완료: {file_path} ({len(data)}개 레코드)")
        return str(file_path)
    
    def load_from_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """CSV 파일에서 읽어서 리스트 형태로 반환"""
        data = []
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
        
        print(f"CSV 로드 완료: {file_path} ({len(data)}개 레코드)")
        return data
    
    def save_api_response(self, response_data: Dict[str, Any], data_type: str, timestamp: str = None) -> str:
        """API 원본 응답(JSON)을 그대로 저장하는 백업용 함수                                                                                                                       """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"{data_type}_raw_{timestamp}.json"
        file_path = self.base_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(response_data, jsonfile, ensure_ascii=False, indent=2)
        
        print(f"API 응답 백업 저장: {file_path}")
        return str(file_path)
    
    def get_latest_csv(self, data_type: str) -> str:
        """특정 데이터 타입의 가장 최근 CSV 파일 경로 반환"""
        csv_files = list(self.base_dir.glob(f"{data_type}_*.csv"))
        
        if not csv_files:
            raise FileNotFoundError(f"{data_type} 타입의 CSV 파일을 찾을 수 없습니다")
        
        # 파일명의 타임스탬프로 정렬하여 가장 최근 파일 반환
        latest_file = max(csv_files, key=lambda x: x.stem.split('_')[-1])
        return str(latest_file)
