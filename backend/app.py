#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Fix UTF-8 encoding in Windows - Safe version for PyInstaller
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

"""
SIM-NET Desktop Application
============================
Desktop Application using Flask + PyWebView
With PNETLab Real Device Integration
"""

from flask import Flask, request, jsonify, session, send_file, send_from_directory
from flask_cors import CORS
from functools import wraps
import json
import subprocess
import threading
import time
import re
import telnetlib
import paramiko
import socket
from datetime import datetime, timedelta
from pathlib import Path
import webview
import atexit
import pickle
import requests
import urllib.request

app = Flask(__name__)
app.secret_key = 'simnet-ai-agent-secret-key-2024'

# CORS Configuration for Desktop Mode
CORS(app, supports_credentials=True, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-CSRF-Token"],
        "supports_credentials": True
    }
})

# ==================== DATA STORAGE ====================
DATA_FILE = 'simnet_data.pkl'
class DataStore:
    def __init__(self):
        self.users = [
            {'id': 1, 'username': 'admin', 'password': 'admin123', 'role': 'admin', 'email': 'admin@simnet.local'},
            {'id': 2, 'username': 'engineer', 'password': 'engineer123', 'role': 'engineer',
             'email': 'engineer@simnet.local'},
            {'id': 3, 'username': 'viewer', 'password': 'viewer123', 'role': 'viewer', 'email': 'viewer@simnet.local'}
        ]
        self.devices = []
        self.logs = []
        self.alerts = []
        self.performance_data = []
        self.security_issues = []
        self.connected_telnet_sessions = {}
        self.device_logs_buffer = {}
        self.settings = {}
        self.load_data()

    def save_data(self):
        """حفظ البيانات تلقائياً"""
        try:
            data = {
                'users': self.users,
                'devices': self.devices,
                'logs': self.logs,
                'alerts': self.alerts,
                'performance_data': self.performance_data,
                'security_issues': self.security_issues,
                'device_logs_buffer': self.device_logs_buffer,
                'settings': self.settings
            }
            with open(DATA_FILE, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_data(self):
        """تحميل البيانات المحفوظة"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'rb') as f:
                    data = pickle.load(f)
                self.users = data.get('users', self.users)
                self.devices = data.get('devices', [])
                self.logs = data.get('logs', [])
                self.alerts = data.get('alerts', [])
                self.performance_data = data.get('performance_data', [])
                self.security_issues = data.get('security_issues', [])
                self.device_logs_buffer = data.get('device_logs_buffer', {})
                self.settings = data.get('settings', {})
            except Exception as e:
                print(f"Error loading data: {e}")

    def add_log(self, event_type, description, user_id=None, device_id=None, severity='info', ip_address=None):
        log = {
            'id': len(self.logs) + 1,
            'event_type': event_type,
            'description': description,
            'user_id': user_id,
            'device_id': device_id,
            'severity': severity,
            'ip_address': ip_address,
            'created_at': datetime.now().isoformat()
        }
        self.logs.insert(0, log)
        self.save_data()
        return log

    def get_user_by_username(self, username):
        return next((u for u in self.users if u['username'] == username), None)

    def get_user_by_id(self, user_id):
        return next((u for u in self.users if u['id'] == user_id), None)

    def get_device_by_id(self, device_id):
        return next((d for d in self.devices if d['id'] == device_id), None)

    def get_device_by_ip(self, ip):
        return next((d for d in self.devices if d['ip_address'] == ip), None)


# Create instance
db = DataStore()
atexit.register(db.save_data)


# ==================== AUTH MIDDLEWARE ====================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)

    return decorated


def engineer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        user = db.get_user_by_id(session['user_id'])
        if not user or user['role'] not in ['admin', 'engineer']:
            return jsonify({'error': 'Engineer access required'}), 403
        return f(*args, **kwargs)

    return decorated


# ==================== REAL DEVICE CONNECTIONS ====================
active_connections = {}


class DeviceConnector:
    """Manage Telnet/SSH connections to real network devices"""

    @staticmethod
    def connect_telnet(ip, username, password, enable_password=''):
        """Connect to device via Telnet"""
        try:
            tn = telnetlib.Telnet(ip, port=23, timeout=10)

            # Login sequence
            tn.read_until(b"Username:", timeout=5)
            tn.write(username.encode() + b"\n")
            tn.read_until(b"Password:", timeout=5)
            tn.write(password.encode() + b"\n")

            time.sleep(1)
            output = tn.read_very_eager().decode('utf-8', errors='ignore')

            # Enter enable mode
            if '>' in output:
                tn.write(b"enable\n")
                if enable_password:
                    tn.read_until(b"Password:", timeout=3)
                    tn.write(enable_password.encode() + b"\n")
                else:
                    time.sleep(0.5)

            return {
                'success': True,
                'connection': tn,
                'type': 'telnet',
                'output': output
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def connect_ssh(ip, username, password, enable_password=''):
        """Connect to device via SSH"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password, timeout=10)

            shell = ssh.invoke_shell()
            time.sleep(1)
            output = shell.recv(65535).decode('utf-8', errors='ignore')

            # Enter enable mode
            if '>' in output:
                shell.send("enable\n")
                if enable_password:
                    time.sleep(0.5)
                    shell.send(enable_password + "\n")
                time.sleep(0.5)
                output += shell.recv(65535).decode('utf-8', errors='ignore')

            return {
                'success': True,
                'connection': ssh,
                'shell': shell,
                'type': 'ssh',
                'output': output
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def execute_command(session_id, command):
        """Execute single command on connected device"""
        if session_id not in active_connections:
            return {'success': False, 'error': 'Not connected'}

        try:
            conn = active_connections[session_id]

            if conn['type'] == 'telnet':
                tn = conn['connection']
                tn.write(command.encode() + b"\n")
                time.sleep(0.5)
                output = tn.read_very_eager().decode('utf-8', errors='ignore')
            else:
                shell = conn['shell']
                shell.send(command + "\n")
                time.sleep(0.5)
                output = shell.recv(65535).decode('utf-8', errors='ignore')

            return {'success': True, 'output': output}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def execute_batch(session_id, commands):
        """Execute multiple commands"""
        results = []

        for cmd in commands:
            if not cmd or cmd.strip() == '':
                continue

            result = DeviceConnector.execute_command(session_id, cmd)
            results.append({
                'command': cmd,
                'output': result.get('output', ''),
                'error': result.get('error', ''),
                'success': result['success']
            })
            time.sleep(0.3)

        return results

    @staticmethod
    def disconnect(session_id):
        """Close device connection"""
        if session_id in active_connections:
            conn = active_connections[session_id]
            try:
                if conn['type'] == 'telnet':
                    conn['connection'].close()
                else:
                    conn['connection'].close()
            except:
                pass
            del active_connections[session_id]
            return {'success': True}
        return {'success': False, 'error': 'Session not found'}


# ==================== AI ENGINE ====================
class AIAgent:
    def __init__(self):
        self.problem_database = self._init_problem_db()
        self.patterns = self._init_patterns()

    def _init_problem_db(self):
        return {
            'interface_down': {
                'keywords': ['interface', 'down', 'link', 'port', 'ethernet', 'gigabit'],
                'solutions': [
                    'Check physical connections and LEDs',
                    'Execute: show ip interface brief',
                    'Restart Interface: shutdown then no shutdown',
                    'Verify Duplex and Speed matching',
                    'Replace cables if damaged'
                ],
                'severity': 'High',
                'category': 'Physical'
            },
            'high_cpu': {
                'keywords': ['cpu', 'high', 'load', 'process', 'utilization'],
                'solutions': [
                    'Execute: show processes cpu sorted',
                    'Look for Routing Loops',
                    'Stop active Debug commands',
                    'Optimize routing table',
                    'Upgrade devices if problem persists'
                ],
                'severity': 'Critical',
                'category': 'Performance'
            },
            'high_memory': {
                'keywords': ['memory', 'ram', 'buffer', 'leak'],
                'solutions': [
                    'Execute: show memory statistics',
                    'Identify memory-consuming processes',
                    'Look for memory leaks',
                    'Reduce BGP table size',
                    'Upgrade device'
                ],
                'severity': 'Critical',
                'category': 'Performance'
            },
            'dhcp_failure': {
                'keywords': ['dhcp', 'ip address', 'lease', 'pool'],
                'solutions': [
                    'Verify DHCP server is working',
                    'Check available addresses in Pool',
                    'Verify DHCP Relay on routers',
                    'Look for unauthorized DHCP servers',
                    'Restart DHCP service'
                ],
                'severity': 'Medium',
                'category': 'Services'
            },
            'dns_failure': {
                'keywords': ['dns', 'resolve', 'name', 'domain'],
                'solutions': [
                    'Verify DNS server access with Ping',
                    'Test resolution with nslookup or dig',
                    'Check firewall rules',
                    'Clear DNS cache',
                    'Verify DNS settings on clients'
                ],
                'severity': 'Medium',
                'category': 'Services'
            },
            'ospf_down': {
                'keywords': ['ospf', 'neighbor', 'adjacency', 'routing'],
                'solutions': [
                    'Verify OSPF is enabled on Interfaces',
                    'Check Area ID matching',
                    'Verify Hello/Dead Timers matching',
                    'Review Passive Interface configuration',
                    'Check Network Type matching'
                ],
                'severity': 'High',
                'category': 'Routing'
            },
            'bgp_down': {
                'keywords': ['bgp', 'peer', 'session', 'established'],
                'solutions': [
                    'Execute: show ip bgp summary',
                    'Ensure TCP 179 is not blocked',
                    'Verify AS number',
                    'Review Update Source',
                    'Check MD5 authentication'
                ],
                'severity': 'High',
                'category': 'Routing'
            },
            'vpn_down': {
                'keywords': ['vpn', 'tunnel', 'ipsec', 'gre', 'isakmp'],
                'solutions': [
                    'Check Tunnel Interface status',
                    'Ensure interesting traffic exists',
                    'Review Crypto Map and ISAKMP',
                    'Verify peer reachability',
                    'Check NAT exemption for VPN'
                ],
                'severity': 'High',
                'category': 'VPN'
            },
            'nat_issue': {
                'keywords': ['nat', 'translation', 'inside', 'outside', 'overload'],
                'solutions': [
                    'Execute: show ip nat translations',
                    'Verify ACL matches traffic',
                    'Check available addresses in Pool',
                    'Look for overlapping NAT rules',
                    'Verify Inside/Outside configuration'
                ],
                'severity': 'Medium',
                'category': 'NAT'
            },
            'acl_blocking': {
                'keywords': ['acl', 'access-list', 'block', 'deny', 'filter'],
                'solutions': [
                    'Review ACL with show access-lists',
                    'Check Hit counters',
                    'Ensure ACL order (top to bottom)',
                    'Add explicit Permit statements',
                    'Use "log" for debugging'
                ],
                'severity': 'Medium',
                'category': 'Security'
            },
            'stp_loop': {
                'keywords': ['stp', 'spanning-tree', 'loop', 'broadcast', 'storm'],
                'solutions': [
                    'Identify loop path with show spanning-tree',
                    'Enable BPDU Guard on access ports',
                    'Check for redundant links',
                    'Review Root Bridge election',
                    'Enable Loop Guard and Root Guard'
                ],
                'severity': 'Critical',
                'category': 'Layer 2'
            },
            'vlan_issue': {
                'keywords': ['vlan', 'tagging', 'trunk', 'access', 'native'],
                'solutions': [
                    'Execute: show vlan brief',
                    'Verify VLANs allowed on Trunks',
                    'Check Access Ports VLAN assignment',
                    'Verify Native VLAN Mismatch',
                    'Review VTP configuration'
                ],
                'severity': 'Medium',
                'category': 'Layer 2'
            },
            'port_security': {
                'keywords': ['port security', 'violation', 'mac', 'sticky'],
                'solutions': [
                    'Check violation mode',
                    'Review allowed MAC addresses',
                    'Clear Sticky MAC if needed',
                    'Increase MAC maximum limit',
                    'Check for MAC Flooding attacks'
                ],
                'severity': 'Medium',
                'category': 'Security'
            },
            'slow_network': {
                'keywords': ['slow', 'latency', 'delay', 'bandwidth', 'congestion'],
                'solutions': [
                    'Check Interface errors',
                    'Test Latency with Ping',
                    'Review Bandwidth usage',
                    'Apply QoS policies',
                    'Check for Duplex Mismatch'
                ],
                'severity': 'Medium',
                'category': 'Performance'
            },
            'arp_spoofing': {
                'keywords': ['arp', 'spoofing', 'mac mismatch', 'gratuitous'],
                'solutions': [
                    'Enable Dynamic ARP Inspection (DAI)',
                    'Add static ARP entries',
                    'Enable DHCP Snooping',
                    'Use DAI Trust',
                    'Monitor ARP table for changes'
                ],
                'severity': 'High',
                'category': 'Security'
            }
        }

    def _init_patterns(self):
        return {
            'interface_error': re.compile(r'(\w+/\d+/\d+).*?(down|error|fail)', re.I),
            'cpu_high': re.compile(r'cpu.*?(\d{2,3})%', re.I),
            'memory_high': re.compile(r'memory.*?(\d{2,3})%', re.I),
            'link_up': re.compile(r'link.*?up', re.I),
            'link_down': re.compile(r'link.*?down', re.I),
            'ospf_neighbor': re.compile(r'ospf.*?(up|down|full)', re.I),
            'bgp_session': re.compile(r'bgp.*?(established|idle|active)', re.I),
            'dhcp_ack': re.compile(r'dhcp.*?(ack|offer|nak)', re.I),
            'error_log': re.compile(r'%(error|warning|critical)-\d+-\w+', re.I)
        }

    def predict_failures(self, device_data):
        predictions = []
        risk_score = 0

        cpu = device_data.get('cpu_usage', 0)
        if cpu > 90:
            predictions.append({
                'type': 'high_cpu',
                'probability': 0.9,
                'time_to_failure': 'Immediate',
                'impact': 'Device may become unresponsive',
                'recommended_action': 'Investigate high CPU processes immediately'
            })
            risk_score += 40
        elif cpu > 70:
            predictions.append({
                'type': 'high_cpu_warning',
                'probability': 0.6,
                'time_to_failure': '1-2 hours',
                'impact': 'Performance degradation',
                'recommended_action': 'Monitor and identify trending processes'
            })
            risk_score += 20

        memory = device_data.get('memory_usage', 0)
        if memory > 85:
            predictions.append({
                'type': 'high_memory',
                'probability': 0.8,
                'time_to_failure': '2-4 hours',
                'impact': 'Possible crashes or OOM kills',
                'recommended_action': 'Check for memory leaks'
            })
            risk_score += 30

        interfaces = device_data.get('interfaces', [])
        down_interfaces = [i for i in interfaces if i.get('status') == 'down']
        if len(down_interfaces) > len(interfaces) * 0.5:
            predictions.append({
                'type': 'multiple_interface_failure',
                'probability': 0.75,
                'time_to_failure': 'Immediate',
                'impact': 'Network segmentation',
                'recommended_action': 'Check for hardware failure or power issues'
            })
            risk_score += 35

        error_rate = device_data.get('error_rate', 0)
        if error_rate > 10:
            predictions.append({
                'type': 'high_error_rate',
                'probability': 0.7,
                'time_to_failure': 'Variable',
                'impact': 'Packet loss and retransmissions',
                'recommended_action': 'Check cable quality and interface settings'
            })
            risk_score += 15

        if risk_score >= 70:
            overall_risk = 'Critical'
        elif risk_score >= 40:
            overall_risk = 'High'
        elif risk_score >= 20:
            overall_risk = 'Medium'
        else:
            overall_risk = 'Low'

        return {
            'predictions': predictions,
            'risk_score': risk_score,
            'overall_risk': overall_risk,
            'analysis_time': datetime.now().isoformat()
        }

    def analyze_logs(self, logs, device_type='router'):
        analyzed = []
        patterns_found = []

        for log in logs:
            log_text = log.get('message', '')
            log_analysis = {
                'original': log_text,
                'timestamp': log.get('timestamp'),
                'severity': log.get('severity', 'info'),
                'meaning': '',
                'action_required': False,
                'related_problems': []
            }

            for pattern_name, pattern in self.patterns.items():
                if pattern.search(log_text):
                    patterns_found.append(pattern_name)

                    if pattern_name == 'interface_error':
                        match = pattern.search(log_text)
                        log_analysis['meaning'] = f"Interface {match.group(1)} is experiencing issues"
                        log_analysis['action_required'] = True
                        log_analysis['related_problems'].append('interface_down')

                    elif pattern_name == 'cpu_high':
                        match = pattern.search(log_text)
                        log_analysis['meaning'] = f"High CPU utilization detected: {match.group(1)}%"
                        log_analysis['action_required'] = True
                        log_analysis['related_problems'].append('high_cpu')

                    elif pattern_name == 'memory_high':
                        match = pattern.search(log_text)
                        log_analysis['meaning'] = f"High memory usage: {match.group(1)}%"
                        log_analysis['action_required'] = True
                        log_analysis['related_problems'].append('high_memory')

                    elif pattern_name == 'ospf_neighbor':
                        log_analysis['meaning'] = "OSPF neighbor state change detected"
                        log_analysis['action_required'] = True
                        log_analysis['related_problems'].append('ospf_down')

                    elif pattern_name == 'bgp_session':
                        log_analysis['meaning'] = "BGP session state change"
                        log_analysis['action_required'] = True
                        log_analysis['related_problems'].append('bgp_down')

            if not log_analysis['meaning']:
                log_analysis['meaning'] = self._interpret_generic_log(log_text, device_type)

            analyzed.append(log_analysis)

        severity_counts = {}
        for log in analyzed:
            sev = log['severity']
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        return {
            'analyzed_logs': analyzed,
            'patterns_detected': list(set(patterns_found)),
            'severity_summary': severity_counts,
            'critical_issues': [l for l in analyzed if l['action_required']],
            'recommendations': self._generate_log_recommendations(analyzed)
        }

    def _interpret_generic_log(self, log_text, device_type):
        interpretations = {
            'router': {
                'up': 'Interface or service came online',
                'down': 'Interface or service went offline',
                'configured': 'Configuration change applied',
                'authenticated': 'User or device authenticated successfully',
                'failed': 'Authentication or operation failed'
            },
            'switch': {
                'learned': 'MAC address learned on port',
                'aged': 'MAC address aged out',
                'flapped': 'Interface state changed rapidly (flapping)'
            }
        }

        device_dict = interpretations.get(device_type, interpretations['router'])

        for key, meaning in device_dict.items():
            if key in log_text.lower():
                return meaning

        return "System event logged - review for context"

    def _generate_log_recommendations(self, analyzed_logs):
        recommendations = []
        critical_count = len([l for l in analyzed_logs if l['severity'] == 'critical'])
        warning_count = len([l for l in analyzed_logs if l['severity'] == 'warning'])

        if critical_count > 5:
            recommendations.append("Multiple critical events detected - immediate investigation required")

        if warning_count > 10:
            recommendations.append("High number of warnings - review trending issues")

        problem_types = set()
        for log in analyzed_logs:
            problem_types.update(log.get('related_problems', []))

        for problem in problem_types:
            if problem in self.problem_database:
                recommendations.append(f"Address {self.problem_database[problem]['solutions'][0]}")

        return recommendations

    def filter_alerts(self, alerts, device_status):
        filtered = []
        suppressed = []

        for alert in alerts:
            alert_score = self._calculate_alert_importance(alert, device_status)

            should_suppress = False
            suppress_reason = ""

            similar_recent = [a for a in filtered if
                              a['type'] == alert['type'] and
                              (datetime.now() - datetime.fromisoformat(a['timestamp'])).seconds < 300]
            if len(similar_recent) > 2:
                should_suppress = True
                suppress_reason = "Similar alerts recently triggered"

            if alert.get('device_id') and device_status.get(alert['device_id']) == 'down':
                if alert['severity'] not in ['critical', 'high']:
                    should_suppress = True
                    suppress_reason = "Device already known to be down"

            if alert.get('maintenance_window'):
                should_suppress = True
                suppress_reason = "Within maintenance window"

            if alert['type'] in ['interface_down', 'link_flap']:
                related = [a for a in alerts if a['device_id'] == alert['device_id'] and a['type'] == alert['type']]
                if len(related) > 3:
                    alert['severity'] = 'critical'
                    alert['message'] += f" (Pattern: {len(related)} similar events)"

            if should_suppress:
                alert['suppressed'] = True
                alert['suppress_reason'] = suppress_reason
                suppressed.append(alert)
            else:
                alert['importance_score'] = alert_score
                filtered.append(alert)

        filtered.sort(key=lambda x: x.get('importance_score', 0), reverse=True)

        return {
            'active_alerts': filtered,
            'suppressed_count': len(suppressed),
            'suppressed_alerts': suppressed[:5],
            'filter_summary': {
                'total_received': len(alerts),
                'active_after_filter': len(filtered),
                'suppression_rate': len(suppressed) / len(alerts) if alerts else 0
            }
        }

    def _calculate_alert_importance(self, alert, device_status):
        score = 0

        severity_weights = {'critical': 100, 'high': 50, 'medium': 25, 'low': 10, 'info': 5}
        score += severity_weights.get(alert.get('severity', 'info'), 0)

        critical_types = ['firewall', 'core-router', 'distribution-switch']
        if alert.get('device_type') in critical_types:
            score += 30

        if device_status.get(alert.get('device_id')) == 'up':
            score += 20

        if alert.get('repeat_count', 0) > 5:
            score += 15

        return score

    def chatbot_assist(self, query, context=None):
        query_lower = query.lower()

        best_match = None
        best_score = 0

        for problem_id, problem_data in self.problem_database.items():
            score = 0
            for keyword in problem_data['keywords']:
                if keyword in query_lower:
                    score += 1

            problem_words = problem_data['keywords'][0].lower().split() if problem_data['keywords'] else []
            for word in problem_words:
                clean = ''.join(c for c in word if c.isalnum())
                if len(clean) > 3 and clean in query_lower:
                    score += 2

            if score > best_score:
                best_score = score
                best_match = problem_id

        if best_match and best_score >= 2:
            problem = self.problem_database[best_match]
            return {
                'problem_detected': True,
                'matched_problem': best_match,
                'severity': problem['severity'],
                'category': problem['category'],
                'solutions': problem['solutions'],
                'confidence': min(best_score * 10, 100)
            }
        else:
            return {
                'problem_detected': False,
                'suggestions': [
                    'Describe the problem in detail (Example: Interface Gig0/1 down)',
                    'Mention device type (Router/Switch/Firewall)',
                    'Mention error messages shown',
                    'Specify when the problem started'
                ]
            }


ai_agent = AIAgent()


# ==================== API ROUTES ====================

@app.route('/')
def index():
    return jsonify({
        'name': 'SIM-NET AI Agent API',
        'version': '2.0.0',
        'features': [
            'Real Device Telnet/SSH Control',
            'AI Failure Prediction',
            'Smart Alert Filtering',
            'Log Analysis',
            'Manual AI Engine'
        ],
        'status': 'running'
    })


# ==================== AUTH ROUTES ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = db.get_user_by_username(data.get('username'))

    if user and user['password'] == data.get('password'):
        if not user.get('is_active', True):
            return jsonify({'error': 'Account disabled'}), 403

        session['user_id'] = user['id']
        session['role'] = user['role']
        db.add_log('LOGIN', f"User {user['username']} logged in", user_id=user['id'])

        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'email': user.get('email')
            }
        })

    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    user_id = session.get('user_id')
    user = db.get_user_by_id(user_id)
    db.add_log('LOGOUT', f"User {user['username']} logged out", user_id=user_id)
    session.clear()
    db.save_data()
    return jsonify({'success': True})


# ==================== DEVICE ROUTES ====================

@app.route('/api/devices', methods=['GET'])
@login_required
def list_devices():
    return jsonify({'devices': db.devices})


@app.route('/api/devices', methods=['POST'])
@engineer_required
def create_device():
    data = request.get_json()

    if db.get_device_by_ip(data.get('ip_address')):
        return jsonify({'error': 'Device with this IP already exists'}), 409

    device_id = len(db.devices) + 1
    device = {
        'id': device_id,
        'ip_address': data.get('ip_address'),
        'hostname': data.get('hostname'),
        'device_type': data.get('device_type', 'Router'),
        'vendor': data.get('vendor', 'Unknown'),
        'username': data.get('username'),
        'password': data.get('password'),
        'location': data.get('location'),
        'status': 'unknown',
        'created_at': datetime.now().isoformat(),
        'created_by': session.get('user_id')
    }

    db.devices.append(device)
    db.add_log('DEVICE_ADDED', f"Device {device['hostname']} added",
               user_id=session.get('user_id'), device_id=device_id)

    return jsonify({'success': True, 'device_id': device_id})


@app.route('/api/devices/<int:device_id>', methods=['PUT'])
@engineer_required
def update_device(device_id):
    device = db.get_device_by_id(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404

    data = request.get_json()
    device.update({
        'hostname': data.get('hostname', device['hostname']),
        'ip_address': data.get('ip_address', device['ip_address']),
        'device_type': data.get('device_type', device['device_type']),
        'vendor': data.get('vendor', device['vendor']),
        'location': data.get('location', device.get('location')),
        'username': data.get('username', device.get('username')),
        'password': data.get('password', device.get('password')),
    })

    db.save_data()
    db.add_log('DEVICE_UPDATED', f"Device {device['hostname']} updated",
               user_id=session.get('user_id'), device_id=device_id)
    return jsonify({'success': True})


@app.route('/api/devices/<int:device_id>', methods=['DELETE'])
@engineer_required
def delete_device(device_id):
    device = db.get_device_by_id(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404

    db.devices = [d for d in db.devices if d['id'] != device_id]
    db.save_data()
    db.add_log('DEVICE_DELETED', f"Device {device['hostname']} deleted",
               user_id=session.get('user_id'))
    return jsonify({'success': True})


# ==================== REAL DEVICE CONTROL ROUTES ====================

@app.route('/api/device/connect', methods=['POST'])
@engineer_required
def connect_device():
    """Connect to real device via Telnet or SSH"""
    data = request.json
    ip = data.get('ip')
    username = data.get('username')
    password = data.get('password')
    enable_pass = data.get('enablePassword', '')
    protocol = data.get('protocol', 'telnet')
    session_id = data.get('sessionId', f"{ip}_{int(time.time())}")

    if protocol == 'telnet':
        result = DeviceConnector.connect_telnet(ip, username, password, enable_pass)
    else:
        result = DeviceConnector.connect_ssh(ip, username, password, enable_pass)

    if result['success']:
        active_connections[session_id] = {
            'type': result['type'],
            'connection': result['connection'],
            'shell': result.get('shell'),
            'ip': ip,
            'connected_at': time.time()
        }

        db.add_log('DEVICE_CONNECTED', f"Connected to {ip} via {protocol.upper()}",
                   user_id=session.get('user_id'), ip_address=ip)

        return jsonify({
            'success': True,
            'sessionId': session_id,
            'message': f'Connected to {ip} via {protocol.upper()}',
            'output': result['output']
        })

    return jsonify({
        'success': False,
        'error': result['error'],
        'message': f'Failed to connect: {result["error"]}'
    }), 500


@app.route('/api/device/execute', methods=['POST'])
@engineer_required
def execute_command():
    """Execute single command on connected device"""
    data = request.json
    session_id = data.get('sessionId')
    command = data.get('command')

    result = DeviceConnector.execute_command(session_id, command)

    if result['success']:
        return jsonify({
            'success': True,
            'command': command,
            'output': result['output'],
            'sessionId': session_id
        })

    return jsonify({
        'success': False,
        'error': result['error']
    }), 500


@app.route('/api/device/execute-batch', methods=['POST'])
@engineer_required
def execute_batch():
    """Execute multiple commands (for VLAN, Routing, etc)"""
    data = request.json
    session_id = data.get('sessionId')
    commands = data.get('commands', [])
    description = data.get('description', 'Configuration')

    if session_id not in active_connections:
        return jsonify({
            'success': False,
            'error': 'Not connected. Connect first.'
        }), 400

    results = DeviceConnector.execute_batch(session_id, commands)

    successful = sum(1 for r in results if r['success'])

    db.add_log('COMMANDS_EXECUTED', f"{description}: {successful}/{len(results)} commands successful",
               user_id=session.get('user_id'))

    return jsonify({
        'success': True,
        'description': description,
        'results': results,
        'sessionId': session_id,
        'totalCommands': len(results),
        'successful': successful
    })


@app.route('/api/device/disconnect', methods=['POST'])
@login_required
def disconnect_device():
    """Disconnect from device"""
    data = request.json
    session_id = data.get('sessionId')

    result = DeviceConnector.disconnect(session_id)

    if result['success']:
        db.add_log('DEVICE_DISCONNECTED', "Device disconnected",
                   user_id=session.get('user_id'))
        return jsonify({'success': True, 'message': 'Disconnected successfully'})

    return jsonify({'success': False, 'error': result['error']}), 404


@app.route('/api/device/status', methods=['GET'])
@login_required
def get_connection_status():
    """Check device connection status"""
    session_id = request.args.get('sessionId')

    if session_id and session_id in active_connections:
        conn = active_connections[session_id]
        return jsonify({
            'connected': True,
            'ip': conn['ip'],
            'type': conn['type'],
            'connectedAt': conn['connected_at'],
            'duration': time.time() - conn['connected_at']
        })

    return jsonify({
        'connected': False,
        'activeSessions': len(active_connections)
    })


# ==================== AI ROUTES ====================

@app.route('/api/ai/predict-failures', methods=['POST'])
@login_required
def predict_failures():
    data = request.get_json()
    device_data = {
        'cpu_usage': data.get('cpu_usage', 65),
        'memory_usage': data.get('memory_usage', 70),
        'interfaces': data.get('interfaces', []),
        'error_rate': data.get('error_rate', 5)
    }

    prediction = ai_agent.predict_failures(device_data)

    if prediction['overall_risk'] in ['Critical', 'High']:
        db.alerts.insert(0, {
            'id': len(db.alerts) + 1,
            'type': 'ai_prediction',
            'severity': prediction['overall_risk'].lower(),
            'title': f"AI Prediction: {prediction['predictions'][0]['type'] if prediction['predictions'] else 'Risk Detected'}",
            'message': f"Risk score: {prediction['risk_score']}/100",
            'device_id': data.get('device_id'),
            'timestamp': datetime.now().isoformat()
        })
        db.save_data()

    return jsonify({'success': True, 'prediction': prediction})


@app.route('/api/ai/analyze-logs', methods=['POST'])
@login_required
def analyze_logs():
    data = request.get_json()
    analysis = ai_agent.analyze_logs(data.get('logs', []), data.get('device_type', 'router'))
    return jsonify({'success': True, 'analysis': analysis})


@app.route('/api/ai/chatbot', methods=['POST'])
@login_required
def ai_chatbot():
    data = request.get_json()
    result = ai_agent.chatbot_assist(data.get('problem', ''), data.get('context', {}))

    if result['problem_detected']:
        db.add_log('AI_CHATBOT', f"Problem detected: {result['matched_problem']}",
                   user_id=session.get('user_id'), severity=result['severity'].lower())

    return jsonify({'success': True, 'result': result})


@app.route('/api/ai/problems', methods=['GET'])
@login_required
def list_ai_problems():
    problems = []
    for pid, pdata in ai_agent.problem_database.items():
        problems.append({
            'id': pid,
            'problem': pid.replace('_', ' ').title(),
            'severity': pdata['severity'],
            'category': pdata['category']
        })

    return jsonify({'success': True, 'count': len(problems), 'problems': problems})


# ==================== MONITORING ROUTES ====================

@app.route('/api/monitoring/dashboard', methods=['GET'])
@login_required
def dashboard():
    total = len(db.devices)
    online = len([d for d in db.devices if d.get('status') == 'up'])

    return jsonify({
        'stats': {
            'total_devices': total,
            'online_devices': online,
            'offline_devices': total - online,
            'unread_alerts': len([a for a in db.alerts if not a.get('is_read')]),
            'active_sessions': len(active_connections)
        },
        'devices': db.devices[:5],
        'alerts': db.alerts[:5],
        'logs': db.logs[:10]
    })


@app.route('/api/alerts', methods=['GET'])
@login_required
def get_alerts():
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    alerts = [a for a in db.alerts if not a.get('is_read')] if unread_only else db.alerts
    return jsonify({'alerts': alerts})


@app.route('/api/logs', methods=['GET'])
@login_required
def get_logs():
    limit = request.args.get('limit', 100, type=int)
    return jsonify({'logs': db.logs[:limit]})


# ==================== DESKTOP APP ====================

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def start_flask_server():
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)


def create_desktop_window():
    possible_paths = [
        get_resource_path('frontend/loading.html'),
        get_resource_path('loading.html'),
        os.path.join(os.path.dirname(__file__), '..', 'frontend', 'loading.html'),
        os.path.join(os.path.dirname(__file__), 'frontend', 'loading.html'),
    ]

    loading_path = None
    for path in possible_paths:
        if os.path.exists(path):
            loading_path = path
            break

    if not loading_path:
        for path in possible_paths:
            test_path = path.replace('loading.html', 'login.html')
            if os.path.exists(test_path):
                loading_path = test_path
                break

    if not loading_path:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"HTML files not found!")
        sys.exit(1)

    window = webview.create_window(
        title='SIM-NET AI Agent',
        url=f'file:///{loading_path.replace("//", "/")}',
        width=1280,
        height=720,
        min_size=(1280, 720),
        resizable=True,
        fullscreen=False,
        text_select=True,
        confirm_close=True
    )

    webview.start(debug=False)


if __name__ == '__main__':
    flask_thread = threading.Thread(target=start_flask_server, daemon=True)
    flask_thread.start()
    create_desktop_window()