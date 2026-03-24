from datetime import datetime, timezone
from models import db


class ModelInventory(db.Model):
    """Mevcut model envanteri - temel model bilgileri."""
    __tablename__ = "model_inventory"

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(200), nullable=False)
    scorecard_category = db.Column(db.String(100), nullable=False, index=True)  # Başvuru, Davranış
    product_type = db.Column(db.String(100), index=True)  # KMH, Konut, Kredi Kartı, Oto, Tüketici
    development_period_start = db.Column(db.Date)
    development_period_end = db.Column(db.Date)
    oot_period_start = db.Column(db.Date)
    oot_period_end = db.Column(db.Date)
    validation_submission_date = db.Column(db.Date)  # Modelin validasyona gönderildiği tarih
    development_table = db.Column(db.String(200))
    target_variable = db.Column(db.String(200))
    # Gini değerleri: train/cv/itt/oot/güncel
    gini_development = db.Column(db.Float)   # gini_train ile aynı (geriye dönük uyumluluk)
    gini_train = db.Column(db.Float)         # Train Gini
    gini_cv = db.Column(db.Float)            # Cross-Validation Gini
    gini_itt = db.Column(db.Float)           # In-Time Test Gini
    gini_oot = db.Column(db.Float)           # Out-of-Time Test Gini
    gini_validation = db.Column(db.Float)    # Validasyon Gini (gini_cv ile aynı, geriye dönük uyumluluk)
    gini_current = db.Column(db.Float)       # Güncel Gini (izleme)
    final_score = db.Column(db.Float)
    status = db.Column(db.String(50), default="active", index=True)  # active, retired, under_review
    owner = db.Column(db.String(200), index=True)
    description = db.Column(db.Text)
    connected_processes = db.Column(db.Text)  # Bağlantılı süreçler açıklaması
    dependency_warning = db.Column(db.Text)   # Bağımlılık uyarısı (örn: konut/oto)
    psi_flag = db.Column(db.Boolean, default=False)          # PSI uyarı bayrağı
    alert_work_started = db.Column(db.Boolean, default=False)  # Alert üstüne çalışma başladı mı
    calibration_status = db.Column(db.String(20), default="ok")  # ok | warning | critical
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    technical_details = db.relationship("TechnicalGuide", backref="model", lazy=True, cascade="all, delete-orphan")
    validation_reports = db.relationship("ValidationReport", backref="model", lazy=True, cascade="all, delete-orphan")
    gini_history = db.relationship("GiniHistory", backref="model", lazy=True, cascade="all, delete-orphan")
    rollout_stages = db.relationship("ModelRollout", backref="model", lazy=True, cascade="all, delete-orphan")
    model_variables = db.relationship("ModelVariable", backref="model", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "model_name": self.model_name,
            "scorecard_category": self.scorecard_category,
            "product_type": self.product_type,
            "development_period_start": self.development_period_start.isoformat() if self.development_period_start else None,
            "development_period_end": self.development_period_end.isoformat() if self.development_period_end else None,
            "oot_period_start": self.oot_period_start.isoformat() if self.oot_period_start else None,
            "oot_period_end": self.oot_period_end.isoformat() if self.oot_period_end else None,
            "validation_submission_date": self.validation_submission_date.isoformat() if self.validation_submission_date else None,
            "development_table": self.development_table,
            "target_variable": self.target_variable,
            "gini_development": self.gini_development,
            "gini_train": self.gini_train,
            "gini_cv": self.gini_cv,
            "gini_itt": self.gini_itt,
            "gini_oot": self.gini_oot,
            "gini_validation": self.gini_validation,
            "gini_current": self.gini_current,
            "final_score": self.final_score,
            "status": self.status,
            "owner": self.owner,
            "description": self.description,
            "connected_processes": self.connected_processes,
            "dependency_warning": self.dependency_warning,
            "psi_flag": self.psi_flag,
            "alert_work_started": self.alert_work_started,
            "calibration_status": self.calibration_status or "ok",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TechnicalGuide(db.Model):
    """Teknik kılavuz - sorgular ve değişken hesaplamaları."""
    __tablename__ = "technical_guide"

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey("model_inventory.id"), nullable=False, index=True)
    section_title = db.Column(db.String(300), nullable=False)
    # section_type: query, variable_calc, methodology, note, backscoring, strategy, log, bizu
    section_type = db.Column(db.String(50))
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
    """Validasyon raporları - giden/gelen/wiseminer dosyalar."""
    __tablename__ = "validation_report"

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey("model_inventory.id"), nullable=False, index=True)
    report_name = db.Column(db.String(300), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # incoming, outgoing, wiseminer
    file_path = db.Column(db.String(500))
    file_data = db.Column(db.LargeBinary)   # Gerçek dosya içeriği (upload)
    file_mimetype = db.Column(db.String(100))
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
            "has_file": self.file_data is not None,
            "file_mimetype": self.file_mimetype,
            "report_date": self.report_date.isoformat() if self.report_date else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class GiniHistory(db.Model):
    """Güncel gini değerleri takibi."""
    __tablename__ = "gini_history"

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey("model_inventory.id"), nullable=False, index=True)
    period = db.Column(db.String(20), nullable=False)  # e.g., "2025-Q1", "2025-01"
    gini_value = db.Column(db.Float, nullable=False)
    target_ratio = db.Column(db.Float)   # Hedef oranı (target_oranı)
    sample_size = db.Column(db.Integer)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "model_id": self.model_id,
            "period": self.period,
            "gini_value": self.gini_value,
            "target_ratio": self.target_ratio,
            "sample_size": self.sample_size,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ModelRollout(db.Model):
    """Model implementasyon kademeleri - canlıya çıkma tarihleri."""
    __tablename__ = "model_rollout"

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey("model_inventory.id"), nullable=False, index=True)
    rollout_percentage = db.Column(db.Integer, nullable=False)  # 10, 25, 50, 100
    rollout_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "model_id": self.model_id,
            "rollout_percentage": self.rollout_percentage,
            "rollout_date": self.rollout_date.isoformat() if self.rollout_date else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ModelVariable(db.Model):
    """Model değişkenleri - feature importance ve istatistikler."""
    __tablename__ = "model_variable"

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey("model_inventory.id"), nullable=False, index=True)
    variable_name = db.Column(db.String(200), nullable=False)
    variable_description = db.Column(db.String(500))
    iv_value = db.Column(db.Float)           # Information Value
    importance_rank = db.Column(db.Integer)  # Feature importance sıralaması
    median_train = db.Column(db.Float)       # Train datasından medyan (çok önemli)
    coefficient = db.Column(db.Float)        # Model katsayısı
    woe_bin_count = db.Column(db.Integer)    # WOE bin sayısı
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "model_id": self.model_id,
            "variable_name": self.variable_name,
            "variable_description": self.variable_description,
            "iv_value": self.iv_value,
            "importance_rank": self.importance_rank,
            "median_train": self.median_train,
            "coefficient": self.coefficient,
            "woe_bin_count": self.woe_bin_count,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
