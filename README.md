# SIM-NET - نظام إدارة الشبكات الذكي

![SIM-NET Logo](frontend/images/logo.png)

## 📋 نظرة عامة

**SIM-NET** هو نظام متكامل لإدارة ومراقبة الشبكات يوفر:
- مراقبة الأجهزة في الوقت الفعلي
- أتمتة المهام والإعدادات
- تحليل الأمان بالذكاء الاصطناعي
- تقارير وإحصائيات شاملة

## ✨ المميزات الرئيسية

### 1. إدارة الأجهزة
- إضافة وإدارة Routers, Switches, Servers, Firewalls
- Ping تلقائي للأجهزة
- اكتشاف الأجهزة عبر CDP
- مراقبة Interfaces

### 2. المراقبة والأتمتة
- مراقبة مستمرة للأجهزة
- Self-Healing (إعادة تشغيل Interfaces تلقائياً)
- مقارنة مع Baseline
- تنبيهات فورية

### 3. الأمان
- فحص إعدادات الأمان
- اكتشاف الهجمات
- إدارة ACLs
- تقارير المخاطر

### 4. الذكاء الاصطناعي
- تحليل Packets
- تحليل Traffic Patterns
- Chatbot للمساعدة
- قاعدة معرفة للمشاكل والحلول

### 5. التقارير
- تقارير يومية/أسبوعية/شهرية
- رسوم بيانية تفاعلية
- خرائط للأجهزة
- تصدير JSON/Excel

## 🚀 طريقة التشغيل

### المتطلبات
- Python 3.8 أو أحدث
- متصفح حديث (Chrome, Firefox, Edge)

### 1. تثبيت المتطلبات

```bash
# الانتقال لمجلد المشروع
cd SIM-NET

# تثبيت متطلبات Python
pip install -r requirements.txt
```

### 2. تشغيل قاعدة البيانات

```bash
# تهيئة قاعدة البيانات
cd database
python db_manager.py
cd ..
```

### 3. تشغيل الخادم الخلفي (Backend)

```bash
# الانتقال لمجلد Backend
cd backend

# تشغيل خادم Flask
python app.py
```

سيعمل الخادم على: `http://localhost:5000`

### 4. تشغيل الواجهة الأمامية (Frontend)

```bash
# يمكن فتح ملف index.html مباشرة في المتصفح
# أو استخدام خادم محلي مثل:

cd frontend

# باستخدام Python
python -m http.server 8080

# أو باستخدام Node.js (إذا كان مثبتاً)
npx serve
```

افتح المتصفح على: `http://localhost:8080`

## 🔑 حسابات افتراضية

| اسم المستخدم | كلمة المرور | الدور | الصلاحيات |
|-------------|------------|-------|----------|
| admin | admin123 | Admin | جميع الصلاحيات |
| engineer | engineer123 | Engineer | إدارة الأجهزة والمراقبة |
| viewer | viewer123 | Viewer | مشاهدة فقط |

## 📁 هيكل المشروع

```
SIM-NET/
├── backend/
│   └── app.py              # خادم Flask الرئيسي
├── frontend/
│   ├── index.html          # الصفحة الرئيسية
│   ├── css/
│   │   └── style.css       # أنماط CSS
│   ├── js/
│   │   └── app.js          # تطبيق JavaScript
│   └── images/             # الصور
├── database/
│   └── db_manager.py       # إدارة قاعدة البيانات
├── modules/
│   ├── network_monitor.py  # مراقبة الشبكة
│   ├── router_automation.py # أتمتة الراوتر
│   └── security_automation.py # أتمتة الأمان
├── ai/
│   └── ai_engine.py        # محرك الذكاء الاصطناعي
├── backups/                # مجلد النسخ الاحتياطية
├── reports/                # مجلد التقارير
├── requirements.txt        # متطلبات Python
└── README.md              # هذا الملف
```

## 🔧 API Endpoints

### المصادقة
- `POST /api/auth/login` - تسجيل الدخول
- `POST /api/auth/logout` - تسجيل الخروج
- `GET /api/auth/me` - المستخدم الحالي

### الأجهزة
- `GET /api/devices` - قائمة الأجهزة
- `POST /api/devices` - إضافة جهاز
- `GET /api/devices/:id` - تفاصيل جهاز
- `DELETE /api/devices/:id` - حذف جهاز
- `POST /api/devices/:id/ping` - Ping جهاز

### المراقبة
- `GET /api/monitoring/dashboard` - بيانات Dashboard
- `GET /api/monitoring/performance` - بيانات الأداء
- `GET /api/monitoring/logs` - السجلات

### الأمان
- `GET /api/security/issues` - مشاكل الأمان
- `POST /api/security/issues` - إضافة مشكلة

### AI
- `GET /api/ai/packet-analysis` - تحليل Packets
- `POST /api/ai/packet-analysis` - إنشاء تحليل
- `GET /api/ai/knowledge-base` - قاعدة المعرفة
- `POST /api/ai/chatbot` - Chatbot

## 📊 لوحة التحكم

لوحة التحكم الرئيسية تعرض:
- إحصائيات الأجهزة (إجمالي، online، offline)
- خريطة الأجهزة
- آخر التنبيهات
- آخر الأنشطة
- رسوم بيانية تفاعلية

## 🤖 Chatbot AI

الـ Chatbot يمكنه المساعدة في:
- تشخيص مشاكل الشبكة
- اقتراح حلول
- تقديم إرشادات

**أمثلة على الأسئلة:**
- "interface is down"
- "high cpu usage"
- "slow network"
- "security alert"

## 🛡️ الأمان

- مصادقة基于 المستخدمين والأدوار
- تشفير كلمات المرور
- تسجيل جميع الأنشطة
- صلاحيات مختلفة لكل دور

## 📈 التقارير

يمكن توليد تقارير تحتوي على:
- إحصائيات الأجهزة
- مشاكل الأمان
- بيانات الأداء
- السجلات

التصدير متاح بصيغ:
- JSON
- Excel (قريباً)
- PDF (قريباً)

## 🔧 Troubleshooting

### مشكلة: لا يمكن الاتصال بالخادم
**الحل:** تأكد من تشغيل Backend على المنفذ 5000
```bash
python backend/app.py
```

### مشكلة: قاعدة البيانات لا تعمل
**الحل:** قم بتهيئة قاعدة البيانات
```bash
python database/db_manager.py
```

### مشكلة: Frontend لا يعرض البيانات
**الحل:** تأكد من:
1. تشغيل Backend
2. عدم وجود حظر CORS
3. صحة عنوان API

## 📝 ملاحظات

- هذا المشروع مناسب لمشروع تخرج
- يمكن توسيعه بإضافة ميزات جديدة
- يدعم العمل مع أجهزة Cisco و Juniper
- يمكن ربطه مع أنظمة إدارة الشبكات الحقيقية

## 👥 المساهمة

نرحب بالمساهمات! يمكنك:
- إضافة ميزات جديدة
- تحسين واجهة المستخدم
- إصلاح الأخطاء
- ترجمة الواجهة

## 📧 التواصل

للاستفسارات والاقتراحات:
- Email: support@simnet.local
- GitHub: github.com/simnet

## 📄 الترخيص

هذا المشروع مفتوح المصدر تحت ترخيص MIT.

---

**تم التطوير بواسطة فريق SIM-NET** 🚀
