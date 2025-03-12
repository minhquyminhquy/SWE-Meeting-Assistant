from app import db
from datetime import datetime
import uuid

class Meeting(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    recording_filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    transcript = db.Column(db.Text, nullable=True)
    summary = db.Column(db.Text, nullable=True)
    decisions = db.Column(db.Text, nullable=True)
    action_items = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    error = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "original_filename": self.original_filename,
            "transcript": self.transcript,
            "summary": self.summary,
            "decisions": self.decisions,
            "action_items": self.action_items,
            "created_at": self.created_at.isoformat(),
            "processed": self.processed,
            "error": self.error
        }
