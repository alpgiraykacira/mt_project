from datetime import datetime, timezone
from models import db


class DevelopmentProject(db.Model):
    """Geliştirilen skorkart projesi."""
    __tablename__ = "development_project"

    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(300), nullable=False)
    scorecard_category = db.Column(db.String(100))  # Başvuru, Davranış
    product_type = db.Column(db.String(100))  # KMH, Konut, Kredi Kartı, Oto, Tüketici
    owner = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default="in_progress")  # in_progress, completed, on_hold, cancelled
    priority = db.Column(db.String(20), default="medium")  # low, medium, high, critical
    start_date = db.Column(db.Date)
    target_end_date = db.Column(db.Date)
    actual_end_date = db.Column(db.Date)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    stages = db.relationship("DevelopmentStage", backref="project", lazy=True,
                             cascade="all, delete-orphan", order_by="DevelopmentStage.order_index")

    def to_dict(self, include_stages=False):
        data = {
            "id": self.id,
            "project_name": self.project_name,
            "scorecard_category": self.scorecard_category,
            "product_type": self.product_type,
            "owner": self.owner,
            "status": self.status,
            "priority": self.priority,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "target_end_date": self.target_end_date.isoformat() if self.target_end_date else None,
            "actual_end_date": self.actual_end_date.isoformat() if self.actual_end_date else None,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "progress": self._calculate_progress(),
        }
        if include_stages:
            # Only top-level stages; children are nested inside each stage's to_dict
            data["stages"] = [s.to_dict() for s in self.stages if s.parent_id is None]
        return data

    def _calculate_progress(self):
        if not self.stages:
            return 0
        # Only count top-level stages (no parent) for progress
        top_stages = [s for s in self.stages if s.parent_id is None]
        if not top_stages:
            return 0
        completed = sum(1 for s in top_stages if s.status == "completed")
        return round((completed / len(top_stages)) * 100)


class DevelopmentStage(db.Model):
    """Geliştirme aşaması."""
    __tablename__ = "development_stage"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("development_project.id"), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("development_stage.id"), nullable=True)
    stage_code = db.Column(db.String(20))  # "1", "3.1", "3.1.2" etc.
    stage_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default="pending")  # pending, in_progress, completed, blocked
    order_index = db.Column(db.Integer, default=0)
    deadline = db.Column(db.Date)
    completed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)  # O aşamada neler yapıldı/yapılacak
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    children = db.relationship("DevelopmentStage", backref=db.backref("parent", remote_side="DevelopmentStage.id"),
                               lazy=True, cascade="all, delete-orphan",
                               order_by="DevelopmentStage.order_index")
    tasks = db.relationship("StageTask", backref="stage", lazy=True,
                            cascade="all, delete-orphan", order_by="StageTask.order_index")

    def to_dict(self, include_children=True):
        data = {
            "id": self.id,
            "project_id": self.project_id,
            "parent_id": self.parent_id,
            "stage_code": self.stage_code,
            "stage_name": self.stage_name,
            "description": self.description,
            "status": self.status,
            "order_index": self.order_index,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "tasks": [t.to_dict() for t in self.tasks],
        }
        if include_children:
            data["children"] = [c.to_dict(include_children=True) for c in self.children]
        return data


class StageTask(db.Model):
    """Aşama içindeki görevler - neler yapıldı/yapılacak."""
    __tablename__ = "stage_task"

    id = db.Column(db.Integer, primary_key=True)
    stage_id = db.Column(db.Integer, db.ForeignKey("development_stage.id"), nullable=False)
    task_description = db.Column(db.String(500), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "stage_id": self.stage_id,
            "task_description": self.task_description,
            "is_completed": self.is_completed,
            "order_index": self.order_index,
        }
