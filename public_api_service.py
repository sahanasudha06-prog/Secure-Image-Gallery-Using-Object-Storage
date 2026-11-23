import urllib.request
import json
import io
import time
from werkzeug.utils import secure_filename

class PublicApiService:
    """
    Integrates verified free & open APIs from public-apis (https://github.com/public-apis/public-apis)
    to ingest real-world media assets securely into Amazon S3 / Object Storage.
    """

    @staticmethod
    def _fetch_url(url, timeout=6):
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json,image/*,*/*"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read(), response.info().get_content_type()

    @classmethod
    def fetch_nasa_apod(cls):
        """NASA Astronomy Picture of the Day API with graceful open backup"""
        try:
            api_url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"
            raw_json, _ = cls._fetch_url(api_url)
            data = json.loads(raw_json.decode("utf-8"))
            img_url = data.get("hdurl") or data.get("url")
            title = data.get("title", "NASA Astronomy Picture")
            date_str = data.get("date", str(int(time.time())))
        except Exception:
            # Fallback to high-res cosmic astronomy archive
            img_url = "https://images-assets.nasa.gov/image/PIA12348/PIA12348~orig.jpg"
            title = "NASA Spitzer Space Telescope Nebula"
            date_str = "2026-Cosmic"

        img_bytes, mime_type = cls._fetch_url(img_url)
        clean_name = secure_filename(f"nasa_{date_str}_{title[:20]}.jpg".replace(" ", "_").lower())

        return {
            "bytes": img_bytes,
            "filename": clean_name,
            "mime_type": mime_type or "image/jpeg",
            "category": "Science & Space",
            "source": "NASA Open Space API",
            "title": title,
            "metadata": {
                "source_api": "NASA Space API",
                "title": title
            }
        }

    @classmethod
    def fetch_dog_ceo(cls):
        """Dog CEO Free Animals API (Public API - Animals)"""
        api_url = "https://dog.ceo/api/breeds/image/random"
        raw_json, _ = cls._fetch_url(api_url)
        data = json.loads(raw_json.decode("utf-8"))
        img_url = data.get("message")
        
        img_bytes, mime_type = cls._fetch_url(img_url)
        breed = img_url.split("/")[-2].replace("-", " ").title() if "/" in img_url else "Dog"
        filename = f"dog_{int(time.time())}_{secure_filename(breed)}.jpg"

        return {
            "bytes": img_bytes,
            "filename": filename,
            "mime_type": mime_type or "image/jpeg",
            "category": "Nature",
            "source": "Dog CEO Open API",
            "title": f"Breed: {breed}",
            "metadata": {
                "source_api": "Dog CEO API",
                "breed": breed
            }
        }

    @classmethod
    def fetch_curated_photos(cls, count=10):
        """Lorem Picsum Open Photo Catalog (Public API - Photography)"""
        try:
            api_url = f"https://picsum.photos/v2/list?page=1&limit={count}"
            raw_json, _ = cls._fetch_url(api_url)
            items = json.loads(raw_json.decode("utf-8"))
            results = []
            for item in items:
                results.append({
                    "id": item.get("id"),
                    "author": item.get("author"),
                    "preview_url": f"https://picsum.photos/id/{item.get('id')}/500/350",
                    "download_url": item.get("download_url"),
                    "width": item.get("width"),
                    "height": item.get("height"),
                    "source": "Lorem Picsum Open Photography"
                })
            return results
        except Exception:
            # Fallback direct curated image
            return [{
                "id": "10",
                "author": "Paul Jarvis",
                "preview_url": "https://picsum.photos/id/10/500/350",
                "download_url": "https://picsum.photos/id/10/1200/800",
                "source": "Lorem Picsum Photography"
            }]

    @classmethod
    def ingest_from_custom_url(cls, target_url, custom_name=None, category="Imported"):
        """Imports an image from any public URL into private object storage"""
        img_bytes, mime_type = cls._fetch_url(target_url)
        if not custom_name:
            ext = "jpg"
            if "png" in mime_type:
                ext = "png"
            elif "webp" in mime_type:
                ext = "webp"
            custom_name = f"web_import_{int(time.time())}.{ext}"
        else:
            custom_name = secure_filename(custom_name)

        return {
            "bytes": img_bytes,
            "filename": custom_name,
            "mime_type": mime_type or "image/jpeg",
            "category": category,
            "source": "Public Web API Ingestion",
            "title": custom_name,
            "metadata": {
                "source_api": "Web URL Ingest",
                "origin_url": target_url
            }
        }
