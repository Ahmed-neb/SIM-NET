"""
SIM-NET AI Engine
=================
محرك الذكاء الاصطناعي للتحليل والكشف عن المشاكل
"""

import re
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import Counter


class AIEngine:
    """محرك AI الرئيسي"""

    def __init__(self):
        self.problem_database = self._initialize_problem_database()

    def _initialize_problem_database(self) -> Dict:
        """
        قاعدة بيانات المشاكل والحلول - 20 مشكلة مع حلول مخصصة
        """
        return {
            # 1. Interface Down
            'interface_down': {
                'id': 1,
                'problem': 'Interface Down',
                'keywords': ['interface', 'down', 'link', 'port', 'سقط', 'مقفول', 'لا يعمل', 'ethernet', 'gigabit', 'fastethernet'],
                'solutions': [
                    '1. Check physical cable connections and LED indicators',
                    '2. Verify interface status with "show ip interface brief"',
                    '3. Try "shutdown" then "no shutdown" to restart interface',
                    '4. Check for errors with "show interfaces"',
                    '5. Verify duplex and speed settings match on both ends'
                ],
                'severity': 'Medium',
                'category': 'Physical Layer'
            },

            # 2. High CPU
            'high_cpu': {
                'id': 2,
                'problem': 'High CPU Utilization',
                'keywords': ['cpu', 'high', 'load', 'process', 'utilization', 'معالج', 'ثقيل', 'busy'],
                'solutions': [
                    '1. Identify high CPU processes with "show processes cpu"',
                    '2. Check for routing loops or broadcast storms',
                    '3. Verify no debug commands are running',
                    '4. Optimize routing table if too large',
                    '5. Consider hardware upgrade if consistently high'
                ],
                'severity': 'High',
                'category': 'Performance'
            },

            # 3. Slow Network
            'slow_network': {
                'id': 3,
                'problem': 'Slow Network Performance',
                'keywords': ['slow', 'latency', 'delay', 'speed', 'performance', 'بطيء', 'تأخير', 'سلوو', 'snail'],
                'solutions': [
                    '1. Check interface counters for errors or drops',
                    '2. Test latency with extended ping tests',
                    '3. Verify duplex and speed settings match',
                    '4. Check for bandwidth saturation during peak hours',
                    '5. Review QoS policies and traffic shaping'
                ],
                'severity': 'Medium',
                'category': 'Performance'
            },

            # 4. Connection Timeout
            'connection_timeout': {
                'id': 4,
                'problem': 'Connection Timeout',
                'keywords': ['connection', 'timeout', 'unreachable', 'اتصال', 'انقطاع', 'لا يستجيب', 'refused'],
                'solutions': [
                    '1. Check basic connectivity with ping and traceroute',
                    '2. Verify routing table has valid path to destination',
                    '3. Check ACLs and firewall rules blocking traffic',
                    '4. Verify NAT configuration if applicable',
                    '5. Check for asymmetric routing issues'
                ],
                'severity': 'Medium',
                'category': 'Connectivity'
            },

            # 5. Security Attack
            'security_attack': {
                'id': 5,
                'problem': 'Security Attack Detected',
                'keywords': ['attack', 'threat', 'intrusion', 'hack', 'اختراق', 'هجوم', 'فايروس', 'malware', 'suspicious'],
                'solutions': [
                    '1. Identify the source IP of the attack immediately',
                    '2. Apply emergency ACLs to block malicious traffic',
                    '3. Enable detailed logging for forensic investigation',
                    '4. Consider isolating affected network segment',
                    '5. Review and update security policies and signatures'
                ],
                'severity': 'High',
                'category': 'Security'
            },

            # 6. VLAN Issue
            'vlan_issue': {
                'id': 6,
                'problem': 'VLAN Configuration Issue',
                'keywords': ['vlan', 'tagging', 'trunk', 'access', 'فلان', 'تاغ', 'ترانك', 'native vlan'],
                'solutions': [
                    '1. Verify VLAN configuration with "show vlan brief"',
                    '2. Check trunk ports allow required VLANs',
                    '3. Verify access ports assigned to correct VLAN',
                    '4. Check native VLAN mismatch on trunk links',
                    '5. Verify VTP configuration if using VTP protocol'
                ],
                'severity': 'Medium',
                'category': 'Layer 2'
            },

            # 7. Routing Problem
            'routing_problem': {
                'id': 7,
                'problem': 'Routing Issue',
                'keywords': ['route', 'routing', 'path', 'gateway', 'next-hop', 'توجيه', 'راوت', 'جيتواي', 'hop'],
                'solutions': [
                    '1. Check routing table with "show ip route"',
                    '2. Verify routing protocol neighbors are established',
                    '3. Check for route flapping in system logs',
                    '4. Verify next-hop reachability',
                    '5. Check for blackholes or routing loops'
                ],
                'severity': 'High',
                'category': 'Layer 3'
            },

            # 8. DHCP Failure
            'dhcp_failure': {
                'id': 8,
                'problem': 'DHCP Not Working',
                'keywords': ['dhcp', 'ip address', 'lease', 'pool', 'ايبي', 'عنوان', 'تخصيص', 'dynamic', 'assigned'],
                'solutions': [
                    '1. Verify DHCP server is running and reachable',
                    '2. Check DHCP pool has available addresses',
                    '3. Verify DHCP relay configuration on routers',
                    '4. Check for rogue DHCP servers',
                    '5. Restart DHCP service and check for conflicts'
                ],
                'severity': 'Medium',
                'category': 'Services'
            },

            # 9. DNS Resolution
            'dns_resolution': {
                'id': 9,
                'problem': 'DNS Resolution Failure',
                'keywords': ['dns', 'resolve', 'name', 'domain', 'دومين', 'نيم', 'تحويل', 'nslookup', 'dig'],
                'solutions': [
                    '1. Check DNS server reachability with ping',
                    '2. Test resolution with nslookup or dig commands',
                    '3. Verify DNS server configuration on clients',
                    '4. Check firewall rules allowing DNS traffic',
                    '5. Clear DNS cache and check for stale records'
                ],
                'severity': 'Medium',
                'category': 'Services'
            },

            # 10. Bandwidth Saturation
            'bandwidth_saturation': {
                'id': 10,
                'problem': 'Bandwidth Saturation',
                'keywords': ['bandwidth', 'traffic', 'congestion', 'saturation', 'ازدحام', 'ترافيك', 'full', 'utilization'],
                'solutions': [
                    '1. Identify top bandwidth consumers with NetFlow',
                    '2. Implement QoS policies to prioritize traffic',
                    '3. Apply traffic shaping or policing',
                    '4. Consider bandwidth upgrade',
                    '5. Review application traffic patterns'
                ],
                'severity': 'Medium',
                'category': 'Performance'
            },

            # 11. STP Loop
            'stp_loop': {
                'id': 11,
                'problem': 'Spanning Tree Loop',
                'keywords': ['stp', 'spanning tree', 'loop', 'broadcast', 'storm', 'تكرار', 'عاصفة', 'bdpu'],
                'solutions': [
                    '1. Identify looping path with "show spanning-tree"',
                    '2. Enable BPDU guard on access ports',
                    '3. Check for redundant links without STP',
                    '4. Verify root bridge election',
                    '5. Enable loop guard and root guard'
                ],
                'severity': 'High',
                'category': 'Layer 2'
            },

            # 12. NAT Issue
            'nat_issue': {
                'id': 12,
                'problem': 'NAT Translation Failure',
                'keywords': ['nat', 'translation', 'inside', 'outside', 'overload', 'ترجمة', 'عنوان عام', 'pnat'],
                'solutions': [
                    '1. Check NAT translations with "show ip nat translations"',
                    '2. Verify ACL matches traffic to be translated',
                    '3. Ensure NAT pool has available addresses',
                    '4. Check for overlapping NAT rules',
                    '5. Verify inside/outside interface configuration'
                ],
                'severity': 'Medium',
                'category': 'Layer 3'
            },

            # 13. ACL Blocking
            'acl_blocking': {
                'id': 13,
                'problem': 'ACL Blocking Traffic',
                'keywords': ['acl', 'access list', 'block', 'deny', 'permit', 'فايرول', 'منع', 'filter', 'drop'],
                'solutions': [
                    '1. Review ACL with "show access-lists"',
                    '2. Check ACL hit counts',
                    '3. Verify ACL order (top-down)',
                    '4. Add explicit permit if needed',
                    '5. Use "log" keyword for debugging'
                ],
                'severity': 'Medium',
                'category': 'Security'
            },

            # 14. OSPF Neighbor
            'ospf_neighbor': {
                'id': 14,
                'problem': 'OSPF Neighbor Down',
                'keywords': ['ospf', 'neighbor', 'adjacency', 'down', 'او اس بي اف', 'جار', 'neighbor', 'full'],
                'solutions': [
                    '1. Verify OSPF enabled on interfaces',
                    '2. Check area ID matches',
                    '3. Verify hello/dead timers',
                    '4. Check passive interface config',
                    '5. Verify network type matches'
                ],
                'severity': 'High',
                'category': 'Routing'
            },

            # 15. BGP Down
            'bgp_down': {
                'id': 15,
                'problem': 'BGP Session Down',
                'keywords': ['bgp', 'peer', 'neighbor', 'session', 'idle', 'بي جي بي', 'بير', 'established'],
                'solutions': [
                    '1. Check BGP state with "show ip bgp summary"',
                    '2. Verify TCP port 179 not blocked',
                    '3. Check AS number configuration',
                    '4. Verify update source interface',
                    '5. Check MD5 authentication'
                ],
                'severity': 'High',
                'category': 'Routing'
            },

            # 16. High Memory
            'high_memory': {
                'id': 16,
                'problem': 'High Memory Usage',
                'keywords': ['memory', 'ram', 'out of memory', 'buffer', 'ذاكرة', 'ميموري', 'full', 'leak'],
                'solutions': [
                    '1. Check memory with "show memory statistics"',
                    '2. Identify memory-intensive processes',
                    '3. Check for memory leaks',
                    '4. Reduce BGP table size',
                    '5. Consider device upgrade'
                ],
                'severity': 'High',
                'category': 'Performance'
            },

            # 17. Port Security
            'port_security': {
                'id': 17,
                'problem': 'Port Security Violation',
                'keywords': ['port security', 'violation', 'mac address', 'sticky', 'بورت سيكيورتي', 'ماك', 'err-disabled'],
                'solutions': [
                    '1. Check violation mode',
                    '2. Verify allowed MAC addresses',
                    '3. Clear sticky MAC if needed',
                    '4. Increase max MAC if legitimate',
                    '5. Check for MAC flooding'
                ],
                'severity': 'Medium',
                'category': 'Security'
            },

            # 18. VPN Tunnel
            'vpn_tunnel': {
                'id': 18,
                'problem': 'VPN Tunnel Down',
                'keywords': ['vpn', 'tunnel', 'ipsec', 'gre', 'tunnel', 'تونل', 'في بي ان', 'phase', 'isakmp'],
                'solutions': [
                    '1. Check tunnel interface status',
                    '2. Verify interesting traffic',
                    '3. Check crypto map and ISAKMP',
                    '4. Verify peer reachability',
                    '5. Check NAT exemption'
                ],
                'severity': 'High',
                'category': 'VPN'
            },

            # 19. QoS Issue
            'qos_issue': {
                'id': 19,
                'problem': 'QoS Not Working',
                'keywords': ['qos', 'quality', 'service', 'priority', 'class', 'policy', 'كواليتي', 'أولوية', 'shape'],
                'solutions': [
                    '1. Verify QoS enabled on interface',
                    '2. Check policy-map applied',
                    '3. Verify traffic matches class-map',
                    '4. Check for queuing drops',
                    '5. Verify bandwidth statements'
                ],
                'severity': 'Medium',
                'category': 'QoS'
            },

            # 20. SNMP Monitoring
            'snmp_monitoring': {
                'id': 20,
                'problem': 'SNMP Monitoring Failure',
                'keywords': ['snmp', 'monitoring', 'trap', 'poll', 'community', 'مونيتورنج', 'تراب', 'oid'],
                'solutions': [
                    '1. Verify SNMP community strings',
                    '2. Check SNMP is enabled',
                    '3. Verify ACL allows SNMP',
                    '4. Check trap destination',
                    '5. Verify SNMP version'
                ],
                'severity': 'Low',
                'category': 'Management'
            }
        }

    def chatbot_assist(self, query: str, context: Dict = None) -> Dict:
        """
        مساعد Chatbot للمشاكل - يدعم 20 مشكلة مع حلول مخصصة
        """
        query_lower = query.lower()
        response = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'problem_detected': False,
            'solutions': [],
            'suggestions': [],
            'related_issues': [],
            'matched_problem': None,
            'severity': 'Low',
            'category': None,
            'match_score': 0
        }

        best_match = None
        best_score = 0

        for problem_id, problem_data in self.problem_database.items():
            score = 0

            # 1. مطابقة الكلمات المفتاحية (+1 لكل كلمة)
            for keyword in problem_data['keywords']:
                if keyword in query_lower:
                    score += 1

            # 2. مطابقة كلمات اسم المشكلة الطويلة (+2)
            problem_words = problem_data['problem'].lower().split()
            for word in problem_words:
                clean_word = ''.join(c for c in word if c.isalnum())
                if len(clean_word) > 3 and clean_word in query_lower:
                    score += 2

            # 3. مطابقة دقيقة (+5)
            if problem_data['problem'].lower() in query_lower:
                score += 5

            if score > best_score:
                best_score = score
                best_match = problem_id

        # عتبة التفعيل: >= 2 نقطة
        if best_match and best_score >= 2:
            problem_data = self.problem_database[best_match]
            response['problem_detected'] = True
            response['matched_problem'] = problem_data['problem']
            response['solutions'] = problem_data['solutions']
            response['severity'] = problem_data['severity']
            response['category'] = problem_data['category']
            response['match_score'] = best_score
            response['related_issues'] = self._get_related_problems(problem_data['category'], best_match)
        else:
            response['suggestions'] = [
                'يرجى تقديم المزيد من التفاصيل:',
                '- نوع الجهاز (Router/Switch)',
                '- رسائل الخطأ الظاهرة',
                '- متى بدأت المشكلة؟',
                '- أي تغييرات أجريت مؤخراً؟'
            ]

        return response

    def _get_related_problems(self, category: str, current_problem: str) -> List[str]:
        """الحصول على مشاكل ذات صلة"""
        related = []
        for problem_id, problem_data in self.problem_database.items():
            if problem_id != current_problem and problem_data['category'] == category:
                related.append(problem_data['problem'])
        return related[:3]

    def get_all_problems(self) -> List[Dict]:
        """الحصول على قائمة بجميع المشاكل"""
        return [
            {
                'id': data['id'],
                'problem': data['problem'],
                'severity': data['severity'],
                'category': data['category']
            }
            for problem_id, data in self.problem_database.items()
        ]

    def get_solutions(self, problem_type: str) -> List[Dict]:
        """الحصول على حلول لمشكلة معينة"""
        solutions = []
        for problem_id, problem_data in self.problem_database.items():
            if problem_type.lower() in problem_data['problem'].lower():
                solutions.append({
                    'problem': problem_data['problem'],
                    'solutions': problem_data['solutions'],
                    'severity': problem_data['severity'],
                    'category': problem_data['category']
                })
        return solutions

    def analyze_packet(self, packet_data: Dict) -> Dict:
        """
        تحليل Packet واحد
        """
        result = {
            'packet_id': packet_data.get('id', 0),
            'timestamp': datetime.now().isoformat(),
            'risk_level': 'Low',
            'threat_type': None,
            'analysis': 'Normal packet',
            'recommendations': [],
            'indicators': []
        }

        protocol = packet_data.get('protocol', '').upper()
        source_ip = packet_data.get('source_ip', '')
        dest_ip = packet_data.get('dest_ip', '')
        flags = packet_data.get('flags', '')

        # تحليل ARP
        if protocol == 'ARP':
            arp_op = packet_data.get('arp_opcode', 0)

            if source_ip == dest_ip and arp_op == 2:
                result['risk_level'] = 'Medium'
                result['threat_type'] = 'ARP Spoofing'
                result['analysis'] = 'Gratuitous ARP detected - possible spoofing attempt'
                result['recommendations'] = [
                    'Enable Dynamic ARP Inspection (DAI)',
                    'Configure ARP ACLs for critical devices',
                    'Enable DHCP snooping'
                ]
                result['indicators'].append('Gratuitous ARP')

            if packet_data.get('mac_mismatch'):
                result['risk_level'] = 'High'
                result['threat_type'] = 'ARP Spoofing'
                result['analysis'] = 'MAC address mismatch detected'
                result['indicators'].append('MAC Mismatch')

        # تحليل TCP
        elif protocol == 'TCP':
            if flags == 'S' and packet_data.get('incomplete_connection', False):
                result['risk_level'] = 'High'
                result['threat_type'] = 'SYN Flood'
                result['analysis'] = 'Incomplete TCP handshake - possible SYN flood'
                result['recommendations'] = [
                    'Enable TCP Intercept',
                    'Configure SYN cookies',
                    'Implement rate limiting'
                ]

        # تحليل ICMP
        elif protocol == 'ICMP':
            if packet_data.get('icmp_type', 0) == 8 and packet_data.get('high_volume', False):
                result['risk_level'] = 'Medium'
                result['threat_type'] = 'ICMP Flood'
                result['analysis'] = 'High volume of ICMP echo requests'

        # تحليل UDP
        elif protocol == 'UDP':
            if packet_data.get('dest_port', 0) == 53 and packet_data.get('large_response', False):
                result['risk_level'] = 'High'
                result['threat_type'] = 'DNS Amplification'
                result['analysis'] = 'Large DNS response - possible amplification attack'

        # Malformed packets
        if packet_data.get('malformed', False):
            result['risk_level'] = 'Medium'
            result['threat_type'] = 'Malformed Packet'
            result['analysis'] = 'Packet has invalid structure or checksum'

        return result

    def analyze_traffic(self, traffic_data: Dict) -> Dict:
        """
        تحليل Traffic Patterns
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'risk_level': 'Low',
            'traffic_volume': traffic_data.get('volume', 0),
            'bandwidth_usage': traffic_data.get('bandwidth_percent', 0),
            'analysis': 'Normal traffic pattern',
            'abnormal_patterns': [],
            'recommendations': [],
            'top_talkers': []
        }

        bandwidth = traffic_data.get('bandwidth_percent', 0)

        if bandwidth > 90:
            result['risk_level'] = 'High'
            result['abnormal_patterns'].append('Bandwidth saturation')
            result['analysis'] = 'Critical bandwidth utilization detected'
            result['recommendations'] = [
                'Implement QoS policies',
                'Identify top talkers',
                'Consider bandwidth upgrade'
            ]
        elif bandwidth > 70:
            result['risk_level'] = 'Medium'
            result['abnormal_patterns'].append('High bandwidth usage')

        # Broadcast storm detection
        if traffic_data.get('broadcast_percent', 0) > 10:
            result['risk_level'] = 'High'
            result['abnormal_patterns'].append('Broadcast storm detected')
            result['analysis'] = 'Excessive broadcast traffic - possible loop'

        return result

    def detect_anomalies(self, data_points: List[Dict]) -> List[Dict]:
        """
        اكتشاف الشذوذ في البيانات
        """
        if len(data_points) < 3:
            return []

        anomalies = []
        values = [dp.get('value', 0) for dp in data_points]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5

        for dp in data_points:
            value = dp.get('value', 0)
            z_score = abs(value - mean) / std_dev if std_dev > 0 else 0

            if z_score > 2:
                anomalies.append({
                    'timestamp': dp.get('timestamp'),
                    'value': value,
                    'expected_range': [mean - 2*std_dev, mean + 2*std_dev],
                    'z_score': z_score,
                    'severity': 'High' if z_score > 3 else 'Medium'
                })

        return anomalies


# ==================== دوال مساعدة ====================

def calculate_entropy(data: bytes) -> float:
    """حساب Entropy للبيانات"""
    if not data:
        return 0
    entropy = 0
    for x in range(256):
        p_x = float(data.count(bytes([x]))) / len(data)
        if p_x > 0:
            entropy += - p_x * (p_x).bit_length()
    return entropy


def is_encrypted_traffic(packet_data: Dict) -> bool:
    """التحقق من التشفير"""
    port = packet_data.get('dest_port', 0)
    encrypted_ports = [443, 22, 993, 995, 465, 587]
    return port in encrypted_ports