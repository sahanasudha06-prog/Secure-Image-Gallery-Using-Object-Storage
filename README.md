# Secure Image Gallery using Cloud Object Storage

**Cloud Computing Project**  
**Student:** Sahana  
**Cloud Technologies:** AWS EC2, Amazon S3, AWS IAM, Public APIs  

---

## 🌟 Project Overview
This project is an enterprise-grade cloud media storage and sharing system. It enforces zero public bucket access using **Amazon S3 Block Public Access (BPA)**, implements the **Principle of Least Privilege (PoLP)** with an EC2 IAM Role (`EC2-S3-ImageGallery-Role`), ensures data durability with **S3 Bucket Versioning**, integrates the **Public APIs Ingestion Hub** (NASA APOD, Picsum Photography, Dog CEO), and provides secure time-bounded media sharing via **Pre-Signed URLs** with live QR codes.

---

## 📁 Directory Structure
```
D:\sahana\
├── app.py                     # Flask REST API backend
├── storage_service.py         # Dual-Mode Object Storage (AWS S3 & Local S3 Emulator)
├── public_api_service.py      # Integration with open verified Public APIs
├── config.py                  # Environment and application configurations
├── requirements.txt           # Python dependencies
├── .env                       # Environment configuration
├── run.bat                    # One-click start script for Windows
├── seed_rich_gallery.py       # High-resolution artwork generator
├── test_app.py                # Automated unit & security test suite
├── templates\
│   └── index.html             # Clean, modern UI (Tailwind CSS, Lucide Icons, QRCode.js)
├── static\
│   ├── css\style.css          # Sleek card and modal styling
│   └── js\app.js              # Client logic, category filters, and Public API modals
└── docs\
    ├── FINAL_PROJECT_REPORT.md      # 5-8 page academic project report
    ├── DEPLOYMENT_STEPS.md          # Complete AWS EC2 & S3 deployment guide
    ├── ARCHITECTURE_DIAGRAM.svg     # Scalable vector cloud architecture diagram
    └── IAM_POLICIES.json            # Official IAM policies for all security tasks
```

---

## 🚀 Quick Start (Localhost Demo)

### Option 1: Double Click `run.bat`
Navigate to `D:\sahana` in File Explorer and double click **`run.bat`**.

### Option 2: Command Line
```bash
cd D:\sahana
python app.py
```

Then open your browser and go to:
👉 **`http://localhost:5000`**

---

## 🔒 Core Features & Security Tasks
1. **Public APIs Hub:** One-click ingestion from NASA APOD, Lorem Picsum, and Dog CEO APIs.
2. **IAM Role for EC2 (`EC2-S3-ImageGallery-Role`):** Instance metadata role; zero hardcoded credentials in source code.
3. **Least Privilege Permissions:** Scoped strictly to `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`, and `s3:ListBucket`.
4. **Block Public Bucket Access:** All four BPA controls enabled; direct unauthenticated access returns `HTTP 403 Forbidden`.
5. **Bucket Versioning:** Tracks all object updates and insertions; soft deletes create `Delete Markers`.
6. **Pre-Signed URLs & QR Codes:** Secure temporary access links generated with HMAC-SHA256 / AWS SigV4 (5m to 7 days).
7. **View Modes & Categories:** Filter by Nature, Architecture, Cloud & Security, Abstract, and Wallpapers.
