from datetime import datetime, timezone
from models import db


class ModelInventory(db.Model):
    """Mevcut model envanteri - temel model bilgileri."""
    __tablename__ = "model_inventory"

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(200), nullable=False)
    model_type = db.Column(db.String(100), nullable=False)  # PD, LGD, EAD, etc.
    segment = db.Column(db.String(200))
    development_period_start = db.Column(db.Date)
    development_period_end = db.Column(db.Date)
    development_table = db.Column(db.String(200))
    target_variable = db.Column(db.String(200))
    gini_development = db.Column(db.Float)
    gini_validation = db.Column(db.Float)
    gini_current = db.Column(db.Float)
    final_score = db.Column(db.Float)
    status = db.Column(db.String(50), default="active")  # active, retired, under_review
    owner = db.Column(db.String(200))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    technical_details = db.relationship("TechnicalGuide", backref="model", lazy=True, cascade="all, delete-orphan")
    validation_reports = db.relationship("ValidationReport", backref="model", lazy=True, cascade="all, delete-orphan")
    gini_history = db.relationship("GiniHistory", backref="model", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "model_name": self.model_name,
            "model_type": self.model_type,
            "segment": self.segment,
            "development_period_start": self.development_period_start.isoformat() if self.development_period_start else None,
            "development_period_end": self.development_period_end.isoformat() if self.development_period_end else None,
            "development_table": self.development_table,
            "target_variable": self.target_variable,
            "gini_development": self.gini_development,
            "gini_validation": self.gini_validation,
            "gini_current": self.gini_current,
            "final_score": self.final_score,
            "status": self.status,
            "owner": self.owner,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TechnicalGuide(db.Model):
    """Teknik kılavuz - sorgular ve değişken hesaplamaları."""
    __tablename__ = "technical_guide"

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey("model_inventory.id"), nullable=False)
    section_title = db.Column(db.String(300), nullable=False)
    section_type = db.Column(db.String(50))  # query, variable_calc, methodology, note
    content = db.Column(db.Text, nullable=False)
    query_code = db.Column(db.Text)  # SQL query or calculation code
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "model_id": self.model_id,
            "section_title": self.section_title,
            "section_type": self.section_type,
            "content": self.content,
            "query_code": self.query_code,
            "order_index": self.order_index,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ValidationReport(db.Model):
    """Validasyon raporları - giden/gelen dosyalar."""
    __tablename__ = "validation_report"

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey("model_inventory.id"), nullable=False)
    report_name = db.Column(db.String(300), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # incoming, outgoing
    file_path = db.Column(db.String(500))
    report_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "model_id": self.model_id,
            "report_name": self.report_name,
            "report_type": self.report_type,
            "file_path": self.file_path,
            "report_date": self.report_date.isoformat() if self.report_date else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class GiniHistory(db.Model):
    """Güncel gini değerleri takibi."""
    __tablename__ = "gini_history"

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey("model_inventory.id"), nullable=False)
    period = db.Column(db.String(20), nullable=False)  # e.g., "2025-Q1", "2025-01"
    gini_value = db.Column(db.Float, nullable=False)
    sample_size = db.Column(db.Integer)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "model_id": self.model_id,
            "period": self.period,
            "gini_value": self.gini_value,
            "sample_size": self.sample_size,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
