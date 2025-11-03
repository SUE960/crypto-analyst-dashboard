"""
데이터 백업 및 복구 시스템
"""
import logging
import json
import gzip
import shutil
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from pathlib import Path
import os
from dataclasses import dataclass
from enum import Enum

class BackupType(Enum):
    """백업 타입"""
    FULL = "full"           # 전체 백업
    INCREMENTAL = "incremental"  # 증분 백업
    DIFFERENTIAL = "differential"  # 차등 백업

@dataclass
class BackupConfig:
    """백업 설정"""
    backup_directory: str = "backups"
    retention_days: int = 30  # 백업 보관 기간
    compression_enabled: bool = True
    encryption_enabled: bool = False
    max_backup_size_mb: int = 1000  # 최대 백업 크기 (MB)

class DataBackupManager:
    """데이터 백업 및 복구 관리자"""
    
    def __init__(self, config: BackupConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # 백업 디렉토리 생성
        self.backup_path = Path(config.backup_directory)
        self.backup_path.mkdir(exist_ok=True)
        
        # 백업 메타데이터 파일
        self.metadata_file = self.backup_path / "backup_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """백업 메타데이터 로드"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"백업 메타데이터 로드 실패: {e}")
        
        return {
            'backups': [],
            'last_full_backup': None,
            'last_incremental_backup': None
        }
    
    def _save_metadata(self):
        """백업 메타데이터 저장"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"백업 메타데이터 저장 실패: {e}")
    
    def create_backup(self, data: Dict[str, Any], backup_type: BackupType = BackupType.FULL) -> Optional[str]:
        """
        데이터 백업 생성
        
        Args:
            data: 백업할 데이터
            backup_type: 백업 타입
            
        Returns:
            백업 파일 경로 또는 None
        """
        try:
            timestamp = datetime.now(timezone.utc)
            backup_filename = f"backup_{backup_type.value}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            
            if self.config.compression_enabled:
                backup_filename += ".gz"
            
            backup_file_path = self.backup_path / backup_filename
            
            # 데이터 직렬화
            backup_data = {
                'metadata': {
                    'backup_type': backup_type.value,
                    'timestamp': timestamp.isoformat(),
                    'version': '1.0',
                    'data_size': len(json.dumps(data))
                },
                'data': data
            }
            
            # 백업 파일 생성
            if self.config.compression_enabled:
                with gzip.open(backup_file_path, 'wt', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, ensure_ascii=False)
            else:
                with open(backup_file_path, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            # 메타데이터 업데이트
            backup_info = {
                'filename': backup_filename,
                'backup_type': backup_type.value,
                'timestamp': timestamp.isoformat(),
                'size_bytes': backup_file_path.stat().st_size,
                'file_path': str(backup_file_path)
            }
            
            self.metadata['backups'].append(backup_info)
            
            if backup_type == BackupType.FULL:
                self.metadata['last_full_backup'] = timestamp.isoformat()
            elif backup_type == BackupType.INCREMENTAL:
                self.metadata['last_incremental_backup'] = timestamp.isoformat()
            
            self._save_metadata()
            
            self.logger.info(f"백업 생성 완료: {backup_filename} ({backup_info['size_bytes']} bytes)")
            return str(backup_file_path)
            
        except Exception as e:
            self.logger.error(f"백업 생성 실패: {e}")
            return None
    
    def restore_backup(self, backup_filename: str) -> Optional[Dict[str, Any]]:
        """
        백업에서 데이터 복구
        
        Args:
            backup_filename: 백업 파일명
            
        Returns:
            복구된 데이터 또는 None
        """
        try:
            backup_file_path = self.backup_path / backup_filename
            
            if not backup_file_path.exists():
                self.logger.error(f"백업 파일을 찾을 수 없습니다: {backup_filename}")
                return None
            
            # 백업 파일 읽기
            if backup_filename.endswith('.gz'):
                with gzip.open(backup_file_path, 'rt', encoding='utf-8') as f:
                    backup_data = json.load(f)
            else:
                with open(backup_file_path, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
            
            self.logger.info(f"백업 복구 완료: {backup_filename}")
            return backup_data.get('data', {})
            
        except Exception as e:
            self.logger.error(f"백업 복구 실패: {e}")
            return None
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """백업 목록 반환"""
        return self.metadata.get('backups', [])
    
    def get_latest_backup(self, backup_type: Optional[BackupType] = None) -> Optional[Dict[str, Any]]:
        """
        최신 백업 정보 반환
        
        Args:
            backup_type: 특정 백업 타입 (None이면 모든 타입)
            
        Returns:
            최신 백업 정보 또는 None
        """
        backups = self.metadata.get('backups', [])
        
        if backup_type:
            backups = [b for b in backups if b['backup_type'] == backup_type.value]
        
        if not backups:
            return None
        
        # 타임스탬프 기준으로 정렬
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        return backups[0]
    
    def cleanup_old_backups(self):
        """오래된 백업 파일 정리"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.config.retention_days)
            
            backups_to_remove = []
            for backup in self.metadata.get('backups', []):
                backup_date = datetime.fromisoformat(backup['timestamp'].replace('Z', '+00:00'))
                if backup_date < cutoff_date:
                    backups_to_remove.append(backup)
            
            for backup in backups_to_remove:
                backup_file_path = Path(backup['file_path'])
                if backup_file_path.exists():
                    backup_file_path.unlink()
                    self.logger.info(f"오래된 백업 파일 삭제: {backup['filename']}")
                
                self.metadata['backups'].remove(backup)
            
            self._save_metadata()
            
            if backups_to_remove:
                self.logger.info(f"{len(backups_to_remove)}개의 오래된 백업 파일 정리 완료")
            
        except Exception as e:
            self.logger.error(f"백업 정리 실패: {e}")
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """백업 통계 정보 반환"""
        backups = self.metadata.get('backups', [])
        
        if not backups:
            return {
                'total_backups': 0,
                'total_size_bytes': 0,
                'backup_types': {},
                'oldest_backup': None,
                'newest_backup': None
            }
        
        total_size = sum(backup['size_bytes'] for backup in backups)
        
        backup_types = {}
        for backup in backups:
            backup_type = backup['backup_type']
            if backup_type not in backup_types:
                backup_types[backup_type] = {'count': 0, 'size_bytes': 0}
            backup_types[backup_type]['count'] += 1
            backup_types[backup_type]['size_bytes'] += backup['size_bytes']
        
        # 타임스탬프 기준으로 정렬
        backups.sort(key=lambda x: x['timestamp'])
        
        return {
            'total_backups': len(backups),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'backup_types': backup_types,
            'oldest_backup': backups[0]['timestamp'],
            'newest_backup': backups[-1]['timestamp'],
            'retention_days': self.config.retention_days
        }
    
    def verify_backup_integrity(self, backup_filename: str) -> bool:
        """
        백업 파일 무결성 검증
        
        Args:
            backup_filename: 백업 파일명
            
        Returns:
            무결성 검증 결과
        """
        try:
            backup_file_path = self.backup_path / backup_filename
            
            if not backup_file_path.exists():
                return False
            
            # 파일 읽기 테스트
            if backup_filename.endswith('.gz'):
                with gzip.open(backup_file_path, 'rt', encoding='utf-8') as f:
                    backup_data = json.load(f)
            else:
                with open(backup_file_path, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
            
            # 필수 필드 검증
            if 'metadata' not in backup_data or 'data' not in backup_data:
                return False
            
            metadata = backup_data['metadata']
            required_fields = ['backup_type', 'timestamp', 'version']
            
            for field in required_fields:
                if field not in metadata:
                    return False
            
            self.logger.info(f"백업 무결성 검증 통과: {backup_filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"백업 무결성 검증 실패: {e}")
            return False
    
    def export_backup(self, backup_filename: str, export_path: str) -> bool:
        """
        백업 파일 외부로 내보내기
        
        Args:
            backup_filename: 백업 파일명
            export_path: 내보낼 경로
            
        Returns:
            내보내기 성공 여부
        """
        try:
            backup_file_path = self.backup_path / backup_filename
            export_file_path = Path(export_path)
            
            if not backup_file_path.exists():
                self.logger.error(f"백업 파일을 찾을 수 없습니다: {backup_filename}")
                return False
            
            # 디렉토리 생성
            export_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 파일 복사
            shutil.copy2(backup_file_path, export_file_path)
            
            self.logger.info(f"백업 파일 내보내기 완료: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"백업 파일 내보내기 실패: {e}")
            return False
