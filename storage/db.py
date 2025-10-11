import os
from typing import List, Optional
import logging
from dataclasses import dataclass
from datetime import datetime
from pymongo import MongoClient
from passlib.context import CryptContext
from bson.objectid import ObjectId

# Attempt to use system CA certificates for TLS connections (e.g., MongoDB Atlas)
try:
    import certifi  # type: ignore
    _CA_FILE = certifi.where()
except Exception:  # pragma: no cover - optional dependency
    certifi = None  # type: ignore
    _CA_FILE = None

# Password hashing context
# Use pbkdf2_sha256 to avoid bcrypt backend issues & 72-byte limit
# Note: Existing users hashed with bcrypt won't validate; recreate them.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

@dataclass
class ReportRecord:
    report_id: str
    created_at: str
    issue_type: str
    text: Optional[str]
    voice_text: Optional[str]
    image_path: Optional[str]
    location: dict
    complaint_text: str
    status: str
    fake: bool
    fake_score: float
    username: Optional[str] = None

class CivicDB:
    def __init__(self):
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB", "civic_eye")
        try:
            # Build connection kwargs. Use CA bundle for Atlas/SRV URIs to avoid SSL handshake issues.
            conn_kwargs = {
                "serverSelectionTimeoutMS": 5000,
            }
            # Heuristic: SRV scheme or mongodb.net host implies TLS is required
            if mongodb_uri.startswith("mongodb+srv://") or "mongodb.net" in mongodb_uri:
                if _CA_FILE:
                    conn_kwargs["tlsCAFile"] = _CA_FILE
                else:
                    logging.getLogger(__name__).warning(
                        "certifi is not installed; TLS handshake with Atlas may fail. "
                        "Install with: pip install certifi"
                    )
            self.client = MongoClient(mongodb_uri, **conn_kwargs)
            # Force a ping early so connection issues show up immediately
            self.client.admin.command("ping")
            self.db = self.client[db_name]
            logging.getLogger(__name__).info("Connected to MongoDB: %s/%s", mongodb_uri, db_name)
        except Exception as exc:
            logging.getLogger(__name__).exception("MongoDB connection failed: %s", exc)
            self.client = None
            self.db = None

    def is_connected(self) -> bool:
        return self.db is not None
        
    def find_user(self, username: str) -> Optional[dict]:
        """Find a user by username"""
        if self.db is None:
            return None
        try:
            return self.db.users.find_one({"username": username})
        except Exception:
            logging.getLogger(__name__).exception("Error finding user")
            return None
    
    def verify_password(self, user: dict, password: str) -> bool:
        """Verify password hash"""
        try:
            return pwd_context.verify(password, user.get("password", ""))
        except Exception:
            logging.getLogger(__name__).exception("Password verification failed")
            return False
    
    def create_user(self, username: str, email: str, password: str, name: str, role: str = "citizen") -> bool:
        """Create a new user"""
        if self.db is None:
            logging.getLogger(__name__).error("Cannot create user: DB not connected")
            return False
        if self.find_user(username):
            return False
        try:
            user = {
                "username": username,
                "email": email,
                "password": pwd_context.hash(password),
                "name": name,
                "role": role,
                "created_at": datetime.utcnow()
            }
            result = self.db.users.insert_one(user)
            return bool(result.inserted_id)
        except Exception:
            logging.getLogger(__name__).exception("Error creating user")
            return False
    
    def save_report(self, record: ReportRecord) -> bool:
        """Save a new report"""
        if self.db is None:
            logging.getLogger(__name__).error("Cannot save report: DB not connected")
            return False
        try:
            doc = {
                "report_id": record.report_id,
                "created_at": record.created_at,
                "issue_type": record.issue_type,
                "text": record.text,
                "voice_text": record.voice_text,
                "image_path": record.image_path,
                "location": record.location,
                "complaint_text": record.complaint_text,
                "status": record.status,
                "fake": record.fake,
                "fake_score": record.fake_score,
                "username": record.username
            }
            logging.getLogger(__name__).info(f"Saving report with ID: {record.report_id}")
            result = self.db.reports.insert_one(doc)
            success = bool(result.inserted_id)
            logging.getLogger(__name__).info(f"Report saved successfully: {success}")
            return success
        except Exception:
            logging.getLogger(__name__).exception("Error saving report")
            return False
    
    def get_report(self, report_id: str) -> Optional[ReportRecord]:
        """Get a report by ID (case-insensitive)"""
        if self.db is None:
            logging.getLogger(__name__).error("Cannot get report: DB not connected")
            return None
        try:
            # Make search case-insensitive
            report_id = report_id.strip().lower()
            logging.getLogger(__name__).info(f"Searching for report ID: {report_id}")
            doc = self.db.reports.find_one({"report_id": report_id})
            if not doc:
                logging.getLogger(__name__).warning(f"Report not found: {report_id}")
                # Debug: check what reports exist
                count = self.db.reports.count_documents({})
                logging.getLogger(__name__).info(f"Total reports in DB: {count}")
                return None
            # Drop Mongo's internal _id before constructing dataclass
            doc.pop("_id", None)
            logging.getLogger(__name__).info(f"Report found: {report_id}")
            return ReportRecord(**doc)
        except Exception:
            logging.getLogger(__name__).exception("Error getting report")
            return None
    
    def list_reports(self, limit: int = 100) -> List[ReportRecord]:
        """List recent reports"""
        if self.db is None:
            return []
        try:
            docs = self.db.reports.find().sort("created_at", -1).limit(limit)
            cleaned = []
            for doc in docs:
                doc.pop("_id", None)
                cleaned.append(ReportRecord(**doc))
            return cleaned
        except Exception:
            logging.getLogger(__name__).exception("Error listing reports")
            return []
    
    def update_status(self, report_id: str, new_status: str) -> bool:
        """Update report status"""
        if self.db is None:
            logging.getLogger(__name__).error("Cannot update status: DB not connected")
            return False
        result = self.db.reports.update_one(
            {"report_id": report_id},
            {"$set": {"status": new_status}}
        )
        return result.modified_count > 0
    
    def list_authorities(self) -> List[dict]:
        """List all authority users"""
        if self.db is None:
            return []
        return list(self.db.users.find({"role": "authority"}))
    
    def get_user_reports(self, username: str) -> List[ReportRecord]:
        """Get all reports by a specific user"""
        if self.db is None or not username:
            return []
        try:
            docs = self.db.reports.find({"username": username}).sort("created_at", -1)
            cleaned = []
            for doc in docs:
                doc.pop("_id", None)
                # Handle missing username field in old records
                if "username" not in doc:
                    doc["username"] = None
                cleaned.append(ReportRecord(**doc))
            return cleaned
        except Exception:
            logging.getLogger(__name__).exception("Error getting user reports")
            return []
    
    def get_user_points(self, username: str) -> int:
        """Calculate civic points for user based on verified complaints + manual adjustments"""
        if self.db is None or not username:
            return 0
        try:
            resolved_count = self.db.reports.count_documents({
                "username": username, 
                "status": "resolved",
                "fake": False
            })
            auto_points = resolved_count * 10  # 10 points per resolved complaint
            manual_points = self.get_user_manual_points(username)
            return auto_points + manual_points
        except Exception:
            logging.getLogger(__name__).exception("Error calculating user points")
            return 0
    
    def get_leaderboard(self, limit: int = 10) -> List[dict]:
        """Get top users by civic points"""
        if self.db is None:
            return []
        try:
            pipeline = [
                {"$match": {"status": "resolved", "fake": False, "username": {"$exists": True, "$ne": None}}},
                {"$group": {
                    "_id": "$username",
                    "points": {"$sum": 10},
                    "complaints": {"$sum": 1}
                }},
                {"$sort": {"points": -1}},
                {"$limit": limit}
            ]
            return list(self.db.reports.aggregate(pipeline))
        except Exception:
            logging.getLogger(__name__).exception("Error getting leaderboard")
            return []
    
    def get_user_notifications(self, username: str) -> List[dict]:
        """Get recent notifications for user"""
        if self.db is None or not username:
            return []
        try:
            recent_reports = self.db.reports.find(
                {"username": username}, 
                {"report_id": 1, "status": 1, "created_at": 1}
            ).sort("created_at", -1).limit(5)
            
            notifications = []
            for report in recent_reports:
                if report.get("status") == "resolved":
                    notifications.append({
                        "message": f"Complaint {report.get('report_id', 'Unknown')} marked as Resolved ✅",
                        "type": "success",
                        "date": report.get("created_at", "")
                    })
                elif report.get("status") == "in_progress":
                    notifications.append({
                        "message": f"Complaint {report.get('report_id', 'Unknown')} is now In Progress 🔄",
                        "type": "info", 
                        "date": report.get("created_at", "")
                    })
            return notifications
        except Exception:
            logging.getLogger(__name__).exception("Error getting notifications")
            return []
    
    def get_all_users_with_stats(self) -> List[dict]:
        """Get all users with their complaint statistics"""
        if self.db is None:
            return []
        try:
            users = list(self.db.users.find({}, {"password": 0}))  # Exclude password
            
            for user in users:
                username = user.get("username")
                if username:
                    # Get user reports
                    user_reports = self.get_user_reports(username)
                    
                    # Calculate stats
                    total_complaints = len(user_reports)
                    resolved_complaints = len([r for r in user_reports if r.status == 'resolved'])
                    pending_complaints = len([r for r in user_reports if r.status in ['submitted', 'in_progress']])
                    fake_complaints = len([r for r in user_reports if r.fake])
                    
                    # Get civic points
                    civic_points = self.get_user_points(username)
                    
                    # Add stats to user object
                    user['total_complaints'] = total_complaints
                    user['resolved_complaints'] = resolved_complaints
                    user['pending_complaints'] = pending_complaints
                    user['fake_complaints'] = fake_complaints
                    user['civic_points'] = civic_points
                    user['recent_reports'] = user_reports[:5]  # Last 5 reports
                else:
                    user['total_complaints'] = 0
                    user['resolved_complaints'] = 0
                    user['pending_complaints'] = 0
                    user['fake_complaints'] = 0
                    user['civic_points'] = 0
                    user['recent_reports'] = []
            
            return users
        except Exception:
            logging.getLogger(__name__).exception("Error getting all users with stats")
            return []
    
    def adjust_user_points(self, username: str, points_delta: int) -> bool:
        """Manually adjust user points (admin only)"""
        if self.db is None or not username:
            return False
        try:
            # Get current points
            current_points = self.get_user_points(username)
            
            # Store manual adjustment in user document
            result = self.db.users.update_one(
                {"username": username},
                {
                    "$inc": {"manual_points": points_delta},
                    "$set": {"last_points_update": datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception:
            logging.getLogger(__name__).exception("Error adjusting user points")
            return False
    
    def get_user_manual_points(self, username: str) -> int:
        """Get manually adjusted points for a user"""
        if self.db is None or not username:
            return 0
        try:
            user = self.db.users.find_one({"username": username})
            return user.get("manual_points", 0) if user else 0
        except Exception:
            logging.getLogger(__name__).exception("Error getting manual points")
            return 0
    
    def delete_report(self, report_id: str) -> bool:
        """Delete a report (admin only)"""
        if self.db is None or not report_id:
            return False
        try:
            result = self.db.reports.delete_one({"report_id": report_id})
            return result.deleted_count > 0
        except Exception:
            logging.getLogger(__name__).exception("Error deleting report")
            return False
