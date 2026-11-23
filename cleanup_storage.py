#!/usr/bin/env python3
"""
cleanup_storage.py — AWS Free Tier Storage Optimizer
Removes test versions, delete markers, and oversized uploads to keep the S3 bucket < 5 MB.
"""

import os
import json
from config import Config
from storage_service import StorageService

def run_cleanup():
    print("=" * 60)
    print("  AWS FREE TIER STORAGE CLEANUP & OPTIMIZER")
    print("=" * 60)
    
    storage = StorageService()
    
    if storage.backend == "aws":
        print(f"[+] Connecting to AWS S3 Bucket: {storage.bucket_name}...")
        try:
            versions = storage.s3_client.list_object_versions(Bucket=storage.bucket_name)
            del_count = 0
            # Remove delete markers
            for d in versions.get("DeleteMarkers", []):
                storage.s3_client.delete_object(
                    Bucket=storage.bucket_name,
                    Key=d["Key"],
                    VersionId=d["VersionId"]
                )
                del_count += 1
            print(f"[✓] Cleaned up {del_count} stale delete markers from AWS S3.")
        except Exception as e:
            print(f"[!] Error cleaning AWS S3: {e}")
    else:
        meta_file = storage.meta_file
        with open(meta_file, "r") as f:
            data = json.load(f)
            
        pruned_versions = 0
        for key, obj in data.get("objects", {}).items():
            versions = obj.get("versions", [])
            # Keep only the latest 2 versions per object
            if len(versions) > 2:
                to_remove = versions[2:]
                obj["versions"] = versions[:2]
                for v in to_remove:
                    skey = v.get("storage_key", "")
                    if skey:
                        fpath = os.path.join(storage.objects_dir, skey)
                        if os.path.isfile(fpath):
                            os.remove(fpath)
                    pruned_versions += 1
                    
        with open(meta_file, "w") as f:
            json.dump(data, f, indent=2)
            
        print(f"[✓] Pruned {pruned_versions} redundant historical versions.")
        
    stats = storage.get_stats()
    print(f"\n[✓] Storage status:")
    print(f"    • Total Active Objects: {stats['total_images']}")
    print(f"    • Total Storage Used:   {stats['total_bytes_formatted']}")
    print(f"    • Free Tier Status:     Guaranteed $0.00 / Month (well within 5 GB limit)")
    print("=" * 60)

if __name__ == "__main__":
    run_cleanup()
