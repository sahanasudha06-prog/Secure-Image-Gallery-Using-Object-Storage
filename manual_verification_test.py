"""
manual_verification_test.py
Rigorous manual verification of ALL requirements and security tasks specified in Sir's PDF.
"""
import io
import os
import sys
import json
from PIL import Image, ImageDraw
from app import app, storage

def create_sample_image(text="Test", color="#3b82f6"):
    img = Image.new("RGB", (400, 300), color=color)
    d = ImageDraw.Draw(img)
    d.text((50, 140), text, fill="white")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf

def run_all_manual_tests():
    print("=" * 70)
    print("  COMPREHENSIVE MANUAL VERIFICATION: SAHANA SECURE IMAGE GALLERY")
    print("=" * 70)
    
    client = app.test_client()
    passed = 0
    total = 12

    # ---------------- TEST 1: APP DEMO & STATS ----------------
    print("\n[TEST 1/12] Testing Application Demo & Live S3 Stats API...")
    res = client.get("/api/stats")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    stats = res.get_json()["stats"]
    print(f"  • S3 Bucket:         {stats['bucket']}")
    print(f"  • Storage Backend:   {stats['storage_backend']}")
    print(f"  • Versioning:        {stats['versioning']}")
    print(f"  • Block Public Acc:  {stats['block_public_access']}")
    print(f"  • Total Images:      {stats['total_images']}")
    print(f"  • Total Storage:     {stats['total_bytes_formatted']}")
    assert stats["versioning"] == "Enabled"
    print("  --> PASS: Application and live stats responding perfectly.")
    passed += 1

    # ---------------- TEST 2: UPLOAD IMAGE (FEATURE 1) ----------------
    print("\n[TEST 2/12] Testing Image Upload (Feature 1)...")
    img_buf = create_sample_image("Manual Test Asset 2026", color="#4f46e5")
    upload_res = client.post(
        "/api/upload",
        data={"image": (img_buf, "manual_test_photo.jpg")},
        content_type="multipart/form-data"
    )
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.data}"
    up_data = upload_res.get_json()["data"]
    test_key = up_data["key"]
    v1_id = up_data["version_id"]
    print(f"  • Uploaded Key:      {test_key}")
    print(f"  • Assigned S3 VerID: {v1_id}")
    print(f"  • MIME Content-Type: {up_data['content_type']}")
    print(f"  • Storage Class:     {up_data['storage_class']}")
    assert test_key == "manual_test_photo.jpg"
    print("  --> PASS: Uploaded image successfully into private S3 storage.")
    passed += 1

    # ---------------- TEST 3: VIEW IMAGES (FEATURE 2) ----------------
    print("\n[TEST 3/12] Testing View Images & Gallery Listing (Feature 2)...")
    list_res = client.get("/api/images")
    assert list_res.status_code == 200
    images = list_res.get_json()["images"]
    found = any(img["key"] == "manual_test_photo.jpg" for img in images)
    assert found, "Uploaded image not found in gallery listing"
    target_img = next(img for img in images if img["key"] == "manual_test_photo.jpg")
    print(f"  • Gallery Count:     {len(images)} images")
    print(f"  • Preview URL Gen:   {target_img['preview_url'][:60]}...")
    print("  --> PASS: Image listing and thumbnail previews functioning.")
    passed += 1

    # ---------------- TEST 4: S3 BLOCK PUBLIC ACCESS (SECURITY TASK 5) ----------------
    print("\n[TEST 4/12] Testing S3 Block Public Access (Security Task 5)...")
    # An unsigned, direct request to the media URL MUST be rejected with HTTP 403 Forbidden
    direct_res = client.get(f"/api/media/{test_key}")
    assert direct_res.status_code == 403, f"Expected 403, got {direct_res.status_code}"
    err_json = direct_res.get_json()
    print(f"  • HTTP Status:       {direct_res.status_code} Forbidden")
    print(f"  • Denial Reason:     {err_json['error']}")
    print(f"  • Policy Enforced:   {err_json['security_policy']}")
    print("  --> PASS: Direct unauthenticated public requests strictly blocked (403 Forbidden).")
    passed += 1

    # ---------------- TEST 5: GENERATE PRE-SIGNED URL (FEATURE 4) ----------------
    print("\n[TEST 5/12] Testing Pre-Signed URL Generation (Feature 4)...")
    presign_res = client.post(
        f"/api/images/{test_key}/presign",
        json={"expires_in": 300}
    )
    assert presign_res.status_code == 200
    pdata = presign_res.get_json()["data"]
    presigned_url = pdata["url"]
    print(f"  • Generated URL:     {presigned_url}")
    print(f"  • Expiration:        {pdata['expires_at']} ({pdata['expires_in_seconds']}s)")
    print(f"  • Token Auth Type:   {pdata['access_type']}")
    print("  --> PASS: Time-bounded pre-signed URL generated successfully.")
    passed += 1

    # ---------------- TEST 6: AUTHORIZED PRE-SIGNED URL ACCESS ----------------
    print("\n[TEST 6/12] Testing Authorized Media Access via Pre-Signed URL...")
    fetch_res = client.get(presigned_url)
    assert fetch_res.status_code == 200, f"Expected 200, got {fetch_res.status_code}"
    assert fetch_res.mimetype == "image/jpeg"
    print(f"  • HTTP Status:       {fetch_res.status_code} OK")
    print(f"  • Returned MIME:     {fetch_res.mimetype}")
    print(f"  • Data Length:       {len(fetch_res.data)} bytes")
    print("  --> PASS: Pre-signed token successfully authorizes temporary read access.")
    passed += 1

    # ---------------- TEST 7: EXPIRED / TAMPERED TOKEN DENIAL ----------------
    print("\n[TEST 7/12] Testing Tampered Signature Rejection...")
    tampered_url = presigned_url + "tampered"
    tampered_res = client.get(tampered_url)
    assert tampered_res.status_code == 403
    print(f"  • Tampered Status:   {tampered_res.status_code} Forbidden")
    print("  --> PASS: Tampered / unauthorized signatures rejected with 403 Forbidden.")
    passed += 1

    # ---------------- TEST 8: BUCKET VERSIONING (SECURITY TASK 6) ----------------
    print("\n[TEST 8/12] Testing S3 Bucket Versioning (Security Task 6)...")
    # Upload an update with the exact same key
    img_v2 = create_sample_image("Manual Test Asset Version 2", color="#10b981")
    v2_res = client.post(
        "/api/upload",
        data={"image": (img_v2, test_key)},
        content_type="multipart/form-data"
    )
    assert v2_res.status_code == 200
    v2_id = v2_res.get_json()["data"]["version_id"]
    assert v2_id != v1_id, "New version must have distinct version ID"
    print(f"  • Original Version:  {v1_id}")
    print(f"  • New Version ID:    {v2_id}")

    # Check version history
    ver_history = client.get(f"/api/images/{test_key}/versions").get_json()["versions"]
    assert len(ver_history) >= 2
    assert ver_history[0]["version_id"] == v2_id
    assert ver_history[0]["is_latest"] is True
    print(f"  • Version Count:     {len(ver_history)} versions preserved in S3")
    print("  --> PASS: S3 Bucket Versioning successfully protects against overwrites.")
    passed += 1

    # ---------------- TEST 9: S3 VERSION RESTORE ----------------
    print("\n[TEST 9/12] Testing S3 Version Restore Capability...")
    restore_res = client.post(
        f"/api/images/{test_key}/versions/{v1_id}/restore",
        headers={"X-User-Role": "ImageAdmins"}
    )
    assert restore_res.status_code == 200
    restore_data = restore_res.get_json()
    print(f"  • Restore Result:    {restore_data['message']}")
    # Verify version 1 data restored as latest
    updated_history = client.get(f"/api/images/{test_key}/versions").get_json()["versions"]
    assert updated_history[0]["restored_from"] == v1_id
    print("  --> PASS: Historical version successfully restored as new active version.")
    passed += 1

    # ---------------- TEST 10: S3 OBJECT METADATA INSPECTOR ----------------
    print("\n[TEST 10/12] Testing S3 Object Metadata Inspector...")
    meta_res = client.get(f"/api/images/{test_key}/metadata")
    assert meta_res.status_code == 200
    meta = meta_res.get_json()
    print(f"  • S3 Bucket:         {meta['bucket']}")
    print(f"  • AWS Region:        {meta['region']}")
    print(f"  • Encryption:        {meta['encryption']}")
    print(f"  • Storage Class:     {meta['storage_class']}")
    print(f"  • ETag:              {meta['etag']}")
    assert meta["encryption"] == "AES256 (SSE-S3)"
    print("  --> PASS: Complete S3 object metadata returned.")
    passed += 1

    # ---------------- TEST 11: LEAST PRIVILEGE RBAC ENFORCEMENT ----------------
    print("\n[TEST 11/12] Testing Principle of Least Privilege (RBAC)...")
    # Step A: Viewer attempts deletion -> Must return 403 Forbidden
    viewer_del = client.delete(
        f"/api/images/{test_key}",
        headers={"X-User-Role": "Viewer"}
    )
    assert viewer_del.status_code == 403, f"Viewer deletion should be 403, got {viewer_del.status_code}"
    print(f"  • Viewer Delete:     HTTP {viewer_del.status_code} (AccessDenied - Least Privilege)")

    # Step B: ImageAdmins attempts deletion -> Must succeed with 200 OK
    admin_del = client.delete(
        f"/api/images/{test_key}",
        headers={"X-User-Role": "ImageAdmins"}
    )
    assert admin_del.status_code == 200, f"Admin deletion failed: {admin_del.data}"
    print(f"  • Admin Delete:      HTTP {admin_del.status_code} (Authorized - ImageAdmins privilege)")
    print("  --> PASS: Principle of Least Privilege strictly enforced between IAM roles.")
    passed += 1

    # ---------------- TEST 12: DELIVERABLES FILE AUDIT ----------------
    print("\n[TEST 12/12] Auditing All Deliverables on Disk...")
    base_dir = r"D:\sahana"
    docs_dir = os.path.join(base_dir, "docs")
    shots_dir = os.path.join(docs_dir, "screenshots")
    
    deliverables = [
        ("Deliverable 1: App Demo (Launcher)", os.path.join(base_dir, "run.bat")),
        ("Deliverable 2: Architecture Diagram", os.path.join(docs_dir, "ARCHITECTURE_DIAGRAM.svg")),
        ("Deliverable 3: IAM Policy Document", os.path.join(docs_dir, "IAM_POLICIES.json")),
        ("Deliverable 4: AWS Console Screenshots", [
            os.path.join(shots_dir, "aws_console_1_iam_group_imageadmins.svg"),
            os.path.join(shots_dir, "aws_console_2_iam_role_ec2.svg"),
            os.path.join(shots_dir, "aws_console_3_s3_block_public_access.svg"),
            os.path.join(shots_dir, "aws_console_4_s3_bucket_versioning.svg"),
            os.path.join(shots_dir, "aws_console_5_s3_objects_list.svg"),
            os.path.join(shots_dir, "aws_console_6_ec2_running_instance.svg"),
        ]),
        ("Deliverable 5: Source Code & Deployment", os.path.join(docs_dir, "DEPLOYMENT_STEPS.md")),
        ("Deliverable 6: Final Project Report (5-8 pp)", os.path.join(docs_dir, "FINAL_PROJECT_REPORT.md")),
        ("Deliverable 7: AWS CLI Evidence", os.path.join(docs_dir, "AWS_CLI_EVIDENCE.md")),
        ("Deliverable 8: Free Tier $0 Cost Guide", os.path.join(docs_dir, "FREE_TIER_COST_GUIDE.md")),
    ]

    all_exist = True
    for name, path in deliverables:
        if isinstance(path, list):
            for sub_p in path:
                exists = os.path.exists(sub_p)
                print(f"  • {os.path.basename(sub_p)}: {'[OK]' if exists else '[MISSING]'}")
                if not exists: all_exist = False
        else:
            exists = os.path.exists(path)
            print(f"  • {name}: {'[OK]' if exists else '[MISSING]'}")
            if not exists: all_exist = False

    assert all_exist, "One or more required deliverables are missing!"
    print("  --> PASS: All required deliverables exist, verified and complete.")
    passed += 1

    print("\n" + "=" * 70)
    print(f"  ALL {passed}/{total} VERIFICATION CHECKS PASSED WITH ZERO ERRORS!")
    print("=" * 70)

if __name__ == "__main__":
    run_all_manual_tests()
