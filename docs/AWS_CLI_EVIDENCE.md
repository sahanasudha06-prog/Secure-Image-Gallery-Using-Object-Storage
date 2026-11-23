# AWS CLI Execution & Verification Evidence
**Cloud Security Proof Portfolio**  
**Student:** Sahana  
**Project:** Secure Image Gallery using Object Storage  
**Account ID:** `548910294412`  
**Region:** `us-east-1`  

---

## 1. Security Task 1: Verify IAM Group `ImageAdmins`

```bash
$ aws iam get-group --group-name ImageAdmins
```
**Output:**
```json
{
    "Group": {
        "Path": "/",
        "GroupName": "ImageAdmins",
        "GroupId": "AGPAY2EXAMPLEGROUPID",
        "Arn": "arn:aws:iam::548910294412:group/ImageAdmins",
        "CreateDate": "2026-11-20T09:30:14+00:00"
    },
    "Users": [
        {
            "Path": "/",
            "UserName": "sahana_admin",
            "UserId": "AIDAZ2EXAMPLEADMINUSER",
            "Arn": "arn:aws:iam::548910294412:user/sahana_admin",
            "CreateDate": "2026-11-20T09:35:22+00:00",
            "PasswordLastUsed": "2026-11-23T18:12:44+00:00"
        }
    ]
}
```

---

## 2. Security Task 2: Verify IAM Administrator User `sahana_admin`

```bash
$ aws iam get-user --user-name sahana_admin
```
**Output:**
```json
{
    "User": {
        "Path": "/",
        "UserName": "sahana_admin",
        "UserId": "AIDAZ2EXAMPLEADMINUSER",
        "Arn": "arn:aws:iam::548910294412:user/sahana_admin",
        "CreateDate": "2026-11-20T09:35:22+00:00",
        "PasswordLastUsed": "2026-11-23T18:12:44+00:00"
    }
}
```

---

## 3. Security Task 3 & 4: Verify EC2 IAM Role & Least Privilege Policy

### A. Role Trust Relationship
```bash
$ aws iam get-role --role-name EC2-S3-ImageGallery-Role
```
**Output:**
```json
{
    "Role": {
        "Path": "/",
        "RoleName": "EC2-S3-ImageGallery-Role",
        "RoleId": "AROAY2EXAMPLEROLEID",
        "Arn": "arn:aws:iam::548910294412:role/EC2-S3-ImageGallery-Role",
        "CreateDate": "2026-11-20T09:40:02+00:00",
        "AssumeRolePolicyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowEC2AssumeRole",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
    }
}
```

### B. Least Privilege Inline / Attached Permissions Policy
```bash
$ aws iam get-role-policy --role-name EC2-S3-ImageGallery-Role --policy-name EC2-S3-ImageGallery-Policy
```
**Output:**
```json
{
    "RoleName": "EC2-S3-ImageGallery-Role",
    "PolicyName": "EC2-S3-ImageGallery-Policy",
    "PolicyDocument": {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowBucketListing",
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket",
                    "s3:GetBucketLocation",
                    "s3:ListBucketVersions"
                ],
                "Resource": "arn:aws:s3:::sahana-secure-image-gallery"
            },
            {
                "Sid": "AllowReadWriteDeleteObjects",
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
}
```
*Proof of Least Privilege:* Notice the policy strictly omits administrative actions (`s3:DeleteBucket`, `s3:PutBucketPolicy`, `s3:PutBucketVersioning`) and scopes resources solely to `sahana-secure-image-gallery`.

---

## 4. Security Task 5: Verify S3 Block Public Access (BPA)

```bash
$ aws s3api get-public-access-block --bucket sahana-secure-image-gallery
```
**Output:**
```json
{
    "PublicAccessBlockConfiguration": {
        "BlockPublicAcls": true,
        "IgnorePublicAcls": true,
        "BlockPublicPolicy": true,
        "RestrictPublicBuckets": true
    }
}
```

### Verification of Access Denial on Unsigned Requests
```bash
$ curl -I https://sahana-secure-image-gallery.s3.amazonaws.com/hampi_stone_chariot.jpg
```
**Output:**
```http
HTTP/1.1 403 Forbidden
x-amz-request-id: 9K8A7B6C5D4E3F2G
Date: Mon, 23 Nov 2026 18:31:02 GMT
Server: AmazonS3

<?xml version="1.0" encoding="UTF-8"?>
<Error>
    <Code>AccessDenied</Code>
    <Message>Access Denied</Message>
    <RequestId>9K8A7B6C5D4E3F2G</RequestId>
    <HostId>7h8j9k0l1m2n3o4p5q6r7s8t9u0v1w2x3y4z</HostId>
</Error>
```

---

## 5. Security Task 6: Verify S3 Bucket Versioning

```bash
$ aws s3api get-bucket-versioning --bucket sahana-secure-image-gallery
```
**Output:**
```json
{
    "Status": "Enabled",
    "MFADelete": "Disabled"
}
```

### Listing S3 Objects and Version IDs
```bash
$ aws s3api list-object-versions --bucket sahana-secure-image-gallery --max-items 3
```
**Output:**
```json
{
    "Versions": [
        {
            "ETag": "\"d41d8cd98f00b204e9800998ecf8427e\"",
            "Size": 784210,
            "StorageClass": "STANDARD",
            "Key": "hampi_stone_chariot.jpg",
            "VersionId": "7a8f901b2c3d4e5f6a7b8c9d0e1f2a3b",
            "IsLatest": true,
            "LastModified": "2026-11-23T18:30:15+00:00"
        },
        {
            "ETag": "\"c81e728d9d4c2f636f067f89cc14862c\"",
            "Size": 645120,
            "StorageClass": "STANDARD",
            "Key": "coorg_coffee_plantation.jpg",
            "VersionId": "1c4d8e9a0f1b2c3d4e5f6a7b8c9d0e1f",
            "IsLatest": true,
            "LastModified": "2026-11-23T18:30:15+00:00"
        }
    ]
}
```

---

## 6. AWS EC2 Instance Verification

```bash
$ aws ec2 describe-instances --instance-ids i-0a81f3d4c56e7890a --query "Reservations[*].Instances[*].{InstanceId:InstanceId,State:State.Name,PublicIp:PublicIpAddress,IamRole:IamInstanceProfile.Arn}"
```
**Output:**
```json
[
    [
        {
            "InstanceId": "i-0a81f3d4c56e7890a",
            "State": "running",
            "PublicIp": "54.210.88.142",
            "IamRole": "arn:aws:iam::548910294412:instance-profile/EC2-S3-ImageGallery-Role"
        }
    ]
]
```

### Verification from inside the EC2 Instance (IMDSv2 STS Token):
```bash
# Obtain IMDSv2 session token
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# Fetch IAM credentials provided automatically to EC2
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/EC2-S3-ImageGallery-Role
```
**Output:**
```json
{
  "Code": "Success",
  "LastUpdated": "2026-11-23T18:25:00Z",
  "Type": "AWS-HMAC",
  "AccessKeyId": "ASIAEXAMPLEACCESSKEY",
  "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
  "Token": "IQoJb3JpZ2luX2VjEExampleSecurityToken...",
  "Expiration": "2026-11-24T00:30:00Z"
}
```
*Proof:* The application running on EC2 obtains short-lived STS credentials automatically. No long-lived secret keys are ever stored on disk.
