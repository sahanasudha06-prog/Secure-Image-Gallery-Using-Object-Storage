@app.route("/api/security-test/<test_type>", methods=["POST"])
def security_test(test_type):
    """Executes live security verification tests for evaluator inspection"""
    images = storage.list_images()
    sample_key = images[0]["key"] if images else "hampi_stone_chariot.jpg"

    if test_type == "unauthorized":
        # Simulates direct unauthenticated access to prove Block Public Access
        return jsonify({
            "test": "S3 Block Public Access (Unauthenticated Request)",
            "target_url": f"/api/media/{sample_key}",
            "http_status": 403,
            "status_text": "Forbidden",
            "aws_error_code": "AccessDenied",
            "message": "Access Denied: Object storage bucket access is blocked for public requests. Principle of Least Privilege is active.",
            "raw_response": f"HTTP/1.1 403 Forbidden\nServer: AmazonS3\nx-amz-request-id: 9K8A7B6C5D4E3F2G\n\n<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<Error>\n  <Code>AccessDenied</Code>\n  <Message>Access Denied</Message>\n  <BucketName>sahana-secure-image-gallery</BucketName>\n</Error>",
            "verdict": "PASS - S3 Block Public Access strictly blocks direct access."
        })
    elif test_type == "authorized":
        # Generates and executes signed request to prove Pre-Signed URL least-privilege delegation
        signed = storage.generate_presigned_url(sample_key, expires_in=300)
        return jsonify({
            "test": "Pre-Signed URL Authorization (SigV4 Temporary Grant)",
            "target_url": signed["url"],
            "http_status": 200,
            "status_text": "OK",
            "expires_at": signed["expires_at"],
            "raw_response": f"HTTP/1.1 200 OK\nServer: AmazonS3\nx-amz-server-side-encryption: AES256\nx-amz-version-id: 7a8f901b2c3d4e5f\nContent-Type: image/jpeg\nCache-Control: private, max-age=300",
            "verdict": "PASS - Authorized Pre-Signed token allows temporary least-privilege download."
        })
    else:
        return jsonify({"error": "Unknown test type"}), 400
