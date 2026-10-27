from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(80),  unique=True, nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    password_hash= db.Column(db.String(255), nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    analyses     = db.relationship("Analysis", backref="user", lazy=True,
                                   order_by="Analysis.created_at.desc()")

    def to_dict(self):
        return {
            "id":         self.id,
            "username":   self.username,
            "email":      self.email,
            "created_at": self.created_at.strftime("%Y-%m-%d"),
        }


class Analysis(db.Model):
    __tablename__ = "analyses"

    id                  = db.Column(db.Integer, primary_key=True)
    user_id             = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    clause_id           = db.Column(db.String(100))
    clause_title        = db.Column(db.String(255))
    clause_text         = db.Column(db.Text)

    risk_level          = db.Column(db.String(10))
    risk_score          = db.Column(db.Integer)
    risk_category       = db.Column(db.String(50))
    key_issue           = db.Column(db.String(500))
    plain_english_summary = db.Column(db.Text)
    actionable_advice   = db.Column(db.Text)
    suggested_revision  = db.Column(db.Text)

    created_at          = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":                   self.id,
            "clause_id":            self.clause_id,
            "clause_title":         self.clause_title,
            "clause_text":          self.clause_text,
            "risk_level":           self.risk_level,
            "risk_score":           self.risk_score,
            "risk_category":        self.risk_category,
            "key_issue":            self.key_issue,
            "plain_english_summary":self.plain_english_summary,
            "actionable_advice":    self.actionable_advice,
            "suggested_revision":   self.suggested_revision,
            "created_at":           self.created_at.strftime("%b %d, %Y · %H:%M"),
        }
