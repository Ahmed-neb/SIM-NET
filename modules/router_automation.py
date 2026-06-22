"""
SIM-NET Router Automation Module
================================
وحدة أتمتة الراوتر والسويتش
"""

import telnetlib
import time
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class RouterAutomation:
    """فئة أتمتة الراوتر"""
    
    def __init__(self):
        self.golden_configs = {}  # تخزين التكوينات الذهبية
        self.command_history = []  # تاريخ الأوامر المنفذة
        
    def connect(self, ip: str, username: str, password: str, 
                enable_password: str = None, timeout: int = 10) -> Optional[telnetlib.Telnet]:
        """الاتصال بالجهاز عبر Telnet"""
        try:
            tn = telnetlib.Telnet(ip, 23, timeout=timeout)
            
            # تسجيل الدخول
            tn.read_until(b"Username:", timeout=5)
            tn.write(username.encode('ascii') + b"\n")
            
            tn.read_until(b"Password:", timeout=5)
            tn.write(password.encode('ascii') + b"\n")
            
            time.sleep(1)
            
            # Enable mode
            tn.write(b"enable\n")
            if enable_password:
                tn.read_until(b"Password:", timeout=5)
                tn.write(enable_password.encode('ascii') + b"\n")
            
            # تعطيل الـ Paging
            tn.write(b"terminal length 0\n")
            time.sleep(1)
            tn.read_very_eager()
            
            return tn
            
        except Exception as e:
            print(f"Connection failed: {e}")
            return None
    
    def execute_command(self, tn: telnetlib.Telnet, command: str, 
                        delay: float = 2) -> str:
        """تنفيذ أمر"""
        try:
            tn.write(command.encode('ascii') + b"\n")
            time.sleep(delay)
            output = tn.read_very_eager().decode('ascii', errors='ignore')
            
            # تسجيل الأمر في التاريخ
            self.command_history.append({
                'command': command,
                'timestamp': datetime.now().isoformat(),
                'output_length': len(output)
            })
            
            return output
        except Exception as e:
            return f"Error: {e}"
    
    def get_running_config(self, tn: telnetlib.Telnet) -> str:
        """الحصول على Running Configuration"""
        return self.execute_command(tn, "show running-config", delay=3)
    
    def get_startup_config(self, tn: telnetlib.Telnet) -> str:
        """الحصول على Startup Configuration"""
        return self.execute_command(tn, "show startup-config", delay=3)
    
    def backup_config(self, tn: telnetlib.Telnet, device_name: str, 
                      backup_dir: str = "backups") -> Dict:
        """
        إنشاء نسخة احتياطية من الإعدادات
        
        Returns:
            معلومات عن النسخة الاحتياطية
        """
        config = self.get_running_config(tn)
        
        # إنشاء اسم الملف
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{device_name}_{timestamp}.cfg"
        
        # إنشاء المجلد إذا لم يكن موجوداً
        backup_path = Path(backup_dir)
        backup_path.mkdir(exist_ok=True)
        
        # حفظ الملف
        file_path = backup_path / filename
        with open(file_path, 'w') as f:
            f.write(config)
        
        return {
            'success': True,
            'filename': filename,
            'filepath': str(file_path),
            'size': len(config),
            'timestamp': timestamp,
            'device': device_name
        }
    
    def restore_config(self, tn: telnetlib.Telnet, config_file: str) -> bool:
        """
        استعادة الإعدادات من ملف
        
        Args:
            tn: كائن Telnet
            config_file: مسار ملف الإعدادات
            
        Returns:
            True إذا نجحت العملية
        """
        try:
            with open(config_file, 'r') as f:
                config_lines = f.readlines()
            
            # الدخول في وضع التكوين
            self.execute_command(tn, "configure terminal", delay=1)
            
            # تطبيق الإعدادات
            for line in config_lines:
                line = line.strip()
                if line and not line.startswith('!') and not line.startswith('Building'):
                    self.execute_command(tn, line, delay=0.5)
            
            # حفظ الإعدادات
            self.execute_command(tn, "end", delay=1)
            self.execute_command(tn, "write memory", delay=2)
            
            return True
            
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
    
    def set_golden_config(self, device_id: str, config_lines: List[str]):
        """تعيين التكوين الذهبي للجهاز"""
        self.golden_configs[device_id] = config_lines
    
    def compare_with_golden(self, tn: telnetlib.Telnet, 
                            device_id: str) -> Dict:
        """
        مقارنة الإعدادات الحالية مع التكوين الذهبي
        
        Returns:
            نتائج المقارنة والاختلافات
        """
        if device_id not in self.golden_configs:
            return {
                'success': False,
                'error': 'Golden config not set for this device'
            }
        
        running_config = self.get_running_config(tn)
        running_lines = [line.strip() for line in running_config.splitlines()]
        golden_lines = self.golden_configs[device_id]
        
        # إيجاد الاختلافات
        missing_in_running = []
        for line in golden_lines:
            line = line.strip()
            if line and line not in running_lines:
                missing_in_running.append(line)
        
        return {
            'success': True,
            'device_id': device_id,
            'drift_detected': len(missing_in_running) > 0,
            'missing_lines': missing_in_running,
            'drift_count': len(missing_in_running),
            'timestamp': datetime.now().isoformat()
        }
    
    def fix_config_drift(self, tn: telnetlib.Telnet, device_id: str) -> Dict:
        """
        إصلاح اختلافات التكوين
        
        Returns:
            نتائج عملية الإصلاح
        """
        comparison = self.compare_with_golden(tn, device_id)
        
        if not comparison['success']:
            return comparison
        
        if not comparison['drift_detected']:
            return {
                'success': True,
                'message': 'No drift detected - configuration is compliant',
                'fixed_lines': []
            }
        
        # تطبيق الإعدادات المفقودة
        self.execute_command(tn, "configure terminal", delay=1)
        
        fixed_lines = []
        for line in comparison['missing_lines']:
            result = self.execute_command(tn, line, delay=0.5)
            fixed_lines.append({
                'command': line,
                'result': 'applied' if 'error' not in result.lower() else 'failed'
            })
        
        # حفظ الإعدادات
        self.execute_command(tn, "end", delay=1)
        self.execute_command(tn, "write memory", delay=2)
        
        return {
            'success': True,
            'message': f'Fixed {len(fixed_lines)} configuration drift items',
            'fixed_lines': fixed_lines,
            'timestamp': datetime.now().isoformat()
        }
    
    def push_config(self, tn: telnetlib.Telnet, config_lines: List[str]) -> Dict:
        """
        دفع إعدادات إلى الجهاز
        
        Args:
            tn: كائن Telnet
            config_lines: قائمة بأسطر الإعدادات
            
        Returns:
            نتائج العملية
        """
        results = []
        
        self.execute_command(tn, "configure terminal", delay=1)
        
        for line in config_lines:
            line = line.strip()
            if line and not line.startswith('!'):
                output = self.execute_command(tn, line, delay=0.5)
                results.append({
                    'command': line,
                    'success': 'error' not in output.lower() and 'invalid' not in output.lower(),
                    'output': output[:200]  # أول 200 حرف فقط
                })
        
        self.execute_command(tn, "end", delay=1)
        self.execute_command(tn, "write memory", delay=2)
        
        successful = sum(1 for r in results if r['success'])
        
        return {
            'success': successful == len(results),
            'total_commands': len(results),
            'successful': successful,
            'failed': len(results) - successful,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def execute_on_multiple(self, devices: List[Dict], command: str) -> List[Dict]:
        """
        تنفيذ أمر على عدة أجهزة
        
        Args:
            devices: قائمة الأجهزة
            command: الأمر المراد تنفيذه
            
        Returns:
            نتائج التنفيذ لكل جهاز
        """
        results = []
        
        for device in devices:
            tn = self.connect(
                device['ip'],
                device['username'],
                device['password'],
                device.get('enable_password')
            )
            
            if tn:
                output = self.execute_command(tn, command)
                results.append({
                    'device': device['ip'],
                    'success': True,
                    'output': output
                })
                tn.close()
            else:
                results.append({
                    'device': device['ip'],
                    'success': False,
                    'error': 'Connection failed'
                })
        
        return results
    
    def get_interface_stats(self, tn: telnetlib.Telnet) -> List[Dict]:
        """الحصول على إحصائيات Interfaces"""
        output = self.execute_command(tn, "show interfaces", delay=2)
        
        interfaces = []
        current_interface = None
        
        for line in output.splitlines():
            line = line.strip()
            
            # بداية Interface جديد
            if line and not line.startswith(' ') and 'is' in line:
                parts = line.split()
                if len(parts) >= 2:
                    current_interface = {
                        'name': parts[0],
                        'status': ' '.join(parts[1:3]) if len(parts) > 2 else 'unknown',
                        'input_packets': 0,
                        'output_packets': 0,
                        'input_errors': 0,
                        'output_errors': 0
                    }
            
            # إحصائيات
            if current_interface:
                if 'input packets' in line.lower():
                    match = re.search(r'(\d+) packets input', line, re.IGNORECASE)
                    if match:
                        current_interface['input_packets'] = int(match.group(1))
                
                elif 'output packets' in line.lower():
                    match = re.search(r'(\d+) packets output', line, re.IGNORECASE)
                    if match:
                        current_interface['output_packets'] = int(match.group(1))
                
                elif 'input errors' in line.lower():
                    match = re.search(r'(\d+) input errors', line, re.IGNORECASE)
                    if match:
                        current_interface['input_errors'] = int(match.group(1))
                
                elif 'output errors' in line.lower():
                    match = re.search(r'(\d+) output errors', line, re.IGNORECASE)
                    if match:
                        current_interface['output_errors'] = int(match.group(1))
                        interfaces.append(current_interface)
                        current_interface = None
        
        return interfaces
    
    def get_routing_table(self, tn: telnetlib.Telnet) -> List[Dict]:
        """الحصول على جدول التوجيه"""
        output = self.execute_command(tn, "show ip route", delay=2)
        
        routes = []
        for line in output.splitlines():
            line = line.strip()
            
            # تحليل سطر المسار
            if line and line[0].isupper() and 'via' in line:
                parts = line.split()
                if len(parts) >= 4:
                    route = {
                        'protocol': parts[0],
                        'network': parts[1] if len(parts) > 1 else 'unknown',
                        'admin_distance': '',
                        'metric': '',
                        'next_hop': '',
                        'interface': ''
                    }
                    
                    # استخراج المعلومات
                    for i, part in enumerate(parts):
                        if 'via' in part and i + 1 < len(parts):
                            route['next_hop'] = parts[i + 1].rstrip(',')
                        if 'metric' in part:
                            match = re.search(r'metric (\d+)', line)
                            if match:
                                route['metric'] = match.group(1)
                    
                    routes.append(route)
        
        return routes
    
    def create_vlan(self, tn: telnetlib.Telnet, vlan_id: int, 
                    vlan_name: str) -> bool:
        """إنشاء VLAN"""
        try:
            commands = [
                "configure terminal",
                f"vlan {vlan_id}",
                f"name {vlan_name}",
                "end",
                "write memory"
            ]
            
            for cmd in commands:
                self.execute_command(tn, cmd, delay=1)
            
            return True
        except Exception as e:
            print(f"VLAN creation failed: {e}")
            return False
    
    def assign_vlan_to_port(self, tn: telnetlib.Telnet, port: str, 
                            vlan_id: int) -> bool:
        """تخصيص VLAN لـ Port"""
        try:
            commands = [
                "configure terminal",
                f"interface {port}",
                "switchport mode access",
                f"switchport access vlan {vlan_id}",
                "no shutdown",
                "end",
                "write memory"
            ]
            
            for cmd in commands:
                self.execute_command(tn, cmd, delay=1)
            
            return True
        except Exception as e:
            print(f"VLAN assignment failed: {e}")
            return False
    
    def create_acl(self, tn: telnetlib.Telnet, acl_name: str, 
                   rules: List[str]) -> bool:
        """إنشاء Access Control List"""
        try:
            commands = ["configure terminal"]
            
            # تحديد نوع ACL
            if acl_name.isdigit():
                commands.append(f"access-list {acl_name}")
            else:
                commands.append(f"ip access-list extended {acl_name}")
            
            # إضافة القواعد
            for rule in rules:
                commands.append(rule)
            
            commands.extend(["end", "write memory"])
            
            for cmd in commands:
                self.execute_command(tn, cmd, delay=0.5)
            
            return True
        except Exception as e:
            print(f"ACL creation failed: {e}")
            return False
    
    def apply_acl(self, tn: telnetlib.Telnet, acl_name: str, 
                  interface: str, direction: str = "in") -> bool:
        """تطبيق ACL على Interface"""
        try:
            commands = [
                "configure terminal",
                f"interface {interface}",
                f"ip access-group {acl_name} {direction}",
                "end",
                "write memory"
            ]
            
            for cmd in commands:
                self.execute_command(tn, cmd, delay=1)
            
            return True
        except Exception as e:
            print(f"ACL application failed: {e}")
            return False


# ==================== دوال مساعدة ====================

def generate_interface_range(start_port: int, end_port: int, 
                              prefix: str = "FastEthernet0/") -> str:
    """توليد نطاق Interfaces"""
    return f"{prefix}{start_port} - {end_port}"

def parse_config_file(filepath: str) -> List[str]:
    """تحليل ملف إعدادات"""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # تنظيف الأسطر
    cleaned = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('!') and not line.startswith('Building'):
            cleaned.append(line)
    
    return cleaned


# ==================== اختبار ====================

if __name__ == '__main__':
    automation = RouterAutomation()
    print("Router Automation Module Ready")
    print("Available methods:", [m for m in dir(automation) if not m.startswith('_')])
