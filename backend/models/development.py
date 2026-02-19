from datetime import datetime, timezone
from models import db


class DevelopmentProject(db.Model):
    """Geliştirilen skorkart projesi."""
    __tablename__ = "development_project"

    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(300), nullable=False)
    model_type = db.Column(db.String(100))  # PD, LGD, EAD, etc.
    segment = db.Column(db.String(200))
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
            "model_type": self.model_type,
            "segment": self.segment,
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
            data["stages"] = [s.to_dict() for s in self.stages]
        return data

    def _calculate_progress(self):
        if not self.stages:
            return 0
        completed = sum(1 for s in self.stages if s.status == "completed")
        return round((completed / len(self.stages)) * 100)


class DevelopmentStage(db.Model):
    """Geliştirme aşaması."""
    __tablename__ = "development_stage"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("development_project.id"), nullable=False)
    stage_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default="pending")  # pending, in_progress, completed, blocked
    order_index = db.Column(db.Integer, default=0)
    deadline = db.Column(db.Date)
    completed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)  # O aşamada neler yapıldı/yapılacak
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    tasks = db.relationship("StageTask", backref="stage", lazy=True,
                            cascade="all, delete-orphan", order_by="StageTask.order_index")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
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
