"""
SIM-NET Network Monitoring Module
=================================
وحدة مراقبة الشبكة والأجهزة
"""

import subprocess
import telnetlib
import time
import re
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class NetworkMonitor:
    """فئة مراقبة الشبكة"""
    
    def __init__(self):
        self.baseline_interfaces = {}
        self.monitoring_active = False
        self.monitor_thread = None
        
    def ping_device(self, ip: str, count: int = 4) -> Dict:
        """
        Ping جهاز للتحقق من توفره
        
        Args:
            ip: عنوان IP للجهاز
            count: عدد محاولات الـ Ping
            
        Returns:
            قاموس يحتوي على نتائج الـ Ping
        """
        try:
            result = subprocess.run(
                ['ping', '-n', str(count), ip],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0
            output = result.stdout
            
            # استخراج إحصائيات
            stats = {
                'sent': count,
                'received': 0,
                'lost': 0,
                'loss_percent': 100,
                'avg_time': 0
            }
            
            if success:
                # استخراج عدد الردود
                received_match = re.search(r'Received = (\d+)', output)
                if received_match:
                    stats['received'] = int(received_match.group(1))
                    stats['lost'] = count - stats['received']
                    stats['loss_percent'] = (stats['lost'] / count) * 100
                
                # استخراج متوسط الوقت
                avg_match = re.search(r'Average = (\d+)ms', output)
                if avg_match:
                    stats['avg_time'] = int(avg_match.group(1))
            
            return {
                'success': success,
                'ip': ip,
                'timestamp': datetime.now().isoformat(),
                'stats': stats,
                'output': output
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'ip': ip,
                'timestamp': datetime.now().isoformat(),
                'error': 'Ping timeout',
                'stats': {'sent': count, 'received': 0, 'lost': count, 'loss_percent': 100, 'avg_time': 0}
            }
        except Exception as e:
            return {
                'success': False,
                'ip': ip,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'stats': {'sent': count, 'received': 0, 'lost': count, 'loss_percent': 100, 'avg_time': 0}
            }
    
    def telnet_connect(self, ip: str, username: str, password: str, 
                       enable_password: str = None, timeout: int = 10) -> Optional[telnetlib.Telnet]:
        """
        الاتصال بجهاز عبر Telnet
        
        Args:
            ip: عنوان IP
            username: اسم المستخدم
            password: كلمة المرور
            enable_password: كلمة مرور Enable (اختياري)
            timeout: مهلة الاتصال
            
        Returns:
            كائن Telnet أو None في حالة الفشل
        """
        try:
            tn = telnetlib.Telnet(ip, 23, timeout=timeout)
            
            # انتظار Username
            tn.read_until(b"Username:", timeout=5)
            tn.write(username.encode('ascii') + b"\n")
            
            # انتظار Password
            tn.read_until(b"Password:", timeout=5)
            tn.write(password.encode('ascii') + b"\n")
            
            time.sleep(1)
            
            # الدخول في وضع Enable
            tn.write(b"enable\n")
            if enable_password:
                tn.read_until(b"Password:", timeout=5)
                tn.write(enable_password.encode('ascii') + b"\n")
            else:
                tn.write(password.encode('ascii') + b"\n")
            
            time.sleep(1)
            tn.read_very_eager()
            
            return tn
            
        except Exception as e:
            print(f"Telnet connection failed to {ip}: {e}")
            return None
    
    def execute_command(self, tn: telnetlib.Telnet, command: str, 
                        delay: float = 2) -> str:
        """
        تنفيذ أمر على جهاز عبر Telnet
        
        Args:
            tn: كائن Telnet
            command: الأمر المراد تنفيذه
            delay: تأخير الانتظار
            
        Returns:
            ناتج الأمر
        """
        try:
            tn.write(command.encode('ascii') + b"\n")
            time.sleep(delay)
            output = tn.read_very_eager().decode('ascii', errors='ignore')
            return output
        except Exception as e:
            return f"Error executing command: {e}"
    
    def get_device_info(self, tn: telnetlib.Telnet) -> Dict:
        """
        الحصول على معلومات الجهاز
        
        Args:
            tn: كائن Telnet
            
        Returns:
            قاموس يحتوي على معلومات الجهاز
        """
        output = self.execute_command(tn, "show version")
        
        info = {
            'vendor': 'Unknown',
            'device_type': 'Unknown',
            'os_version': 'Unknown',
            'hostname': 'Unknown',
            'uptime': 'Unknown'
        }
        
        for line in output.splitlines():
            line = line.strip()
            
            # Cisco IOS
            if "Cisco IOS Software" in line:
                info['vendor'] = 'Cisco'
                if "Version" in line:
                    match = re.search(r'Version ([^,]+)', line)
                    if match:
                        info['os_version'] = match.group(1).strip()
            
            # Hostname
            if line.startswith("hostname"):
                info['hostname'] = line.split()[-1]
            
            # Uptime
            if "uptime" in line.lower():
                match = re.search(r'uptime is (.+)', line, re.IGNORECASE)
                if match:
                    info['uptime'] = match.group(1)
            
            # Device Type
            if "cisco" in line.lower() and "processor" in line.lower():
                match = re.search(r'cisco (\S+)', line, re.IGNORECASE)
                if match:
                    info['device_type'] = match.group(1)
        
        return info
    
    def get_interfaces_status(self, tn: telnetlib.Telnet) -> List[Dict]:
        """
        الحصول على حالة Interfaces
        
        Args:
            tn: كائن Telnet
            
        Returns:
            قائمة بـ Interfaces وحالتها
        """
        output = self.execute_command(tn, "show ip interface brief")
        interfaces = []
        
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 5 and parts[0][0].isalpha():
                interface = {
                    'name': parts[0],
                    'ip': parts[1] if len(parts) > 1 else 'unassigned',
                    'status': parts[4] if len(parts) > 4 else 'unknown',
                    'protocol': parts[5] if len(parts) > 5 else 'unknown'
                }
                interfaces.append(interface)
        
        return interfaces
    
    def get_cdp_neighbors(self, tn: telnetlib.Telnet) -> List[Dict]:
        """
        الحصول على CDP Neighbors
        
        Args:
            tn: كائن Telnet
            
        Returns:
            قائمة بالأجهزة المجاورة
        """
        output = self.execute_command(tn, "show cdp neighbors")
        neighbors = []
        
        lines = output.splitlines()
        for i, line in enumerate(lines):
            if len(line.split()) >= 4 and not line.startswith('Device'):
                parts = line.split()
                if len(parts) >= 4:
                    neighbor = {
                        'device_id': parts[0],
                        'local_interface': parts[1] if len(parts) > 1 else 'unknown',
                        'holdtime': parts[2] if len(parts) > 2 else 'unknown',
                        'capability': parts[3] if len(parts) > 3 else 'unknown',
                        'platform': parts[4] if len(parts) > 4 else 'unknown',
                        'port_id': parts[5] if len(parts) > 5 else 'unknown'
                    }
                    neighbors.append(neighbor)
        
        return neighbors
    
    def check_interface_changes(self, device_id: int, interfaces: List[Dict]) -> List[Dict]:
        """
        التحقق من تغييرات Interfaces مقارنة بالـ Baseline
        
        Args:
            device_id: معرف الجهاز
            interfaces: قائمة Interfaces الحالية
            
        Returns:
            قائمة بالتغييرات المكتشفة
        """
        changes = []
        
        if device_id not in self.baseline_interfaces:
            self.baseline_interfaces[device_id] = {}
        
        for interface in interfaces:
            name = interface['name']
            current_status = interface['status']
            
            if name in self.baseline_interfaces[device_id]:
                old_status = self.baseline_interfaces[device_id][name]
                if old_status != current_status:
                    changes.append({
                        'interface': name,
                        'old_status': old_status,
                        'new_status': current_status,
                        'timestamp': datetime.now().isoformat()
                    })
            
            self.baseline_interfaces[device_id][name] = current_status
        
        return changes
    
    def classify_issue(self, status: str) -> str:
        """
        تصنيف مشكلة بناءً على الحالة
        
        Args:
            status: حالة Interface
            
        Returns:
            مستوى الخطورة
        """
        status_lower = status.lower()
        
        if status_lower == "down":
            return "Critical"
        elif status_lower in ["administratively down", "err-disabled"]:
            return "Medium"
        elif status_lower == "up":
            return "Normal"
        else:
            return "Low"
    
    def restart_interface(self, tn: telnetlib.Telnet, interface: str) -> bool:
        """
        إعادة تشغيل Interface (Self-Healing)
        
        Args:
            tn: كائن Telnet
            interface: اسم Interface
            
        Returns:
            True إذا نجحت العملية
        """
        try:
            self.execute_command(tn, "configure terminal", delay=1)
            self.execute_command(tn, f"interface {interface}", delay=1)
            self.execute_command(tn, "shutdown", delay=2)
            self.execute_command(tn, "no shutdown", delay=2)
            self.execute_command(tn, "end", delay=1)
            return True
        except Exception as e:
            print(f"Error restarting interface {interface}: {e}")
            return False
    
    def monitor_device(self, ip: str, username: str, password: str,
                       enable_password: str = None) -> Dict:
        """
        مراقبة جهاز كامل
        
        Args:
            ip: عنوان IP
            username: اسم المستخدم
            password: كلمة المرور
            enable_password: كلمة مرور Enable
            
        Returns:
            قاموس يحتوي على نتائج المراقبة
        """
        result = {
            'ip': ip,
            'timestamp': datetime.now().isoformat(),
            'ping': None,
            'telnet': None,
            'device_info': None,
            'interfaces': None,
            'cdp_neighbors': None,
            'changes': [],
            'issues': []
        }
        
        # Ping
        ping_result = self.ping_device(ip)
        result['ping'] = ping_result
        
        if not ping_result['success']:
            result['status'] = 'down'
            return result
        
        # Telnet
        tn = self.telnet_connect(ip, username, password, enable_password)
        if not tn:
            result['status'] = 'telnet_failed'
            return result
        
        result['telnet'] = {'success': True}
        
        # معلومات الجهاز
        device_info = self.get_device_info(tn)
        result['device_info'] = device_info
        
        # Interfaces
        interfaces = self.get_interfaces_status(tn)
        result['interfaces'] = interfaces
        
        # التحقق من التغييرات
        device_id = hash(ip)  # استخدام hash كـ ID مؤقت
        changes = self.check_interface_changes(device_id, interfaces)
        result['changes'] = changes
        
        # تصنيف المشاكل
        for interface in interfaces:
            severity = self.classify_issue(interface['status'])
            if severity in ['Critical', 'Medium']:
                result['issues'].append({
                    'interface': interface['name'],
                    'status': interface['status'],
                    'severity': severity
                })
                
                # Self-Healing: إعادة تشغيل Interface إذا كان Down
                if severity == 'Critical' and interface['status'].lower() == 'down':
                    restart_success = self.restart_interface(tn, interface['name'])
                    if restart_success:
                        result['self_healing'] = {
                            'interface': interface['name'],
                            'action': 'restarted',
                            'timestamp': datetime.now().isoformat()
                        }
        
        # CDP Neighbors
        cdp_neighbors = self.get_cdp_neighbors(tn)
        result['cdp_neighbors'] = cdp_neighbors
        
        result['status'] = 'up'
        
        tn.close()
        return result
    
    def start_continuous_monitoring(self, devices: List[Dict], 
                                    interval: int = 300,
                                    callback=None):
        """
        بدء المراقبة المستمرة
        
        Args:
            devices: قائمة الأجهزة للمراقبة
            interval: الفاصل الزمني بالثواني
            callback: دالة callback عند اكتمال كل دورة
        """
        self.monitoring_active = True
        
        def monitor_loop():
            while self.monitoring_active:
                results = []
                for device in devices:
                    result = self.monitor_device(
                        device['ip'],
                        device.get('username', ''),
                        device.get('password', ''),
                        device.get('enable_password')
                    )
                    results.append(result)
                
                if callback:
                    callback(results)
                
                time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_continuous_monitoring(self):
        """إيقاف المراقبة المستمرة"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)


# ==================== دوال مساعدة ====================

def quick_ping(ip: str) -> bool:
    """Ping سريع للتحقق من توفر الجهاز"""
    try:
        result = subprocess.run(
            ['ping', '-n', '1', ip],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def get_latency(ip: str) -> float:
    """الحصول على latency للجهاز"""
    try:
        result = subprocess.run(
            ['ping', '-n', '4', ip],
            capture_output=True,
            text=True,
            timeout=20
        )
        
        # استخراج متوسط الوقت
        match = re.search(r'Average = (\d+)ms', result.stdout)
        if match:
            return float(match.group(1))
        return -1
    except:
        return -1


# ==================== اختبار ====================

if __name__ == '__main__':
    monitor = NetworkMonitor()
    
    # اختبار Ping
    print("Testing ping to 8.8.8.8...")
    result = monitor.ping_device('8.8.8.8')
    print(f"Success: {result['success']}")
    print(f"Stats: {result['stats']}")
