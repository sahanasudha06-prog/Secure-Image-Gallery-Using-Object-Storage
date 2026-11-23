# Secure Image Gallery using Cloud Object Storage

**Cloud Computing Laboratory Project**  
**Student:** Sahana  
**Cloud Infrastructure:** AWS EC2, Amazon S3, AWS IAM  
**Live Cloud Demo:** [http://3.106.248.243:5000](http://3.106.248.243:5000)

---

## 🌟 Live Cloud Deployment

| Cloud Component | Resource Details | Security Configuration |
|---|---|---|
| **Virtual Machine (VM)** | AWS EC2 `t3.micro` (Ubuntu Server) | Instance Profile: `EC2-S3-ImageGallery-Role` |
| **Object Storage** | Amazon S3: `sahana-secure-image-gallery` | **Block Public Access (4/4 ON)**, **Versioning Enabled** |
| **AWS Region** | `ap-southeast-2` (Asia Pacific / Sydney) | Server-Side Encryption: `SSE-S3 (AES-256)` |
| **IAM Group** | `ImageAdmins` | Least Privilege S3 Administration |
| **IAM User** | `sahana_admin` | Dedicated Administrator Identity |
| **Live Web App** | `http://3.106.248.243:5000` | Temporary Access via SigV4 Pre-Signed URLs |

---

## 🔒 6 Security Tasks (Syllabus Compliance)

1. **IAM Group (`ImageAdmins`):** Dedicated administrative group enforcing the Principle of Least Privilege.
2. **IAM User (`sahana_admin`):** Administrator user mapped to `ImageAdmins` for secure management.
3. **IAM Role for EC2 (`EC2-S3-ImageGallery-Role`):** Instance profile attached to the VM; **zero hardcoded credentials or secret keys** in source code.
4. **Least-Privilege EC2 Policy:** Scoped strictly to `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`, and `s3:ListBucket` on `sahana-secure-image-gallery`.
5. **Block Public Bucket Access:** All 4 S3 BPA controls strictly active; unauthenticated direct requests return `HTTP 403 Forbidden`.
6. **Bucket Versioning:** Continuous object version tracking safeguarding against accidental overwrites with 1-click version restore.

---

## 🚀 Core Application Capabilities

* **Upload Images:** Drag-and-drop or file browser upload directly to private Amazon S3 with assigned S3 Version IDs.
* **View Images:** Responsive gallery grid with full-size Lightbox preview, Next/Previous keyboard navigation, and S3 Object Metadata inspector.
* **Delete Images:** Role-based deletion protected by Least Privilege (restricted to `ImageAdmins`; ReadOnly users are denied with 403).
* **Generate Image URLs:** Time-bounded temporary access links (5m, 15m, 1h, 6h, 24h) with live countdown timers and direct test links.
* **Public APIs Ingestion:** Stream media directly from [public-apis](https://github.com/public-apis/public-apis) (NASA APOD, Picsum Photography, Dog CEO) into private S3.

---

## 📁 Repository & Deliverables Directory Structure

```
.
├── app.py                     # Flask REST API backend (boto3 AWS S3 engine)
├── storage_service.py         # Dual-Mode Storage Service (AWS S3 & Local Emulation)
├── public_api_service.py      # Integration with open verified Public APIs
├── config.py                  # Cloud configuration & environment mappings
├── requirements.txt           # Python dependencies (flask, boto3, pillow, etc.)
├── cleanup_storage.py         # AWS Free Tier storage optimizer
├── test_app.py                # Automated 9-test functional & security verification suite
├── manual_verification_test.py # 12-step end-to-end audit script
├── templates/
│   └── index.html             # Clean UI with S3 stats strip, lightbox, and RBAC switcher
├── static/
│   ├── css/style.css          # Sleek card layout and responsive styles
│   └── js/app.js              # Client-side state, live countdowns, and version restore
└── docs/
    ├── FINAL_PROJECT_REPORT.md      # 5-8 page academic project report
    ├── DEPLOYMENT_STEPS.md          # Step-by-step AWS EC2 & S3 deployment guide
    ├── ARCHITECTURE_DIAGRAM.svg     # Cloud architecture vector diagram
    ├── IAM_POLICIES.json            # Official IAM policies for all security tasks
    ├── FREE_TIER_COST_GUIDE.md      # AWS Free Tier $0 budget & teardown guide
    ├── AWS_CLI_EVIDENCE.md          # Real AWS CLI verification command outputs
    └── screenshots/                 # Real AWS Console & Application screenshots
```

---

## 🛠️ How to Run the Project

### On AWS EC2 (Production Mode):
```bash
git clone https://github.com/sahanasudha06-prog/Secure-Image-Gallery-Using-Object-Storage.git
cd Secure-Image-Gallery-Using-Object-Storage
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

export STORAGE_BACKEND=aws
export AWS_S3_BUCKET=sahana-secure-image-gallery
export AWS_REGION=ap-southeast-2

python3 app.py
```
Access via: `http://<EC2-PUBLIC-IP>:5000`

### On Localhost (Development / Zero-Cost Mode):
Double click **`run.bat`** or run:
```bash
python app.py
```
Access via: `http://localhost:5000`

---

## 🧪 Verification & Automated Testing

Run the automated test suite anytime:
```bash
python test_app.py
```
*All 9 test cases verify S3 connectivity, BPA 403 denial, pre-signed SigV4 authorization, bucket versioning, and Least Privilege RBAC enforcement.*
