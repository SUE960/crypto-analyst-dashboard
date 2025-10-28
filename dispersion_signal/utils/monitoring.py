"""
시스템 모니터링 및 알림 모듈
"""
import logging
import smtplib
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from dataclasses import dataclass
from enum import Enum

class AlertSeverity(Enum):
    """알림 심각도"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AlertThreshold:
    """알림 임계값 설정"""
    api_failure_rate: float = 0.1  # API 실패율 10%
    data_missing_hours: int = 2    # 데이터 누락 2시간
    price_dispersion_threshold: float = 5.0  # 가격 분산도 5%
    quality_score_threshold: float = 70.0    # 품질 점수 70점
    consecutive_failures: int = 3  # 연속 실패 3회

@dataclass
class AlertConfig:
    """알림 설정"""
    email_enabled: bool = False
    slack_enabled: bool = False
    email_recipients: List[str] = None
    slack_webhook_url: str = ""
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""

class SystemMonitor:
    """시스템 모니터링 및 알림 클래스"""
    
    def __init__(self, config: AlertConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.thresholds = AlertThreshold()
        
        # 모니터링 상태 저장
        self.api_failure_counts = {}
        self.last_data_timestamps = {}
        self.consecutive_failures = {}
        
        # 알림 히스토리 (중복 알림 방지)
        self.alert_history = {}
        self.alert_cooldown = timedelta(minutes=30)  # 30분 쿨다운
    
    def monitor_api_call(self, api_name: str, success: bool, response_time: float = 0.0):
        """
        API 호출 모니터링
        
        Args:
            api_name: API 이름
            success: 호출 성공 여부
            response_time: 응답 시간 (초)
        """
        if api_name not in self.api_failure_counts:
            self.api_failure_counts[api_name] = {'total': 0, 'failures': 0}
        
        self.api_failure_counts[api_name]['total'] += 1
        if not success:
            self.api_failure_counts[api_name]['failures'] += 1
            
            # 연속 실패 카운트
            if api_name not in self.consecutive_failures:
                self.consecutive_failures[api_name] = 0
            self.consecutive_failures[api_name] += 1
            
            # 연속 실패 임계값 체크
            if self.consecutive_failures[api_name] >= self.thresholds.consecutive_failures:
                self._send_alert(
                    severity=AlertSeverity.HIGH,
                    title=f"API 연속 실패 알림",
                    message=f"{api_name} API가 {self.consecutive_failures[api_name]}회 연속 실패했습니다.",
                    details={'api_name': api_name, 'consecutive_failures': self.consecutive_failures[api_name]}
                )
        else:
            # 성공 시 연속 실패 카운트 리셋
            if api_name in self.consecutive_failures:
                self.consecutive_failures[api_name] = 0
        
        # API 실패율 체크
        failure_rate = self.api_failure_counts[api_name]['failures'] / self.api_failure_counts[api_name]['total']
        if failure_rate > self.thresholds.api_failure_rate:
            self._send_alert(
                severity=AlertSeverity.MEDIUM,
                title=f"API 실패율 높음",
                message=f"{api_name} API 실패율이 {failure_rate:.1%}입니다. (임계값: {self.thresholds.api_failure_rate:.1%})",
                details={'api_name': api_name, 'failure_rate': failure_rate}
            )
    
    def monitor_data_freshness(self, data_source: str, last_timestamp: datetime):
        """
        데이터 신선도 모니터링
        
        Args:
            data_source: 데이터 소스 이름
            last_timestamp: 마지막 데이터 타임스탬프
        """
        self.last_data_timestamps[data_source] = last_timestamp
        
        now = datetime.now(timezone.utc)
        time_diff = now - last_timestamp
        
        if time_diff > timedelta(hours=self.thresholds.data_missing_hours):
            self._send_alert(
                severity=AlertSeverity.HIGH,
                title=f"데이터 누락 알림",
                message=f"{data_source} 데이터가 {time_diff} 동안 업데이트되지 않았습니다.",
                details={'data_source': data_source, 'last_update': last_timestamp.isoformat()}
            )
    
    def monitor_price_dispersion(self, symbol: str, dispersion: float):
        """
        가격 분산도 모니터링
        
        Args:
            symbol: 코인 심볼
            dispersion: 가격 분산도 (%)
        """
        if dispersion > self.thresholds.price_dispersion_threshold:
            self._send_alert(
                severity=AlertSeverity.MEDIUM,
                title=f"높은 가격 분산도",
                message=f"{symbol}의 가격 분산도가 {dispersion:.2f}%입니다. (임계값: {self.thresholds.price_dispersion_threshold}%)",
                details={'symbol': symbol, 'dispersion': dispersion}
            )
    
    def monitor_data_quality(self, symbol: str, quality_score: float):
        """
        데이터 품질 모니터링
        
        Args:
            symbol: 코인 심볼
            quality_score: 품질 점수 (0-100)
        """
        if quality_score < self.thresholds.quality_score_threshold:
            self._send_alert(
                severity=AlertSeverity.LOW,
                title=f"낮은 데이터 품질",
                message=f"{symbol}의 데이터 품질 점수가 {quality_score:.1f}점입니다. (임계값: {self.thresholds.quality_score_threshold}점)",
                details={'symbol': symbol, 'quality_score': quality_score}
            )
    
    def _send_alert(self, severity: AlertSeverity, title: str, message: str, details: Dict[str, Any]):
        """
        알림 전송
        
        Args:
            severity: 알림 심각도
            title: 알림 제목
            message: 알림 메시지
            details: 상세 정보
        """
        # 중복 알림 방지
        alert_key = f"{title}_{severity.value}"
        now = datetime.now(timezone.utc)
        
        if alert_key in self.alert_history:
            last_alert_time = self.alert_history[alert_key]
            if now - last_alert_time < self.alert_cooldown:
                return
        
        self.alert_history[alert_key] = now
        
        # 이메일 알림
        if self.config.email_enabled:
            self._send_email_alert(severity, title, message, details)
        
        # Slack 알림
        if self.config.slack_enabled:
            self._send_slack_alert(severity, title, message, details)
        
        # 로그 기록
        self.logger.warning(f"ALERT [{severity.value.upper()}] {title}: {message}")
    
    def _send_email_alert(self, severity: AlertSeverity, title: str, message: str, details: Dict[str, Any]):
        """이메일 알림 전송"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.smtp_username
            msg['To'] = ', '.join(self.config.email_recipients)
            msg['Subject'] = f"[{severity.value.upper()}] {title}"
            
            body = f"""
{alert_severity_emoji(severity)} {title}

{message}

상세 정보:
{json.dumps(details, indent=2, ensure_ascii=False)}

시간: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

---
Dispersion Signal Monitoring System
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            server.starttls()
            server.login(self.config.smtp_username, self.config.smtp_password)
            
            text = msg.as_string()
            server.sendmail(self.config.smtp_username, self.config.email_recipients, text)
            server.quit()
            
            self.logger.info(f"이메일 알림 전송 완료: {title}")
            
        except Exception as e:
            self.logger.error(f"이메일 알림 전송 실패: {e}")
    
    def _send_slack_alert(self, severity: AlertSeverity, title: str, message: str, details: Dict[str, Any]):
        """Slack 알림 전송"""
        try:
            color_map = {
                AlertSeverity.LOW: "#36a64f",      # 녹색
                AlertSeverity.MEDIUM: "#ff9500",    # 주황색
                AlertSeverity.HIGH: "#ff0000",     # 빨간색
                AlertSeverity.CRITICAL: "#8B0000"   # 진한 빨간색
            }
            
            payload = {
                "attachments": [
                    {
                        "color": color_map[severity],
                        "title": f"{alert_severity_emoji(severity)} {title}",
                        "text": message,
                        "fields": [
                            {
                                "title": "심각도",
                                "value": severity.value.upper(),
                                "short": True
                            },
                            {
                                "title": "시간",
                                "value": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
                                "short": True
                            }
                        ],
                        "footer": "Dispersion Signal Monitoring",
                        "ts": int(datetime.now(timezone.utc).timestamp())
                    }
                ]
            }
            
            # 상세 정보 추가
            if details:
                detail_text = "\n".join([f"• {k}: {v}" for k, v in details.items()])
                payload["attachments"][0]["fields"].append({
                    "title": "상세 정보",
                    "value": detail_text,
                    "short": False
                })
            
            response = requests.post(self.config.slack_webhook_url, json=payload)
            response.raise_for_status()
            
            self.logger.info(f"Slack 알림 전송 완료: {title}")
            
        except Exception as e:
            self.logger.error(f"Slack 알림 전송 실패: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        시스템 상태 요약 반환
        
        Returns:
            시스템 상태 딕셔너리
        """
        status = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'api_status': {},
            'data_freshness': {},
            'alert_summary': {
                'total_alerts': len(self.alert_history),
                'recent_alerts': []
            }
        }
        
        # API 상태
        for api_name, counts in self.api_failure_counts.items():
            failure_rate = counts['failures'] / counts['total'] if counts['total'] > 0 else 0
            status['api_status'][api_name] = {
                'total_calls': counts['total'],
                'failures': counts['failures'],
                'failure_rate': failure_rate,
                'status': 'healthy' if failure_rate < self.thresholds.api_failure_rate else 'degraded',
                'consecutive_failures': self.consecutive_failures.get(api_name, 0)
            }
        
        # 데이터 신선도
        now = datetime.now(timezone.utc)
        for source, last_timestamp in self.last_data_timestamps.items():
            time_diff = now - last_timestamp
            status['data_freshness'][source] = {
                'last_update': last_timestamp.isoformat(),
                'age_minutes': int(time_diff.total_seconds() / 60),
                'status': 'fresh' if time_diff < timedelta(hours=self.thresholds.data_missing_hours) else 'stale'
            }
        
        # 최근 알림
        recent_alerts = []
        for alert_key, alert_time in self.alert_history.items():
            if now - alert_time < timedelta(hours=24):  # 최근 24시간
                recent_alerts.append({
                    'alert': alert_key,
                    'time': alert_time.isoformat()
                })
        
        status['alert_summary']['recent_alerts'] = recent_alerts[-10:]  # 최근 10개
        
        return status
    
    def reset_counters(self):
        """모니터링 카운터 리셋"""
        self.api_failure_counts.clear()
        self.consecutive_failures.clear()
        self.logger.info("모니터링 카운터 리셋 완료")

def alert_severity_emoji(severity: AlertSeverity) -> str:
    """알림 심각도별 이모지 반환"""
    emoji_map = {
        AlertSeverity.LOW: "🟢",
        AlertSeverity.MEDIUM: "🟡", 
        AlertSeverity.HIGH: "🟠",
        AlertSeverity.CRITICAL: "🔴"
    }
    return emoji_map.get(severity, "⚪")
