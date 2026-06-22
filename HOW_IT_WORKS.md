# كيف يعمل SIM-NET؟

## 🎯 نظرة عامة

**SIM-NET** يعمل كمنصة متكاملة لإدارة الشبكات من خلال:

```
┌─────────────────────────────────────────────────────────┐
│                    المستخدم (Browser)                    │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP Requests
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Frontend (HTML/CSS/JS)                      │
│  - Dashboard  - Devices  - Monitoring  - AI Chatbot     │
└────────────────────┬────────────────────────────────────┘
                     │ API Calls (Fetch/AJAX)
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Backend (Flask Python)                      │
│  - Authentication  - API Endpoints  - Business Logic    │
└────────────────────┬────────────────────────────────────┘
                     │ SQL Queries
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Database (SQLite)                           │
│  - Users  - Devices  - Logs  - Performance Data         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 تدفق البيانات

### 1. تسجيل الدخول

```
المستخدم يدخل بياناته
        ↓
Frontend يرسل POST /api/auth/login
        ↓
Backend يتحقق من البيانات
        ↓
Database يبحث عن المستخدم
        ↓
Backend يرسل JWT/Session Token
        ↓
Frontend يخزن Token ويعرض Dashboard
```

### 2. إضافة جهاز

```
المستخدم يدخل بيانات الجهاز
        ↓
Frontend يرسل POST /api/devices
        ↓
Backend يتحقق من البيانات
        ↓
Database يضيف الجهاز
        ↓
Backend يرسل تأكيد
        ↓
Frontend يعرض الجهاز في القائمة
```

### 3. مراقبة الجهاز

```
المستخدم يضغط Ping
        ↓
Frontend يرسل POST /api/devices/:id/ping
        ↓
Backend ينفذ Ping (subprocess)
        ↓
Backend يحلل النتيجة
        ↓
Database يحدث حالة الجهاز
        ↓
Backend يرسل النتيجة
        ↓
Frontend يعرض النتيجة
```

---

## 🏗️ المكونات

### Frontend (الواجهة الأمامية)

**التقنيات:**
- HTML5 - هيكل الصفحات
- CSS3 - التصميم والأنماط
- JavaScript - التفاعل والمنطق
- Chart.js - الرسوم البيانية
- Leaflet - الخرائط

**الملفات الرئيسية:**
- `index.html` - الصفحة الرئيسية
- `css/style.css` - الأنماط
- `js/app.js` - التطبيق

**كيف يعمل:**
1. يتم تحميل HTML عند فتح المتصفح
2. CSS يطبق الأنماط والتصميم
3. JavaScript يضيف التفاعل
4. يتم إرسال طلبات للـ Backend
5. يتم عرض البيانات المستلمة

### Backend (الواجهة الخلفية)

**التقنيات:**
- Flask - إطار عمل الويب
- SQLite - قاعدة البيانات
- Python - لغة البرمجة

**الملفات الرئيسية:**
- `app.py` - التطبيق الرئيسي
- `config.py` - الإعدادات

**كيف يعمل:**
1. Flask يستقبل الطلبات
2. يتحقق من المصادقة
3. ينفذ المنطق المطلوب
4. يتصل بقاعدة البيانات
5. يرسل الرد

### Database (قاعدة البيانات)

**التقنيات:**
- SQLite - قاعدة بيانات خفيفة

**الجداول الرئيسية:**
- `users` - المستخدمين
- `devices` - الأجهزة
- `logs` - السجلات
- `performance` - بيانات الأداء

**كيف تعمل:**
1. تخزن البيانات في ملف `.db`
2. SQL للاستعلام والتعديل
3. ORM للتعامل مع البيانات

---

## 🤖 مميزات AI

### 1. Packet Analysis

```
Packet يصل للنظام
        ↓
AI يحلل المحتوى
        ↓
يبحث عن أنماط مشبوهة
        ↓
يصنف مستوى الخطورة
        ↓
يقترح حلول
        ↓
يخزن النتيجة
```

**أمثلة:**
- ARP Spoofing → High Risk
- SYN Flood → High Risk
- Normal Traffic → Low Risk

### 2. Traffic Analysis

```
بيانات Traffic تصل
        ↓
AI يقارن مع Baseline
        ↓
يبحث عن شذوذ
        ↓
يصنف المخاطر
        ↓
يقترح إجراءات
```

**أمثلة:**
- Bandwidth > 90% → High Risk
- Traffic Spike → Medium Risk
- Normal Pattern → Low Risk

### 3. Chatbot

```
المستخدم يكتب مشكلة
        ↓
Chatbot يحلل النص
        ↓
يبحث في Knowledge Base
        ↓
يجد أفضل تطابق
        ↓
يرسل حلول مقترحة
```

**أمثلة:**
- "interface down" → حلول Interface
- "high cpu" → حلول CPU
- "slow network" → حلول Network

---

## 📡 Network Automation

### Telnet Connection

```python
# 1. الاتصال بالجهاز
tn = telnetlib.Telnet(ip, 23)

# 2. تسجيل الدخول
tn.write(b"username\n")
tn.write(b"password\n")

# 3. تنفيذ أوامر
tn.write(b"show version\n")
output = tn.read_very_eager()

# 4. معالجة النتائج
parse_output(output)
```

### Ping Device

```python
# 1. تنفيذ Ping
result = subprocess.run(['ping', '-n', '4', ip])

# 2. تحليل النتيجة
if result.returncode == 0:
    device.status = 'up'
else:
    device.status = 'down'

# 3. تحديث قاعدة البيانات
update_device_status(device_id, device.status)
```

### Self-Healing

```python
# 1. اكتشاف Interface Down
if interface.status == 'down':
    
    # 2. محاولة الإصلاح
    restart_interface(tn, interface.name)
    
    # 3. التحقق من الإصلاح
    new_status = check_interface(tn, interface.name)
    
    # 4. تسجيل النتيجة
    if new_status == 'up':
        log_event('Self-healing successful')
    else:
        log_event('Self-healing failed')
```

---

## 🔐 الأمان

### Authentication Flow

```
المستخدم يدخل بياناته
        ↓
Backend يتحقق من:
  - Username موجود؟
  - Password صحيح؟
  - الحساب نشط؟
        ↓
إذا نجح:
  - إنشاء Session
  - تسجيل الدخول
  - إعادة Token
        ↓
إذا فشل:
  - رفض الدخول
  - تسجيل المحاولة
```

### Role-Based Access

```
طلب يصل
        ↓
التحقق من الدور:
  - Admin → جميع الصلاحيات
  - Engineer → إدارة الأجهزة
  - Viewer → مشاهدة فقط
        ↓
السماح أو الرفض
```

---

## 📊 التقارير

### توليد تقرير

```
المستخدم يطلب تقرير
        ↓
جمع البيانات:
  - إحصائيات الأجهزة
  - السجلات
  - مشاكل الأمان
  - بيانات الأداء
        ↓
تنسيق البيانات
        ↓
إنشاء الملف
        ↓
إرسال للتحميل
```

---

## 🎨 Charts & Maps

### Chart.js

```javascript
// 1. إنشاء Canvas
<canvas id="myChart"></canvas>

// 2. إعداد البيانات
const data = {
    labels: ['Online', 'Offline'],
    datasets: [{
        data: [10, 2],
        backgroundColor: ['green', 'red']
    }]
};

// 3. إنشاء الرسم
new Chart(ctx, {
    type: 'doughnut',
    data: data
});
```

### Leaflet Map

```javascript
// 1. إنشاء الخريطة
const map = L.map('map').setView([24.7136, 46.6753], 5);

// 2. إضافة الطبقة
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')
 .addTo(map);

// 3. إضافة علامات
L.marker([lat, lng])
 .addTo(map)
 .bindPopup('Device Info');
```

---

## 🔄 Real-time Updates

### Polling (الطريقة المستخدمة)

```javascript
// كل 10 ثواني
setInterval(() => {
    fetch('/api/monitoring/dashboard')
        .then(response => response.json())
        .then(data => updateUI(data));
}, 10000);
```

### WebSockets (مستقبلاً)

```javascript
// الاتصال بالـ WebSocket
const ws = new WebSocket('ws://localhost:5000/ws');

// استقبال الرسائل
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateUI(data);
};
```

---

## 💾 Data Storage

### SQLite

```
┌─────────────────────────────────────┐
│           network.db                │
├─────────────────────────────────────┤
│  users                              │
│  ├── id, username, password, role   │
│                                     │
│  devices                            │
│  ├── id, ip, hostname, type, status │
│                                     │
│  logs                               │
│  ├── id, event, description, time   │
│                                     │
│  performance                        │
│  ├── id, device_id, cpu, memory     │
└─────────────────────────────────────┘
```

---

## 🚀 Performance

### تحسينات الأداء

1. **Lazy Loading**
   - تحميل البيانات عند الحاجة
   - عدم تحميل كل الصفحات مرة واحدة

2. **Caching**
   - تخزين البيانات مؤقتاً
   - تقليل الطلبات للـ Backend

3. **Pagination**
   - تقسيم البيانات الكبيرة
   - تحمين جزء في كل مرة

---

## 🔧 Extensibility

### إضافة ميزة جديدة

1. **Backend:**
   - إضافة Route جديد
   - إضافة منطق العمل
   - إضافة للـ Database

2. **Frontend:**
   - إضافة صفحة جديدة
   - إضافة زر في القائمة
   - ربط مع الـ API

3. **Database:**
   - إضافة جدول جديد
   - تحديث db_manager.py

---

## 📈 Monitoring

### ما يتم مراقبته:

- ✅ حالة الأجهزة (Up/Down)
- ✅ استخدام CPU/Memory
- ✅ Interfaces Status
- ✅ Bandwidth Usage
- ✅ Security Events
- ✅ Errors & Warnings

### كيفية المراقبة:

1. **Ping:** كل X دقائق
2. **Telnet:** عند الطلب
3. **Logs:** في الوقت الفعلي
4. **Performance:** كل ساعة

---

## 🎯 Summary

**SIM-NET** يعمل من خلال:

1. **Frontend** يعرض الواجهة ويتفاعل مع المستخدم
2. **Backend** يعالج الطلبات وينفذ المنطق
3. **Database** يخزن البيانات
4. **AI** يحلل ويكتشف المشاكل
5. **Automation** ينفذ المهام تلقائياً

**النتيجة:** نظام متكامل لإدارة الشبكات بكفاءة وسهولة!

---

**هل تحتاج مساعدة؟ راجع README.md أو USER_GUIDE.md**
