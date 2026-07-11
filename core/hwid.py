"""
HWID Generation Module
يولد معرّف فريد للجهاز بناءً على:
- معرف لوحة الأم (Motherboard Serial)
- عنوان MAC (MAC Address)
- معرف المعالج (CPU ID)
"""

import hashlib
import platform
import socket
import subprocess
import json
from pathlib import Path


class HWIDGenerator:
    """توليد معرف فريد للجهاز (HWID)"""
    
    @staticmethod
    def get_motherboard_serial():
        """الحصول على معرّف لوحة الأم"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["wmic", "baseboard", "get", "serialnumber"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    return lines[1].strip()
            elif platform.system() == "Linux":
                try:
                    with open("/sys/class/dmi/id/board_serial", "r") as f:
                        return f.read().strip()
                except FileNotFoundError:
                    pass
            elif platform.system() == "Darwin":  # macOS
                result = subprocess.run(
                    ["system_profiler", "SPHardwareDataType"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                for line in result.stdout.split('\n'):
                    if "Serial Number" in line:
                        return line.split(":")[-1].strip()
        except Exception as e:
            print(f"خطأ في الحصول على معرف لوحة الأم: {e}")
        return "UNKNOWN_MB"
    
    @staticmethod
    def get_mac_address():
        """الحصول على عنوان MAC الأساسي"""
        try:
            mac = ":".join(["{:02x}".format((uuid.getnode() >> (i << 3)) & 0xff)
                           for i in range(6)][::-1])
            return mac
        except Exception as e:
            print(f"خطأ في الحصول على MAC: {e}")
        
        try:
            hostname = socket.gethostname()
            mac = socket.gethostbyname_ex(hostname)[2][0]
            return mac
        except Exception:
            pass
        
        return "UNKNOWN_MAC"
    
    @staticmethod
    def get_cpu_id():
        """الحصول على معرف المعالج"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["wmic", "cpu", "get", "processorid"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    return lines[1].strip()
            elif platform.system() == "Linux":
                try:
                    with open("/proc/cpuinfo", "r") as f:
                        for line in f:
                            if "Serial" in line:
                                return line.split(":")[-1].strip()
                except FileNotFoundError:
                    pass
            elif platform.system() == "Darwin":
                result = subprocess.run(
                    ["system_profiler", "SPHardwareDataType"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                for line in result.stdout.split('\n'):
                    if "Serial Number" in line:
                        return line.split(":")[-1].strip()
        except Exception as e:
            print(f"خطأ في الحصول على معرف المعالج: {e}")
        return "UNKNOWN_CPU"
    
    @classmethod
    def generate_hwid(cls):
        """توليد HWID من مكونات الجهاز"""
        mb_serial = cls.get_motherboard_serial()
        mac_addr = cls.get_mac_address()
        cpu_id = cls.get_cpu_id()
        
        # دمج البيانات
        combined = f"{mb_serial}|{mac_addr}|{cpu_id}"
        
        # تشفير باستخدام SHA256
        hwid = hashlib.sha256(combined.encode()).hexdigest()
        
        return hwid, {
            "motherboard": mb_serial,
            "mac": mac_addr,
            "cpu": cpu_id
        }
    
    @staticmethod
    def save_hwid(hwid_path="hwid.json"):
        """حفظ HWID في ملف"""
        hwid, components = HWIDGenerator.generate_hwid()
        
        data = {
            "hwid": hwid,
            "components": components,
            "platform": platform.system(),
            "version": "1.0"
        }
        
        with open(hwid_path, 'w') as f:
            json.dump(data, f, indent=4)
        
        return hwid
    
    @staticmethod
    def load_hwid(hwid_path="hwid.json"):
        """قراءة HWID من ملف"""
        if not Path(hwid_path).exists():
            return None
        
        with open(hwid_path, 'r') as f:
            data = json.load(f)
        
        return data.get("hwid")
