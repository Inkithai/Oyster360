"""
Oyster360 MFA Service
TOTP-based two-factor authentication
"""
import pyotp
import qrcode
import io
import base64
from sqlalchemy.orm import Session
from app.models.user import User

class MFAService:
    def __init__(self, db: Session):
        self.db = db

    def generate_secret(self, user_id: int) -> dict:
        """Generate TOTP secret for user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        # Generate secret
        secret = pyotp.random_base32()
        user.mfa_secret = secret
        self.db.commit()
        
        # Generate QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name="Oyster360"
        )
        
        # Generate QR code image
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "secret": secret,
            "qr_code": f"data:image/png;base64,{qr_code}",
            "provisioning_uri": provisioning_uri
        }

    def verify_token(self, user_id: int, token: str) -> bool:
        """Verify TOTP token"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.mfa_secret:
            return False
        
        totp = pyotp.TOTP(user.mfa_secret)
        return totp.verify(token)

    def enable_mfa(self, user_id: int, token: str) -> bool:
        """Enable MFA after verifying token"""
        if self.verify_token(user_id, token):
            user = self.db.query(User).filter(User.id == user_id).first()
            user.mfa_enabled = True
            self.db.commit()
            return True
        return False

    def disable_mfa(self, user_id: int) -> bool:
        """Disable MFA"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.mfa_enabled = False
            user.mfa_secret = None
            self.db.commit()
            return True
        return False