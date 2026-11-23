import os
import json
import time
import uuid
import hmac
import hashlib
import mimetypes
from datetime import datetime
from werkzeug.utils import secure_filename
from config import Config

def detect_category(key, explicit_category=None):
    if explicit_category and explicit_category != "Auto":
        return explicit_category
    lower = key.lower()
    if any(k in lower for k in ["sunset", "forest", "tree", "mountain", "nature", "mist", "lake"]):
        return "Nature"
    if any(k in lower for k in ["cloud", "security", "policy", "token", "banner", "s3", "iam", "aws"]):
        return "Cloud & Security"
    if any(k in lower for k in ["neon", "cyber", "space", "nebula", "planet", "abstract", "glitch"]):
        return "Abstract & Art"
    if any(k in lower for k in ["skyline", "architecture", "building", "facade", "geometric", "tower"]):
        return "Architecture"
    return "Photography"

class StorageService:
    def __init__(self):
        self.backend = Config.STORAGE_BACKEND
        if self.backend == "aws":
            import boto3
            from botocore.config import Config as BotoConfig
            
            session_kwargs = {"region_name": Config.AWS_REGION}
            if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
                session_kwargs["aws_access_key_id"] = Config.AWS_ACCESS_KEY_ID
                session_kwargs["aws_secret_access_key"] = Config.AWS_SECRET_ACCESS_KEY
                if Config.AWS_SESSION_TOKEN:
                    session_kwargs["aws_session_token"] = Config.AWS_SESSION_TOKEN
            
            self.s3_client = boto3.client(
                "s3",
                config=BotoConfig(signature_version="s3v4"),
                **session_kwargs
            )
            self.bucket_name = Config.AWS_S3_BUCKET
        else:
            self.base_dir = Config.LOCAL_STORAGE_DIR
            self.objects_dir = os.path.join(self.base_dir, "objects")
            self.meta_file = os.path.join(self.base_dir, "metadata.json")
            os.makedirs(self.objects_dir, exist_ok=True)
            self._init_local_metadata()

    def _init_local_metadata(self):
        if not os.path.exists(self.meta_file):
            initial_data = {
                "bucket_name": "sahana-secure-image-gallery",
                "versioning_enabled": True,
                "block_public_access": True,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "objects": {}
            }
            with open(self.meta_file, "w") as f:
                json.dump(initial_data, f, indent=2)

    def _load_metadata(self):
        with open(self.meta_file, "r") as f:
            return json.load(f)

    def _save_metadata(self, data):
        with open(self.meta_file, "w") as f:
            json.dump(data, f, indent=2)

    def upload_image(self, file_stream, filename, content_type=None, category=None):
        safe_name = secure_filename(filename)
        if not safe_name:
            safe_name = f"image_{int(time.time())}.jpg"
            
        file_bytes = file_stream.read()
        file_size = len(file_bytes)
        
        if not content_type:
            content_type, _ = mimetypes.guess_type(safe_name)
            content_type = content_type or "image/jpeg"

        assigned_category = detect_category(safe_name, category)

        if self.backend == "aws":
            extra_args = {
                "ContentType": content_type,
                "ServerSideEncryption": "AES256",
                "Metadata": {
                    "uploaded_by": "ImageAdmins-Sahana",
                    "original_filename": safe_name,
                    "category": assigned_category
                }
            }
            response = self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=safe_name,
                Body=file_bytes,
                **extra_args
            )
            version_id = response.get("VersionId", "v1")
            return {
                "key": safe_name,
                "version_id": version_id,
                "size": file_size,
                "content_type": content_type,
                "category": assigned_category,
                "storage_class": "STANDARD",
                "encryption": "AES256",
                "uploaded_at": datetime.utcnow().isoformat() + "Z"
            }
        else:
            meta = self._load_metadata()
            version_id = str(uuid.uuid4())[:8]
            storage_key = f"{version_id}_{safe_name}"
            file_path = os.path.join(self.objects_dir, storage_key)
            
            with open(file_path, "wb") as f:
                f.write(file_bytes)

            version_entry = {
                "version_id": version_id,
                "storage_key": storage_key,
                "size": file_size,
                "content_type": content_type,
                "category": assigned_category,
                "uploaded_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "is_latest": True,
                "is_delete_marker": False,
                "etag": hashlib.md5(file_bytes).hexdigest()
            }

            if safe_name not in meta["objects"]:
                meta["objects"][safe_name] = {
                    "key": safe_name,
                    "category": assigned_category,
                    "versions": [version_entry]
                }
            else:
                meta["objects"][safe_name]["category"] = assigned_category
                for v in meta["objects"][safe_name]["versions"]:
                    v["is_latest"] = False
                meta["objects"][safe_name]["versions"].insert(0, version_entry)

            self._save_metadata(meta)

            return {
                "key": safe_name,
                "version_id": version_id,
                "size": file_size,
                "content_type": content_type,
                "category": assigned_category,
                "storage_class": "STANDARD",
                "encryption": "AES256 (Cloud Simulated)",
                "uploaded_at": version_entry["uploaded_at"]
            }

    def list_images(self):
        if self.backend == "aws":
            try:
                response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
                images = []
                for obj in response.get("Contents", []):
                    key = obj["Key"]
                    category = detect_category(key)
                    images.append({
                        "key": key,
                        "size": obj["Size"],
                        "category": category,
                        "last_modified": obj["LastModified"].strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "storage_backend": "AWS S3",
                        "bucket": self.bucket_name
                    })
                return images
            except Exception as e:
                return []
        else:
            meta = self._load_metadata()
            images = []
            for key, data in meta.get("objects", {}).items():
                active_versions = [v for v in data["versions"] if v.get("is_latest") and not v.get("is_delete_marker")]
                if active_versions:
                    latest = active_versions[0]
                    category = data.get("category") or latest.get("category") or detect_category(key)
                    images.append({
                        "key": key,
                        "version_id": latest["version_id"],
                        "size": latest["size"],
                        "content_type": latest["content_type"],
                        "category": category,
                        "last_modified": latest["uploaded_at"],
                        "storage_backend": "Simulated Amazon S3",
                        "bucket": meta["bucket_name"],
                        "total_versions": len(data["versions"])
                    })
            return sorted(images, key=lambda x: x["last_modified"], reverse=True)

    def delete_image(self, key, version_id=None):
        if self.backend == "aws":
            params = {"Bucket": self.bucket_name, "Key": key}
            if version_id:
                params["VersionId"] = version_id
            return self.s3_client.delete_object(**params)
        else:
            meta = self._load_metadata()
            if key not in meta.get("objects", {}):
                return False, "Object not found"

            versions = meta["objects"][key]["versions"]
            if version_id:
                for idx, v in enumerate(versions):
                    if v["version_id"] == version_id:
                        file_path = os.path.join(self.objects_dir, v.get("storage_key", ""))
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        versions.pop(idx)
                        break
                if versions:
                    versions[0]["is_latest"] = True
                else:
                    del meta["objects"][key]
            else:
                marker_id = str(uuid.uuid4())[:8]
                for v in versions:
                    v["is_latest"] = False
                delete_marker = {
                    "version_id": marker_id,
                    "storage_key": "",
                    "size": 0,
                    "content_type": "binary/octet-stream",
                    "category": meta["objects"][key].get("category", "General"),
                    "uploaded_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "is_latest": True,
                    "is_delete_marker": True,
                    "etag": "delete-marker"
                }
                versions.insert(0, delete_marker)

            self._save_metadata(meta)
            return True, "Object deleted successfully"

    def get_image_versions(self, key):
        if self.backend == "aws":
            try:
                res = self.s3_client.list_object_versions(Bucket=self.bucket_name, Prefix=key)
                versions = []
                for v in res.get("Versions", []):
                    if v["Key"] == key:
                        versions.append({
                            "version_id": v["VersionId"],
                            "is_latest": v["IsLatest"],
                            "last_modified": v["LastModified"].strftime("%Y-%m-%d %H:%M:%S UTC"),
                            "size": v["Size"],
                            "is_delete_marker": False
                        })
                for d in res.get("DeleteMarkers", []):
                    if d["Key"] == key:
                        versions.append({
                            "version_id": d["VersionId"],
                            "is_latest": d["IsLatest"],
                            "last_modified": d["LastModified"].strftime("%Y-%m-%d %H:%M:%S UTC"),
                            "size": 0,
                            "is_delete_marker": True
                        })
                return versions
            except Exception:
                return []
        else:
            meta = self._load_metadata()
            if key in meta.get("objects", {}):
                return meta["objects"][key].get("versions", [])
            return []

    def generate_presigned_url(self, key, expires_in=3600, version_id=None):
        expires_in = int(expires_in)
        if self.backend == "aws":
            params = {"Bucket": self.bucket_name, "Key": key}
            if version_id:
                params["VersionId"] = version_id
            url = self.s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params=params,
                ExpiresIn=expires_in
            )
            return {
                "url": url,
                "expires_in_seconds": expires_in,
                "expires_at": datetime.fromtimestamp(time.time() + expires_in).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "key": key,
                "access_type": "AWS IAM Pre-signed SigV4"
            }
        else:
            expiry_ts = int(time.time()) + expires_in
            msg = f"{key}:{expiry_ts}"
            signature = hmac.new(
                Config.SECRET_KEY.encode(),
                msg.encode(),
                hashlib.sha256
            ).hexdigest()
            
            v_param = f"&version={version_id}" if version_id else ""
            presigned_url = f"/api/media/{key}?expires={expiry_ts}&token={signature}{v_param}"
            
            return {
                "url": presigned_url,
                "expires_in_seconds": expires_in,
                "expires_at": datetime.fromtimestamp(expiry_ts).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "key": key,
                "access_type": "S3-Compliant HMAC-SHA256 Token"
            }

    def verify_local_presigned_token(self, key, expires_ts_str, token):
        try:
            expires_ts = int(expires_ts_str)
            if time.time() > expires_ts:
                return False, "Pre-signed URL has expired"
            
            msg = f"{key}:{expires_ts}"
            expected_sig = hmac.new(
                Config.SECRET_KEY.encode(),
                msg.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if hmac.compare_digest(expected_sig, token):
                return True, "Valid signature"
            return False, "Invalid signature or tampered URL"
        except Exception as e:
            return False, f"Signature verification error: {str(e)}"

    def get_local_file_bytes(self, key, version_id=None):
        meta = self._load_metadata()
        if key not in meta.get("objects", {}):
            return None, None
        
        versions = meta["objects"][key]["versions"]
        target_version = None
        if version_id:
            for v in versions:
                if v["version_id"] == version_id:
                    target_version = v
                    break
        else:
            for v in versions:
                if v.get("is_latest") and not v.get("is_delete_marker"):
                    target_version = v
                    break
        
        if not target_version or target_version.get("is_delete_marker"):
            return None, None
            
        file_path = os.path.join(self.objects_dir, target_version["storage_key"])
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return f.read(), target_version["content_type"]
        return None, None

    def restore_version(self, key, version_id):
        if self.backend == "aws":
            try:
                copy_source = {
                    "Bucket": self.bucket_name,
                    "Key": key,
                    "VersionId": version_id
                }
                res = self.s3_client.copy_object(
                    Bucket=self.bucket_name,
                    CopySource=copy_source,
                    Key=key
                )
                return True, f"Object {key} restored successfully. New VersionId: {res.get('VersionId', 'latest')}"
            except Exception as e:
                return False, str(e)
        else:
            meta = self._load_metadata()
            if key not in meta.get("objects", {}):
                return False, "Object not found"
            
            versions = meta["objects"][key]["versions"]
            target_version = None
            for v in versions:
                if v["version_id"] == version_id and not v.get("is_delete_marker"):
                    target_version = v
                    break
            
            if not target_version:
                return False, "Target version not found or is a delete marker"
            
            file_path = os.path.join(self.objects_dir, target_version.get("storage_key", ""))
            if not os.path.exists(file_path):
                return False, "Underlying version storage file missing"
            
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            
            new_version_id = str(uuid.uuid4())[:8]
            new_storage_key = f"{new_version_id}_{key}"
            new_file_path = os.path.join(self.objects_dir, new_storage_key)
            with open(new_file_path, "wb") as f:
                f.write(file_bytes)
            
            for v in versions:
                v["is_latest"] = False
            
            restored_entry = {
                "version_id": new_version_id,
                "storage_key": new_storage_key,
                "size": len(file_bytes),
                "content_type": target_version.get("content_type", "image/jpeg"),
                "category": target_version.get("category", "General"),
                "uploaded_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "is_latest": True,
                "is_delete_marker": False,
                "etag": hashlib.md5(file_bytes).hexdigest(),
                "restored_from": version_id
            }
            versions.insert(0, restored_entry)
            self._save_metadata(meta)
            return True, f"Version {version_id} restored as new active version ({new_version_id})"

    def get_stats(self):
        images = self.list_images()
        categories = {}
        total_bytes = 0
        total_versions = 0

        for img in images:
            cat = img.get("category", "General")
            categories[cat] = categories.get(cat, 0) + 1
            total_bytes += img.get("size", 0)

        last_upload = images[0] if images else None

        if self.backend == "local":
            meta = self._load_metadata()
            for obj_key, obj_data in meta.get("objects", {}).items():
                total_versions += len(obj_data.get("versions", []))
        else:
            total_versions = len(images)

        quota_bytes = 5 * 1024 * 1024 * 1024  # 5GB AWS S3 Free Tier
        pct_used = min(100.0, (total_bytes / (10 * 1024 * 1024)) * 100)

        return {
            "storage_backend": "Amazon S3" if self.backend == "aws" else "Amazon S3 (Local Emulation)",
            "bucket": Config.AWS_S3_BUCKET if self.backend == "aws" else "sahana-secure-image-gallery",
            "region": Config.AWS_REGION,
            "versioning": "Enabled",
            "block_public_access": "Enabled (Strict)",
            "security_role": "EC2-S3-ImageGallery-Role",
            "iam_group": "ImageAdmins",
            "iam_user": "sahana_admin",
            "total_images": len(images),
            "total_versions": total_versions,
            "total_bytes": total_bytes,
            "total_bytes_formatted": self._format_bytes(total_bytes),
            "last_upload": {
                "key": last_upload["key"],
                "last_modified": last_upload["last_modified"],
                "size_formatted": self._format_bytes(last_upload["size"])
            } if last_upload else None,
            "quota_bytes": quota_bytes,
            "percent_used": round(pct_used, 2),
            "categories": categories
        }

    def _format_bytes(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
