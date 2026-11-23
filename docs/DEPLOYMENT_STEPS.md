# AWS Cloud Deployment & Configuration Guide

**Project Title:** Secure Image Gallery using Object Storage  
**Course:** Cloud Computing Laboratory  
**Student:** Sahana  
**Cloud Provider:** Amazon Web Services (AWS)  

---

## 1. Overview of Cloud Architecture

The architecture implements a secure, scalable media storage and archival solution following the **Principle of Least Privilege**:
* **Virtual Machine:** AWS EC2 Instance running Python Flask web application.
* **Object Storage:** Amazon S3 with **Block Public Access** and **Bucket Versioning** enabled.
* **IAM Security:** IAM Group `ImageAdmins`, IAM User `sahana_admin`, and EC2 Instance Role `EC2-S3-ImageGallery-Role` providing temporary credentials (STS) without hardcoding access keys in source code.
* **Public APIs Ingestion Hub:** Ingestion pipeline integrating open verified APIs (NASA APOD, Lorem Picsum, Dog CEO, and Public Web URLs) streaming media directly into encrypted S3 storage.
* **Access Control:** All end-user viewing and downloads are authorized via **Pre-Signed URLs** with customizable expiration periods (e.g., 5 mins, 1 hour, 24 hours, 7 days) and mobile scannable QR codes.

---

## 2. Security Task 1: Create IAM Group `ImageAdmins`

1. Open **AWS Management Console** -> Navigate to **IAM** -> **User Groups**.
2. Click **Create group**.
3. Group name: `ImageAdmins`.
4. Attach the following custom policy (or create a policy named `ImageAdmins-S3-Policy` using the JSON below):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3Management",
      "Effect": "Allow",
      "Action": [
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation",
        "s3:GetBucketVersioning",
        "s3:PutBucketVersioning",
        "s3:GetBucketPolicy",
        "s3:PutBucketPolicy",
        "s3:GetBucketPublicAccessBlock",
        "s3:PutBucketPublicAccessBlock"
      ],
      "Resource": "arn:aws:s3:::*"
    },
    {
      "Sid": "AllowObjectAdmin",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:ListBucketVersions",
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:DeleteObjectVersion"
      ],
      "Resource": [
        "arn:aws:s3:::sahana-secure-image-gallery",
        "arn:aws:s3:::sahana-secure-image-gallery/*"
      ]
    }
  ]
}
```

---

## 3. Security Task 2: Create IAM User for Administrator

1. In **IAM** -> Click **Users** -> **Create user**.
2. Username: `sahana_admin`.
3. Provide AWS Management Console access (Custom password).
4. Add user to the `ImageAdmins` group.
5. Review and click **Create user**.

---

## 4. Security Task 3 & 4: Create IAM Role for EC2

Using an IAM Role eliminates hardcoded access keys and utilizes AWS Security Token Service (STS) auto-rotated credentials.

1. In **IAM** -> Click **Roles** -> **Create role**.
2. Trusted entity type: **AWS service** -> Use case: **EC2**.
3. Click **Next**.
4. Create and attach the least privilege policy named `EC2-S3-ImageGallery-Policy`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListImageBucket",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation",
        "s3:ListBucketVersions"
      ],
      "Resource": "arn:aws:s3:::sahana-secure-image-gallery"
    },
    {
      "Sid": "ReadWriteDeleteImageObjects",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:DeleteObjectVersion"
      ],
      "Resource": "arn:aws:s3:::sahana-secure-image-gallery/*"
    }
  ]
}
```
5. Role name: `EC2-S3-ImageGallery-Role`.
6. Click **Create role**.

---

## 5. Security Task 5 & 6: S3 Bucket Setup (Block Public Access & Versioning)

You can execute this via the AWS Console or using AWS CLI:

### A. Create Private Bucket
```bash
aws s3api create-bucket \
    --bucket sahana-secure-image-gallery \
    --region us-east-1
```

### B. Block Public Bucket Access (Strict Least Privilege)
```bash
aws s3api put-public-access-block \
    --bucket sahana-secure-image-gallery \
    --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### C. Enable Bucket Versioning
```bash
aws s3api put-bucket-versioning \
    --bucket sahana-secure-image-gallery \
    --versioning-configuration Status=Enabled
```

### D. Verify Bucket Status
```bash
aws s3api get-bucket-versioning --bucket sahana-secure-image-gallery
aws s3api get-public-access-block --bucket sahana-secure-image-gallery
```

---

## 6. Launching and Configuring the AWS EC2 VM

1. Navigate to **EC2 Console** -> Click **Launch Instances**.
2. Configuration:
   * **Name:** `Sahana-ImageGallery-Server`
   * **AMI:** Amazon Linux 2023 or Ubuntu 22.04 LTS
   * **Instance Type:** `t2.micro` (Free Tier eligible)
   * **Key Pair:** Create or select your key pair (e.g. `sahana-key.pem`)
   * **Network Settings:**
     * Allow SSH traffic from Your IP (port 22)
     * Allow HTTP traffic from Anywhere (port 80)
     * Allow custom TCP port 5000 (optional)
   * **Advanced Details:**
     * **IAM instance profile:** Select `EC2-S3-ImageGallery-Role`

3. Click **Launch Instance**.

---

## 7. Deploying the Application on EC2

Connect to your EC2 instance via SSH:
```bash
ssh -i "sahana-key.pem" ubuntu@<EC2-PUBLIC-IP>
```

Run the following commands on the server:
```bash
# Update system packages
sudo apt update -y && sudo apt upgrade -y
sudo apt install -y python3 python3-pip git nginx

# Create directory
sudo mkdir -p /var/www/sahana
cd /var/www/sahana

# Copy application files (app.py, storage_service.py, public_api_service.py, config.py, templates, static)
# Install dependencies
pip3 install -r requirements.txt

# Create .env file for AWS EC2 production
cat <<EOF > .env
SECRET_KEY=sahana-cloud-production-secret-2026
STORAGE_BACKEND=aws
AWS_REGION=us-east-1
AWS_S3_BUCKET=sahana-secure-image-gallery
PORT=5000
DEBUG=False
EOF
```

### Configure Systemd Service
```bash
sudo cat <<EOF > /etc/systemd/system/gallery.service
[Unit]
Description=Sahana Secure Image Gallery
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/sahana
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable gallery
sudo systemctl start gallery
```

### Configure Nginx Reverse Proxy
```bash
sudo cat <<EOF > /etc/nginx/sites-available/gallery
server {
    listen 80;
    server_name _;

    client_max_body_size 25M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/gallery /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
```

---

## 8. Localhost Execution (For Immediate Local Testing)

1. Double-click `run.bat` or run:
   ```cmd
   python app.py
   ```
2. Open your web browser at:
   ```
   http://localhost:5000
   ```
3. Test uploading, importing from Public APIs (NASA APOD, Picsum, Dog CEO), generating Pre-Signed URLs with QR codes, inspecting version histories, and deleting objects.
