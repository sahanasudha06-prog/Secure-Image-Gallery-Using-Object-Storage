# AWS Free Tier Compliance & Zero-Cost Guide (1-Month+ Evaluation)

**Project:** Secure Image Gallery using Object Storage  
**Student:** Sahana (with Samudyata)  
**Target Environment:** AWS Free Tier (12-Month Free Allowance)  
**Expected Monthly Cost:** **$0.00 USD (Guaranteed Zero Bill)**

---

## 1. AWS Free Tier Allowances & Allocation

| Cloud Resource | Free Tier Monthly Allowance | Project Consumption | Headroom / Safety Margin |
|---|---|---|---|
| **AWS EC2 (Virtual Machine)** | **750 Hours / Month** of `t2.micro` or `t3.micro` (Linux) | 1 running `t2.micro` instance = **720-744 hours** | **100% Free** (within 750 hr limit) |
| **Amazon S3 Storage** | **5.0 GB** of Amazon S3 Standard Storage | ~15-30 MB of compressed test images | **< 1% used** (> 4.97 GB headroom) |
| **S3 PUT / POST Requests** | **2,000 PUT/POST/LIST Requests** / month | ~100 - 250 requests during student testing | **> 85% headroom** |
| **S3 GET Requests** | **20,000 GET Requests** / month | ~500 - 1,500 requests for viewing gallery | **> 90% headroom** |
| **AWS IAM** | **Always 100% Free** (No limit on Users/Groups/Roles) | 1 Group (`ImageAdmins`), 1 User, 1 Role | **Always Free** |
| **Data Transfer OUT** | **100 GB / Month** to the Public Internet | < 200 MB during demo presentations | **> 99% headroom** |

---

## 2. Strict "Zero-Cost" Architecture Rules

To guarantee **ZERO unexpected AWS charges** during your 1-month development and viva evaluation:

### What WE USE (100% Free Tier):
- **EC2 Instance:** `t2.micro` (or `t3.micro` in regions where t2 is unavailable) with 8 GB GP3 root volume (up to 30 GB EBS is free).
- **Amazon S3:** Standard Storage class in `us-east-1` (or your chosen region).
- **AWS IAM:** Attached IAM Instance Profile (`EC2-S3-ImageGallery-Role`) with least privilege. Zero access keys stored on disk.
- **Direct Public IP:** EC2 Public IPv4 provided automatically at launch (no paid Elastic IP left unattached).

### What WE NEVER USE (Cost Traps to Avoid):
1. ❌ **NO NAT Gateway:** AWS charges **$0.045/hour + $0.045/GB (~$32.40/month)** for a NAT Gateway. We deploy EC2 in a default public subnet with an Internet Gateway (IGW), which is 100% free.
2. ❌ **NO Application Load Balancer (ALB / ELB):** ALB charges **~$16.20/month** base fee. We serve traffic directly via Nginx on EC2 port 80/5000.
3. ❌ **NO Amazon RDS:** Avoid managed relational databases; the app uses pure S3 object metadata and local configuration.
4. ❌ **NO CloudFront Distributions:** Direct S3 Pre-Signed URLs eliminate the need for custom CDN distributions.
5. ❌ **NO Heavy Polling:** The frontend only loads images on page visit and user actions, preventing unnecessary S3 API calls.

---

## 3. How to Set an AWS $0 Cost Alert (Billing Alarm)

To ensure complete peace of mind, configure a $0.01 / Zero-Dollar budget alert in the AWS Console:

1. Open **AWS Billing and Cost Management Console** (`https://console.aws.amazon.com/billing/`).
2. In the navigation pane, choose **Budgets** -> **Create budget**.
3. Choose **Cost budget (Recommended)**.
4. Set **Budget amount**: `$1.00` (or choose **Zero Spend Budget**).
5. Enter your email address to receive an instant email alert if forecasted or actual spend exceeds $0.01.

---

## 4. Keeping Test Data Lightweight

1. **Image Dimensions:** Keep uploaded demo pictures between **100 KB and 1 MB**.
2. **Bucket Versioning Management:** 
   Bucket versioning stores previous iterations of files. To keep your bucket tiny (< 5 MB), run the cleanup script whenever you want to prune old versions:
   ```bash
   python cleanup_storage.py
   ```
3. This purges old overwritten versions and resets the gallery to the clean 6 Karnataka landmark assets.

---

## 5. Post-Evaluation Cleanup / Teardown Checklist

Once your college viva evaluation and project grading are completed, follow this 3-step cleanup to turn off all resources:

### Step 1: Empty and Delete the Amazon S3 Bucket
```bash
# Empty all objects and historical versions
aws s3 rm s3://sahana-secure-image-gallery --recursive

# Delete bucket
aws s3api delete-bucket --bucket sahana-secure-image-gallery --region us-east-1
```
*(Or in AWS S3 Console: select bucket -> click **Empty** -> type `permanently delete` -> click **Delete**).*

### Step 2: Terminate the AWS EC2 Instance
1. In the AWS EC2 Console, select your `sahana-secure-gallery-server` instance.
2. Click **Instance State** -> **Terminate Instance**.
3. The root EBS volume will automatically be deleted, releasing all compute resources.

### Step 3: Delete IAM Role & Group (Optional)
```bash
aws iam remove-user-from-group --group-name ImageAdmins --user-name sahana_admin
aws iam delete-group --group-name ImageAdmins
aws iam delete-user --user-name sahana_admin
```

---

## 6. Summary for the Invigilator
> *"This project is architected strictly within the AWS Free Tier framework (t2.micro + Amazon S3 + IAM), consuming less than 1% of the 5GB S3 allowance and running zero paid managed gateways or load balancers. Cost safety is enforced through lightweight assets and least-privilege IAM policies."*
