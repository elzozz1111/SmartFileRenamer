"""
License Manager Module
إدارة التفعيل والترخيص باستخدام HMAC-SHA256
"""

import hashlib
import hmac
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple, Optional
from core.hwid import HWIDGenerator


class LicenseManager:
    """إدارة المفاتيح والترخيص"""
    
    # السر المستخدم في التوقيع (يجب تغييره في الإنتاج)
    SECRET_KEY = "SmartFileRenamer_2024_SecureKey_#@!"
    LICENSE_FILE = "license.json"
    
    @staticmethod
    def generate_serial(hwid: str, days_valid: int = 365) -> Tuple[str, Dict]:
        """
        توليد مفتاح تسلسلي (Serial) لـ HWID معين
        
        Args:
            hwid: معرف الجهاز الفريد
            days_valid: عدد أيام صلاحية المفتاح
        
        Returns:
            (serial, metadata)
        """
        # إنشاء بيانات التوقيع
        timestamp = datetime.now().isoformat()
        expiry = (datetime.now() + timedelta(days=days_valid)).isoformat()
        
        # البيانات المراد توقيعها
        data = f"{hwid}|{timestamp}|{expiry}"
        
        # إنشاء التوقيع HMAC-SHA256
        signature = hmac.new(
            LicenseManager.SECRET_KEY.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # صيغة المفتاح التسلسلي
        serial = f"SFR-{hwid[:16]}-{signature[:16]}"
        
        metadata = {
            "hwid": hwid,
            "issued_at": timestamp,
            "expires_at": expiry,
            "signature": signature,
            "version": "1.0"
        }
        
        return serial, metadata
    
    @staticmethod
    def verify_serial(serial: str, hwid: str) -> Tuple[bool, Optional[Dict]]:
        """
        التحقق من صحة المفتاح التسلسلي
        
        Args:
            serial: المفتاح المراد التحقق منه
            hwid: معرف الجهاز
        
        Returns:
            (is_valid, metadata)
        """
        try:
            # فك صيغة المفتاح
            parts = serial.split('-')
            if len(parts) < 2 or parts[0] != "SFR":
                return False, None
            
            # استخراج HWID من المفتاح
            serial_hwid_prefix = parts[1]
            if not hwid.startswith(serial_hwid_prefix):
                return False, None
            
            # في التطبيق الحقيقي، يجب التحقق من التوقيع ضد قاعدة البيانات
            # هنا نقوم بتحقق بسيط
            
            metadata = {
                "hwid": hwid,
                "verified": True,
                "timestamp": datetime.now().isoformat()
            }
            
            return True, metadata
        
        except Exception as e:
            print(f"خطأ في التحقق من المفتاح: {e}")
            return False, None
    
    @staticmethod
    def save_license(license_data: Dict, hwid_path: str = "hwid.json"):
        """حفظ بيانات الترخيص"""
        try:
            with open(LicenseManager.LICENSE_FILE, 'w') as f:
                json.dump(license_data, f, indent=4)
            return True
        except Exception as e:
            print(f"خطأ في حفظ الترخيص: {e}")
            return False
    
    @staticmethod
    def load_license() -> Optional[Dict]:
        """قراءة بيانات الترخيص"""
        try:
            if not Path(LicenseManager.LICENSE_FILE).exists():
                return None
            
            with open(LicenseManager.LICENSE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"خطأ في قراءة الترخيص: {e}")
            return False
    
    @staticmethod
    def is_license_valid() -> bool:
        """التحقق من أن الترخيص صحيح وسارٍ"""
        license_data = LicenseManager.load_license()
        
        if not license_data:
            return False
        
        try:
            # التحقق من انتهاء الصلاحية
            expiry = datetime.fromisoformat(license_data.get("expires_at", ""))
            if datetime.now() > expiry:
                return False
            
            # التحقق من HWID
            current_hwid, _ = HWIDGenerator.generate_hwid()
            if license_data.get("hwid") != current_hwid:
                return False
            
            return True
        except Exception as e:
            print(f"خطأ في التحقق من الترخيص: {e}")
            return False
    
    @staticmethod
    def get_license_info() -> Optional[Dict]:
        """الحصول على معلومات الترخيص الحالي"""
        return LicenseManager.load_license()
