"""
Oyster360 File Service
Handles file uploads with validation
"""
import os
from fastapi import UploadFile, HTTPException
from typing import List
import uuid

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

class FileService:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)

    async def upload_file(self, file: UploadFile, user_id: int) -> dict:
        """Upload and validate file"""
        # Validate file extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        # Validate file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")
        
        # Generate unique filename
        filename = f"{user_id}_{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(self.upload_dir, filename)
        
        # Save file
        with open(filepath, "wb") as f:
            f.write(content)
        
        return {
            "filename": filename,
            "original_name": file.filename,
            "size": len(content),
            "url": f"/uploads/{filename}"
        }