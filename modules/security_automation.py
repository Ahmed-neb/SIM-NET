"""
SIM-NET Security Automation Module
==================================
وحدة أتمتة الأمان والحماية
"""

import re
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class SecurityAutomation:
    """فئة أتمتة الأمان"""
    
    def __init__(self):
        self.threat_database = {
            'port_scan': {
                'name': 'Port Scanning',
                'severity': 'medium',
                'description': 'Reconnaissance activity detected - possible port scan',
                'solutions': [
                    'Enable port security on switch ports',
                    'Configure IPS to detect and block scans',
                    'Enable storm control for broadcast traffic'
                ]
            },
            'brute_force': {
                'name': 'Brute Force Login',
                'severity': 'high',
                'description': 'Multiple failed login attempts detected',
                'solutions': [
                    'Enable login block-for command',
                    'Implement strong password policy',
                    'Enable two-factor authentication'
                ]
            },
            'dos_attack': {
                'name': 'DoS Attack',
                'severity': 'critical',
                'description': 'Denial of Service attack detected',
                'solutions': [
                    'Enable rate limiting on interfaces',
                    'Configure ACL to block attack source',
                    'Enable TCP intercept'
                ]
            },
            'arp_spoofing': {
                'name': 'ARP Spoofing',
                'severity': 'high',
                'description': 'ARP spoofing/poisoning detected',
                'solutions': [
                    'Enable Dynamic ARP Inspection (DAI)',
                    'Configure static ARP entries',
                    'Enable ARP inspection trust on legitimate ports'
                ]
            },
            'unauthorized_access': {
                'name': 'Unauthorized Access',
                'severity': 'high',
                'description': 'Unauthorized access attempt detected',
                'solutions': [
                    'Review and tighten ACL configurations',
                    'Enable AAA authentication',
                    'Implement network access control (NAC)'
                ]
            },
            'malicious_traffic': {
                'name': 'Malicious Traffic',
                'severity': 'high',
                'description': 'Traffic patterns indicate malicious activity',
                'solutions': [
                    'Enable NetFlow for traffic analysis',
                    'Configure IPS/IDS signatures',
                    'Implement traffic filtering'
                ]
            }
        }
    
    def analyze_security_config(self, config: str) -> Dict:
        """
        تحليل إعدادات الأمان
        
        Args:
            config: نص إعدادات الجهاز
            
        Returns:
            نتائج التحليل والمشاكل المكتشفة
        """
        issues = []
        score = 100
        
        # التحقق من تشفير كلمات المرور
        if 'service password-encryption' not in config.lower():
            issues.append({
                'type': 'weak_encryption',
                'severity': 'high',
                'description': 'Password encryption is not enabled',
                'recommendation': 'Enable "service password-encryption"'
            })
            score -= 15
        
        # التحقق من HTTP Server
        if 'no ip http server' not in config.lower():
            issues.append({
                'type': 'insecure_service',
                'severity': 'medium',
                'description': 'HTTP server is enabled (insecure)',
                'recommendation': 'Disable with "no ip http server"'
            })
            score -= 10
        
        # التحقق من HTTPS Server
        if 'no ip http secure-server' not in config.lower():
            issues.append({
                'type': 'insecure_service',
                'severity': 'low',
                'description': 'HTTPS server is enabled',
                'recommendation': 'Disable if not needed'
            })
            score -= 5
        
        # التحقق من Login Block
        if 'login block-for' not in config.lower():
            issues.append({
                'type': 'missing_protection',
                'severity': 'medium',
                'description': 'Login block protection not configured',
                'recommendation': 'Enable "login block-for" to prevent brute force'
            })
            score -= 10
        
        # التحقق من Console Password
        if 'line con 0' in config.lower():
            if 'password' not in config.lower().split('line con 0')[1].split('line')[0]:
                issues.append({
                    'type': 'missing_password',
                    'severity': 'critical',
                    'description': 'Console line has no password',
                    'recommendation': 'Set password on console line'
                })
                score -= 20
        
        # التحقق من VTY Password
        if 'line vty' in config.lower():
            vty_section = config.lower().split('line vty')[1].split('line')[0]
            if 'password' not in vty_section and 'login local' not in vty_section:
                issues.append({
                    'type': 'missing_password',
                    'severity': 'critical',
                    'description': 'VTY lines have no password protection',
                    'recommendation': 'Set password or enable local login on VTY lines'
                })
                score -= 20
        
        # التحقق من SNMP
        if 'snmp-server community' in config.lower():
            if 'public' in config.lower() or 'private' in config.lower():
                issues.append({
                    'type': 'weak_snmp',
                    'severity': 'high',
                    'description': 'SNMP community using default names (public/private)',
                    'recommendation': 'Change to strong community strings'
                })
                score -= 15
        
        # التحقق من Telnet
        if 'transport input telnet' in config.lower():
            issues.append({
                'type': 'insecure_protocol',
                'severity': 'medium',
                'description': 'Telnet is enabled (unencrypted)',
                'recommendation': 'Use SSH instead of Telnet'
            })
            score -= 10
        
        # تحديد مستوى الخطورة الإجمالي
        if score >= 80:
            overall_level = 'Good'
        elif score >= 60:
            overall_level = 'Fair'
        elif score >= 40:
            overall_level = 'Poor'
        else:
            overall_level = 'Critical'
        
        return {
            'security_score': max(0, score),
            'overall_level': overall_level,
            'issues_found': len(issues),
            'issues': issues,
            'timestamp': datetime.now().isoformat()
        }
    
    def detect_attacks_from_logs(self, log_data: str) -> List[Dict]:
        """
        اكتشاف الهجمات من Logs
        
        Args:
            log_data: نص الـ Logs
            
        Returns:
            قائمة بالهجمات المكتشفة
        """
        attacks = []
        
        # أنماط الهجمات
        patterns = {
            'brute_force': [
                r'failed login',
                r'authentication failure',
                r'invalid username'
            ],
            'port_scan': [
                r'reseted by peer',
                r'connection attempt',
                r'scan detected'
            ],
            'dos_attack': [
                r'rate limit exceeded',
                r'high connection rate',
                r'possible dos'
            ]
        }
        
        for attack_type, patterns_list in patterns.items():
            for pattern in patterns_list:
                matches = re.findall(pattern, log_data, re.IGNORECASE)
                if len(matches) > 5:  # أكثر من 5 تطابقات
                    threat_info = self.threat_database.get(attack_type, {})
                    attacks.append({
                        'type': attack_type,
                        'name': threat_info.get('name', attack_type),
                        'severity': threat_info.get('severity', 'medium'),
                        'occurrences': len(matches),
                        'description': threat_info.get('description', 'Unknown threat'),
                        'solutions': threat_info.get('solutions', [])
                    })
                    break  # تجنب التكرار
        
        return attacks
    
    def calculate_risk_score(self, device_data: Dict) -> Dict:
        """
        حساب درجة المخاطر
        
        Args:
            device_data: بيانات الجهاز
            
        Returns:
            درجة المخاطر والتصنيف
        """
        score = 0
        factors = []
        
        # المنافذ المفتوحة
        open_ports = device_data.get('open_ports', 0)
        if open_ports > 10:
            score += min(open_ports * 2, 30)
            factors.append(f'High number of open ports ({open_ports})')
        
        # كلمات المرور الضعيفة
        weak_passwords = device_data.get('weak_passwords', 0)
        score += weak_passwords * 10
        if weak_passwords > 0:
            factors.append(f'{weak_passwords} weak passwords detected')
        
        # الهجمات
        attacks = device_data.get('attacks_detected', 0)
        score += attacks * 15
        if attacks > 0:
            factors.append(f'{attacks} attacks detected')
        
        # الإعدادات غير الآمنة
        misconfig = device_data.get('misconfigurations', 0)
        score += misconfig * 5
        if misconfig > 0:
            factors.append(f'{misconfig} security misconfigurations')
        
        # التصنيف
        if score < 30:
            level = 'Low'
            color = 'green'
        elif score < 60:
            level = 'Medium'
            color = 'yellow'
        elif score < 80:
            level = 'High'
            color = 'orange'
        else:
            level = 'Critical'
            color = 'red'
        
        return {
            'risk_score': min(score, 100),
            'risk_level': level,
            'color': color,
            'factors': factors,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_security_recommendations(self, config_analysis: Dict) -> List[str]:
        """توليد توصيات الأمان"""
        recommendations = []
        
        for issue in config_analysis.get('issues', []):
            recommendations.append(issue['recommendation'])
        
        # توصيات عامة
        general_recommendations = [
            'Regularly update IOS/software to latest version',
            'Enable logging and send to syslog server',
            'Implement network segmentation with VLANs',
            'Enable SNMPv3 instead of SNMPv2c',
            'Configure secure management access (SSH only)',
            'Implement ACLs for management plane protection',
            'Enable Control Plane Policing (CoPP)',
            'Regular security audits and penetration testing'
        ]
        
        recommendations.extend(general_recommendations)
        
        return list(set(recommendations))  # إزالة التكرار
    
    def simulate_attack_detection(self) -> Dict:
        """محاكاة اكتشاف هجوم (للاختبار)"""
        attack_types = list(self.threat_database.keys())
        detected = random.sample(attack_types, random.randint(0, 3))
        
        attacks = []
        for attack_type in detected:
            threat = self.threat_database[attack_type]
            attacks.append({
                'type': attack_type,
                'name': threat['name'],
                'severity': threat['severity'],
                'description': threat['description'],
                'source_ip': f"192.168.1.{random.randint(2, 254)}",
                'target_ip': f"10.0.0.{random.randint(1, 10)}",
                'timestamp': datetime.now().isoformat(),
                'solutions': threat['solutions']
            })
        
        return {
            'attacks_detected': len(attacks),
            'attacks': attacks,
            'timestamp': datetime.now().isoformat()
        }
    
    def auto_respond_to_threat(self, threat_type: str, 
                               source_ip: str = None) -> Dict:
        """
        الاستجابة التلقائية للتهديد
        
        Args:
            threat_type: نوع التهديد
            source_ip: IP المصدر (اختياري)
            
        Returns:
            نتائج الاستجابة
        """
        actions = []
        
        if threat_type == 'brute_force':
            actions = [
                'Enable login block-for 120 attempts 3 within 60',
                'Add source IP to watch list',
                'Alert security team'
            ]
        
        elif threat_type == 'port_scan':
            actions = [
                'Enable port security on affected ports',
                'Rate limit ICMP traffic',
                'Log all connection attempts'
            ]
        
        elif threat_type == 'dos_attack':
            actions = [
                'Enable rate limiting on interfaces',
                'Block source IP if identified',
                'Activate TCP intercept',
                'Notify network operations center'
            ]
        
        elif threat_type == 'arp_spoofing':
            actions = [
                'Enable Dynamic ARP Inspection',
                'Configure ARP ACLs',
                'Isolate affected segment'
            ]
        
        else:
            actions = [
                'Log incident for investigation',
                'Increase monitoring frequency',
                'Alert security team'
            ]
        
        return {
            'threat_type': threat_type,
            'auto_response_triggered': True,
            'actions_taken': actions,
            'source_ip_blocked': source_ip is not None,
            'timestamp': datetime.now().isoformat()
        }
    
    def check_acl_effectiveness(self, acl_config: str) -> Dict:
        """التحقق من فعالية ACL"""
        issues = []
        
        # التحقق من وجود قواعد
        rules = [line for line in acl_config.splitlines() if line.strip() and not line.startswith('!')]
        
        if len(rules) < 2:
            issues.append({
                'type': 'insufficient_rules',
                'severity': 'medium',
                'description': 'ACL has very few rules - may not provide adequate protection'
            })
        
        # التحقق من وجود deny any any
        if 'deny' not in acl_config.lower() or 'deny ip any any' not in acl_config.lower():
            issues.append({
                'type': 'missing_default_deny',
                'severity': 'high',
                'description': 'ACL missing explicit deny statement at the end'
            })
        
        # التحقق من الترتيب
        permit_any = False
        for line in rules:
            if 'permit ip any any' in line.lower():
                permit_any = True
            elif permit_any and 'deny' in line.lower():
                issues.append({
                    'type': 'rule_order',
                    'severity': 'high',
                    'description': 'Deny rules after "permit any" will never be matched'
                })
                break
        
        return {
            'total_rules': len(rules),
            'issues_found': len(issues),
            'issues': issues,
            'recommendation': 'Review and optimize ACL configuration'
        }


# ==================== دوال مساعدة ====================

def validate_ip_address(ip: str) -> bool:
    """التحقق من صحة عنوان IP"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    
    octets = ip.split('.')
    for octet in octets:
        if int(octet) > 255:
            return False
    
    return True

def is_private_ip(ip: str) -> bool:
    """التحقق مما إذا كان IP خاصاً"""
    private_ranges = [
        ('10.0.0.0', '10.255.255.255'),
        ('172.16.0.0', '172.31.255.255'),
        ('192.168.0.0', '192.168.255.255')
    ]
    
    # تحويل IP إلى رقم
    def ip_to_num(ip):
        octets = [int(x) for x in ip.split('.')]
        return (octets[0] << 24) + (octets[1] << 16) + (octets[2] << 8) + octets[3]
    
    ip_num = ip_to_num(ip)
    
    for start, end in private_ranges:
        if ip_to_num(start) <= ip_num <= ip_to_num(end):
            return True
    
    return False


# ==================== اختبار ====================

if __name__ == '__main__':
    security = SecurityAutomation()
    
    # اختبار محاكاة اكتشاف الهجمات
    print("Simulating attack detection...")
    result = security.simulate_attack_detection()
    print(f"Attacks detected: {result['attacks_detected']}")
    for attack in result['attacks']:
        print(f"  - {attack['name']} ({attack['severity']})")
