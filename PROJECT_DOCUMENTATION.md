# SIM-NET - توثيق المشروع

## 📖 نظرة عامة

**SIM-NET** هو نظام متكامل لإدارة ومراقبة الشبكات يجمع بين:
- مراقبة الأجهزة في الوقت الفعلي
- الأتمتة الذكية
- تحليل الأمان بالذكاء الاصطناعي
- التقارير والإحصائيات

## 🏗️ هيكل المشروع

```
SIM-NET/
├── backend/                    # الواجهة الخلفية (Flask)
│   ├── app.py                 # التطبيق الرئيسي
│   ├── config.py              # الإعدادات
│   └── __init__.py
│
├── frontend/                   # الواجهة الأمامية (HTML/CSS/JS)
│   ├── index.html             # الصفحة الرئيسية
│   ├── css/
│   │   └── style.css          # الأنماط
│   ├── js/
│   │   └── app.js             # التطبيق
│   └── images/
│
├── database/                   # قاعدة البيانات
│   ├── db_manager.py          # إدارة قاعدة البيانات
│   └── __init__.py
│
├── modules/                    # وحدات الأتمتة
│   ├── network_monitor.py     # مراقبة الشبكة
│   ├── router_automation.py   # أتمتة الراوتر
│   ├── security_automation.py # أتمتة الأمان
│   └── __init__.py
│
├── ai/                         # الذكاء الاصطناعي
│   ├── ai_engine.py           # محرك AI
│   └── __init__.py
│
├── backups/                    # النسخ الاحتياطية
├── reports/                    # التقارير
├── logs/                       # السجلات
│
├── requirements.txt            # متطلبات Python
├── launcher.py                 # ملف التشغيل السريع
├── Start.bat                   # تشغيل Windows
├── Start.sh                    # تشغيل Linux/Mac
├── README.md                   # دليل المستخدم
└── PROJECT_DOCUMENTATION.md    # هذا الملف
```

## 🔧 المكونات الرئيسية

### 1. Backend (Flask)

#### المسارات (Routes)

**المصادقة:**
- `POST /api/auth/login` - تسجيل الدخول
- `POST /api/auth/logout` - تسجيل الخروج
- `GET /api/auth/me` - المستخدم الحالي

**المستخدمين:**
- `GET /api/users` - قائمة المستخدمين
- `POST /api/users` - إضافة مستخدم

**الأجهزة:**
- `GET /api/devices` - قائمة الأجهزة
- `POST /api/devices` - إضافة جهاز
- `GET /api/devices/:id` - تفاصيل جهاز
- `DELETE /api/devices/:id` - حذف جهاز
- `POST /api/devices/:id/ping` - Ping جهاز

**المراقبة:**
- `GET /api/monitoring/dashboard` - بيانات Dashboard
- `GET /api/monitoring/performance` - بيانات الأداء
- `GET /api/monitoring/logs` - السجلات

**الأمان:**
- `GET /api/security/issues` - مشاكل الأمان
- `POST /api/security/issues` - إضافة مشكلة

**الـ AI:**
- `GET /api/ai/packet-analysis` - تحليل Packets
- `POST /api/ai/packet-analysis` - إنشاء تحليل
- `GET /api/ai/traffic-analysis` - تحليل Traffic
- `POST /api/ai/traffic-analysis` - إنشاء تحليل
- `GET /api/ai/knowledge-base` - قاعدة المعرفة
- `POST /api/ai/chatbot` - Chatbot

### 2. Database (SQLite)

#### الجداول

**users:**
- id, username, password, role, email, phone, created_at, last_login, is_active

**devices:**
- id, ip_address, hostname, device_type, vendor, os_version, username, password, enable_password, location, status, last_seen, created_at, created_by

**interfaces:**
- id, device_id, interface_name, status, protocol, ip_address, last_check

**tasks:**
- id, task_name, task_type, description, schedule_time, status, created_by, created_at, last_run

**task_runs:**
- id, task_id, device_id, status, output, error_message, executed_by, executed_at

**backups:**
- id, device_id, backup_type, file_path, file_size, config_content, performed_by, backup_date, notes

**logs:**
- id, event_type, event_category, description, user_id, device_id, severity, ip_address, details, created_at

**performance:**
- id, device_id, cpu_usage, memory_usage, disk_usage, latency, packet_loss, interface_stats, collected_at

**security_issues:**
- id, device_id, issue_type, severity, description, source_ip, target_ip, attack_type, status, solution, detected_at, resolved_at, resolved_by

**packet_analysis:**
- id, device_id, packet_data, risk_level, threat_type, source_ip, destination_ip, protocol, analysis_result, recommended_action, analyzed_at

**traffic_analysis:**
- id, device_id, traffic_volume, bandwidth_usage, abnormal_patterns, risk_level, source_analysis, recommendations, analyzed_at

**ai_knowledge_base:**
- id, problem_type, problem_description, solution_1, solution_2, solution_3, device_type, success_count, created_at

**alerts:**
- id, alert_type, severity, title, message, device_id, is_read, sent_email, sent_sms, created_at

### 3. Modules

#### Network Monitor
- `ping_device()` - Ping جهاز
- `telnet_connect()` - الاتصال عبر Telnet
- `get_device_info()` - معلومات الجهاز
- `get_interfaces_status()` - حالة Interfaces
- `get_cdp_neighbors()` - CDP Neighbors
- `restart_interface()` - إعادة تشغيل Interface

#### Router Automation
- `backup_config()` - نسخ احتياطي
- `restore_config()` - استعادة إعدادات
- `compare_with_golden()` - مقارنة مع Baseline
- `fix_config_drift()` - إصلاح الاختلافات
- `push_config()` - دفع إعدادات
- `create_vlan()` - إنشاء VLAN
- `create_acl()` - إنشاء ACL

#### Security Automation
- `analyze_security_config()` - تحليل إعدادات الأمان
- `detect_attacks_from_logs()` - اكتشاف الهجمات
- `calculate_risk_score()` - حساب درجة المخاطر
- `auto_respond_to_threat()` - الاستجابة التلقائية

### 4. AI Engine

#### Packet Analysis
- تحليل ARP (Spoofing detection)
- تحليل TCP (SYN Flood detection)
- تحليل ICMP (Flood detection)
- اكتشاف Packets المشوهة

#### Traffic Analysis
- Bandwidth usage analysis
- Anomaly detection
- Pattern recognition
- Top talkers identification

#### Chatbot
- فهم المشاكل الشائعة
- اقتراح حلول
- تقديم إرشادات

## 🎨 Frontend

### الصفحات

1. **Login Page**
   - نموذج تسجيل الدخول
   - معلومات الحسابات الافتراضية

2. **Dashboard**
   - إحصائيات سريعة
   - خريطة الأجهزة
   - آخر التنبيهات
   - آخر الأنشطة
   - رسوم بيانية

3. **Devices**
   - قائمة الأجهزة
   - إضافة/حذف/تعديل
   - Ping devices

4. **Monitoring**
   - حالة المراقبة
   - Interfaces status
   - CDP neighbors

5. **Security**
   - مشاكل الأمان
   - درجات المخاطر
   - التوصيات

6. **Performance**
   - رسوم بيانية للـ CPU/Memory
   - جدول بيانات الأداء

7. **AI Analysis**
   - Chatbot
   - تحليل Packets
   - تحليل Traffic

8. **Reports**
   - توليد تقارير
   - تصدير البيانات

9. **Logs**
   - سجلات النظام
   - تصفية حسب الخطورة

10. **Users** (Admin only)
    - إدارة المستخدمين
    - إضافة مستخدمين

## 🔐 الأمان

### المصادقة
- تسجيل الدخول بالاسم وكلمة المرور
- Session-based authentication
- Roles: Admin, Engineer, Viewer

### الصلاحيات
| الدور | الصلاحيات |
|-------|----------|
| Admin | جميع الصلاحيات |
| Engineer | إدارة الأجهزة، المراقبة، الأمان |
| Viewer | مشاهدة فقط |

### الحماية
- تشفير كلمات المرور (في الإنتاج)
- تسجيل جميع الأنشطة
- Rate limiting
- Session timeout

## 📊 الرسوم البيانية

### Chart.js
- Device Status (Doughnut)
- CPU Usage (Line)
- Memory Usage (Line)
- Traffic Analysis (Area)

### Leaflet Maps
- خريطة تفاعلية
- علامات للأجهزة
- Popup معلومات

## 🚀 طريقة التشغيل

### الطريقة 1: استخدام ملف التشغيل السريع

```bash
# Windows
python launcher.py

# أو
Start.bat

# Linux/Mac
python3 launcher.py

# أو
./Start.sh
```

### الطريقة 2: تشغيل يدوي

```bash
# 1. تثبيت المتطلبات
pip install -r requirements.txt

# 2. تهيئة قاعدة البيانات
python database/db_manager.py

# 3. تشغيل Backend
cd backend
python app.py

# 4. تشغيل Frontend (في Terminal آخر)
cd frontend
python -m http.server 8080

# 5. فتح المتصفح
http://localhost:8080
```

## 📝 سجل التغييرات

### الإصدار 1.0.0
- ✅ نظام مصادقة كامل
- ✅ إدارة الأجهزة
- ✅ مراقبة الشبكة
- ✅ أتمتة الراوتر/السويتش
- ✅ أتمتة الأمان
- ✅ محرك AI
- ✅ Chatbot
- ✅ تقارير وإحصائيات
- ✅ رسوم بيانية
- ✅ خرائط تفاعلية

## 🔮 التطويرات المستقبلية

### قريباً
- [ ] دعم SSH بالإضافة لـ Telnet
- [ ] NetFlow collection
- [ ] SNMP monitoring
- [ ] Email/SMS alerts
- [ ] Multi-language support

### مستقبلاً
- [ ] Docker deployment
- [ ] Kubernetes support
- [ ] REST API documentation (Swagger)
- [ ] Mobile app
- [ ] Cloud integration

## 👨‍💻 فريق التطوير

**المطورون:**
- Backend Developer
- Frontend Developer
- Network Engineer
- AI Specialist

## 📧 التواصل

- Email: support@simnet.local
- GitHub: github.com/simnet
- Documentation: docs.simnet.local

## 📄 الترخيص

MIT License - مفتوح المصدر

---

**تم التطوير بكل ❤️ لفريق SIM-NET**
