"""
보안 강화 모듈
"""
import os
import logging
import hashlib
import secrets
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from enum import Enum
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecurityLevel(Enum):
    """보안 레벨"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityConfig:
    """보안 설정"""
    encryption_key_file: str = "security/encryption.key"
    access_log_file: str = "logs/access.log"
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    session_timeout_minutes: int = 60
    password_min_length: int = 12
    require_special_chars: bool = True
    require_numbers: bool = True
    require_uppercase: bool = True

class SecurityManager:
    """보안 관리자"""
    
    def __init__(self, config: SecurityConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # 보안 디렉토리 생성
        os.makedirs(os.path.dirname(config.encryption_key_file), exist_ok=True)
        os.makedirs(os.path.dirname(config.access_log_file), exist_ok=True)
        
        # 암호화 키 로드/생성
        self.encryption_key = self._load_or_generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # 접근 제어 상태
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.active_sessions: Dict[str, datetime] = {}
        
        # 보안 이벤트 로그
        self.security_events: List[Dict[str, Any]] = []
    
    def _load_or_generate_key(self) -> bytes:
        """암호화 키 로드 또는 생성"""
        key_file = self.config.encryption_key_file
        
        if os.path.exists(key_file):
            try:
                with open(key_file, 'rb') as f:
                    return f.read()
            except Exception as e:
                self.logger.error(f"암호화 키 로드 실패: {e}")
        
        # 새 키 생성
        key = Fernet.generate_key()
        try:
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # 소유자만 읽기/쓰기
            self.logger.info("새 암호화 키 생성 완료")
        except Exception as e:
            self.logger.error(f"암호화 키 저장 실패: {e}")
        
        return key
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """
        민감한 데이터 암호화
        
        Args:
            data: 암호화할 데이터
            
        Returns:
            암호화된 데이터 (base64 인코딩)
        """
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"데이터 암호화 실패: {e}")
            raise
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """
        암호화된 데이터 복호화
        
        Args:
            encrypted_data: 암호화된 데이터 (base64 인코딩)
            
        Returns:
            복호화된 데이터
        """
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            self.logger.error(f"데이터 복호화 실패: {e}")
            raise
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """
        비밀번호 해시화
        
        Args:
            password: 원본 비밀번호
            salt: 솔트 (None이면 자동 생성)
            
        Returns:
            (해시된 비밀번호, 솔트)
        """
        if salt is None:
            salt = secrets.token_hex(32)
        
        # PBKDF2를 사용한 해시화
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )
        
        password_hash = base64.b64encode(kdf.derive(password.encode())).decode()
        return password_hash, salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """
        비밀번호 검증
        
        Args:
            password: 입력 비밀번호
            password_hash: 저장된 해시
            salt: 저장된 솔트
            
        Returns:
            검증 결과
        """
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt.encode(),
                iterations=100000,
            )
            
            computed_hash = base64.b64encode(kdf.derive(password.encode())).decode()
            return secrets.compare_digest(password_hash, computed_hash)
        except Exception as e:
            self.logger.error(f"비밀번호 검증 실패: {e}")
            return False
    
    def validate_password_strength(self, password: str) -> tuple[bool, List[str]]:
        """
        비밀번호 강도 검증
        
        Args:
            password: 검증할 비밀번호
            
        Returns:
            (유효성, 오류 메시지 리스트)
        """
        errors = []
        
        # 길이 검증
        if len(password) < self.config.password_min_length:
            errors.append(f"비밀번호는 최소 {self.config.password_min_length}자 이상이어야 합니다")
        
        # 대문자 검증
        if self.config.require_uppercase and not any(c.isupper() for c in password):
            errors.append("비밀번호에 대문자가 포함되어야 합니다")
        
        # 숫자 검증
        if self.config.require_numbers and not any(c.isdigit() for c in password):
            errors.append("비밀번호에 숫자가 포함되어야 합니다")
        
        # 특수문자 검증
        if self.config.require_special_chars and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("비밀번호에 특수문자가 포함되어야 합니다")
        
        # 일반적인 비밀번호 검증
        common_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if password.lower() in common_passwords:
            errors.append("너무 일반적인 비밀번호입니다")
        
        return len(errors) == 0, errors
    
    def generate_api_key(self, length: int = 32) -> str:
        """API 키 생성"""
        return secrets.token_urlsafe(length)
    
    def generate_session_token(self) -> str:
        """세션 토큰 생성"""
        return secrets.token_urlsafe(32)
    
    def log_access_attempt(self, user_id: str, ip_address: str, success: bool, 
                          resource: str = "", details: str = ""):
        """
        접근 시도 로깅
        
        Args:
            user_id: 사용자 ID
            ip_address: IP 주소
            success: 성공 여부
            resource: 접근한 리소스
            details: 상세 정보
        """
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'user_id': user_id,
            'ip_address': ip_address,
            'success': success,
            'resource': resource,
            'details': details
        }
        
        # 파일 로그
        try:
            with open(self.config.access_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"접근 로그 기록 실패: {e}")
        
        # 메모리 로그 (최근 1000개만 유지)
        self.security_events.append(log_entry)
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
        
        # 실패한 시도 기록
        if not success:
            if user_id not in self.failed_attempts:
                self.failed_attempts[user_id] = []
            self.failed_attempts[user_id].append(datetime.now(timezone.utc))
    
    def is_account_locked(self, user_id: str) -> bool:
        """계정 잠금 여부 확인"""
        if user_id not in self.failed_attempts:
            return False
        
        now = datetime.now(timezone.utc)
        lockout_duration = timedelta(minutes=self.config.lockout_duration_minutes)
        
        # 최근 실패 시도들만 필터링
        recent_failures = [
            attempt for attempt in self.failed_attempts[user_id]
            if now - attempt < lockout_duration
        ]
        
        self.failed_attempts[user_id] = recent_failures
        
        return len(recent_failures) >= self.config.max_login_attempts
    
    def create_session(self, user_id: str) -> str:
        """세션 생성"""
        session_token = self.generate_session_token()
        self.active_sessions[session_token] = datetime.now(timezone.utc)
        
        self.log_access_attempt(user_id, "system", True, "session_create", "새 세션 생성")
        return session_token
    
    def validate_session(self, session_token: str) -> bool:
        """세션 유효성 검증"""
        if session_token not in self.active_sessions:
            return False
        
        session_time = self.active_sessions[session_token]
        timeout = timedelta(minutes=self.config.session_timeout_minutes)
        
        if datetime.now(timezone.utc) - session_time > timeout:
            del self.active_sessions[session_token]
            return False
        
        return True
    
    def invalidate_session(self, session_token: str):
        """세션 무효화"""
        if session_token in self.active_sessions:
            del self.active_sessions[session_token]
    
    def get_security_report(self) -> Dict[str, Any]:
        """보안 리포트 생성"""
        now = datetime.now(timezone.utc)
        
        # 최근 24시간 보안 이벤트
        recent_events = [
            event for event in self.security_events
            if datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00')) > now - timedelta(hours=24)
        ]
        
        # 실패한 로그인 시도
        failed_logins = [event for event in recent_events if not event['success']]
        
        # 잠긴 계정
        locked_accounts = [
            user_id for user_id in self.failed_attempts
            if self.is_account_locked(user_id)
        ]
        
        return {
            'timestamp': now.isoformat(),
            'active_sessions': len(self.active_sessions),
            'locked_accounts': len(locked_accounts),
            'recent_events_count': len(recent_events),
            'failed_logins_24h': len(failed_logins),
            'security_level': self._calculate_security_level(recent_events),
            'recommendations': self._generate_security_recommendations(recent_events)
        }
    
    def _calculate_security_level(self, recent_events: List[Dict[str, Any]]) -> SecurityLevel:
        """보안 레벨 계산"""
        if not recent_events:
            return SecurityLevel.LOW
        
        failed_count = len([e for e in recent_events if not e['success']])
        total_count = len(recent_events)
        failure_rate = failed_count / total_count if total_count > 0 else 0
        
        if failure_rate > 0.5:
            return SecurityLevel.CRITICAL
        elif failure_rate > 0.2:
            return SecurityLevel.HIGH
        elif failure_rate > 0.1:
            return SecurityLevel.MEDIUM
        else:
            return SecurityLevel.LOW
    
    def _generate_security_recommendations(self, recent_events: List[Dict[str, Any]]) -> List[str]:
        """보안 권장사항 생성"""
        recommendations = []
        
        failed_count = len([e for e in recent_events if not e['success']])
        
        if failed_count > 10:
            recommendations.append("다수의 실패한 로그인 시도가 감지되었습니다. IP 차단을 고려하세요")
        
        if len(self.active_sessions) > 100:
            recommendations.append("활성 세션이 많습니다. 세션 타임아웃을 줄이거나 정리를 고려하세요")
        
        if not recent_events:
            recommendations.append("보안 이벤트가 없습니다. 모니터링 시스템을 점검하세요")
        
        return recommendations

class APISecurityValidator:
    """API 보안 검증기"""
    
    def __init__(self, security_manager: SecurityManager, logger: Optional[logging.Logger] = None):
        self.security_manager = security_manager
        self.logger = logger or logging.getLogger(__name__)
    
    def validate_api_request(self, api_key: str, ip_address: str, endpoint: str) -> tuple[bool, str]:
        """
        API 요청 검증
        
        Args:
            api_key: API 키
            ip_address: 클라이언트 IP
            endpoint: 요청 엔드포인트
            
        Returns:
            (유효성, 오류 메시지)
        """
        # API 키 형식 검증
        if not api_key or len(api_key) < 16:
            self.security_manager.log_access_attempt("api", ip_address, False, endpoint, "잘못된 API 키 형식")
            return False, "잘못된 API 키 형식"
        
        # IP 주소 검증 (기본적인 형식 체크)
        if not self._is_valid_ip(ip_address):
            self.security_manager.log_access_attempt("api", ip_address, False, endpoint, "잘못된 IP 주소")
            return False, "잘못된 IP 주소"
        
        # 엔드포인트 검증
        if not self._is_allowed_endpoint(endpoint):
            self.security_manager.log_access_attempt("api", ip_address, False, endpoint, "허용되지 않은 엔드포인트")
            return False, "허용되지 않은 엔드포인트"
        
        self.security_manager.log_access_attempt("api", ip_address, True, endpoint, "API 요청 성공")
        return True, ""
    
    def _is_valid_ip(self, ip_address: str) -> bool:
        """IP 주소 유효성 검증"""
        try:
            parts = ip_address.split('.')
            if len(parts) != 4:
                return False
            
            for part in parts:
                if not part.isdigit() or not 0 <= int(part) <= 255:
                    return False
            
            return True
        except:
            return False
    
    def _is_allowed_endpoint(self, endpoint: str) -> bool:
        """허용된 엔드포인트 검증"""
        allowed_endpoints = [
            '/api/data',
            '/api/prices',
            '/api/sentiment',
            '/api/dispersion',
            '/api/health'
        ]
        
        return any(endpoint.startswith(allowed) for allowed in allowed_endpoints)
