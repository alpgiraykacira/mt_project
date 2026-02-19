from datetime import date, datetime, timezone
from flask import Blueprint, request, jsonify
from models import db
from models.development import DevelopmentProject, DevelopmentStage, StageTask

development_bp = Blueprint("development", __name__)


# ── Development Projects CRUD ──

@development_bp.route("/projects", methods=["GET"])
def list_projects():
    """Tüm geliştirme projelerini listele."""
    query = DevelopmentProject.query

    owner = request.args.get("owner")
    status = request.args.get("status")
    priority = request.args.get("priority")

    if owner:
        query = query.filter(DevelopmentProject.owner == owner)
    if status:
        query = query.filter(DevelopmentProject.status == status)
    if priority:
        query = query.filter(DevelopmentProject.priority == priority)

    projects = query.order_by(DevelopmentProject.updated_at.desc()).all()
    return jsonify([p.to_dict(include_stages=True) for p in projects])


@development_bp.route("/projects", methods=["POST"])
def create_project():
    """Yeni geliştirme projesi oluştur. Opsiyonel olarak varsayılan aşamalarla."""
    data = request.get_json()
    project = DevelopmentProject(
        project_name=data["project_name"],
        model_type=data.get("model_type"),
        segment=data.get("segment"),
        owner=data["owner"],
        status=data.get("status", "in_progress"),
        priority=data.get("priority", "medium"),
        start_date=_parse_date(data.get("start_date")),
        target_end_date=_parse_date(data.get("target_end_date")),
        description=data.get("description"),
    )
    db.session.add(project)
    db.session.flush()  # Get the project ID

    # Create default stages if requested
    if data.get("use_default_stages", False):
        _create_default_stages(project.id)

    db.session.commit()
    return jsonify(project.to_dict(include_stages=True)), 201


@development_bp.route("/projects/<int:project_id>", methods=["GET"])
def get_project(project_id):
    """Proje detaylarını aşamalarıyla birlikte getir."""
    project = db.get_or_404(DevelopmentProject, project_id)
    return jsonify(project.to_dict(include_stages=True))


@development_bp.route("/projects/<int:project_id>", methods=["PUT"])
def update_project(project_id):
    """Proje bilgilerini güncelle."""
    project = db.get_or_404(DevelopmentProject, project_id)
    data = request.get_json()

    for field in ["project_name", "model_type", "segment", "owner",
                   "status", "priority", "description"]:
        if field in data:
            setattr(project, field, data[field])

    if "start_date" in data:
        project.start_date = _parse_date(data["start_date"])
    if "target_end_date" in data:
        project.target_end_date = _parse_date(data["target_end_date"])
    if "actual_end_date" in data:
        project.actual_end_date = _parse_date(data["actual_end_date"])

    db.session.commit()
    return jsonify(project.to_dict(include_stages=True))


@development_bp.route("/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    project = db.get_or_404(DevelopmentProject, project_id)
    db.session.delete(project)
    db.session.commit()
    return "", 204


# ── Development Stages ──

@development_bp.route("/projects/<int:project_id>/stages", methods=["POST"])
def create_stage(project_id):
    db.get_or_404(DevelopmentProject, project_id)
    data = request.get_json()
    stage = DevelopmentStage(
        project_id=project_id,
        stage_name=data["stage_name"],
        description=data.get("description"),
        status=data.get("status", "pending"),
        order_index=data.get("order_index", 0),
        deadline=_parse_date(data.get("deadline")),
        notes=data.get("notes"),
    )
    db.session.add(stage)
    db.session.commit()
    return jsonify(stage.to_dict()), 201


@development_bp.route("/projects/<int:project_id>/stages/<int:stage_id>", methods=["PUT"])
def update_stage(project_id, stage_id):
    stage = db.get_or_404(DevelopmentStage, stage_id)
    data = request.get_json()

    for field in ["stage_name", "description", "status", "order_index", "notes"]:
        if field in data:
            setattr(stage, field, data[field])

    if "deadline" in data:
        stage.deadline = _parse_date(data["deadline"])

    if data.get("status") == "completed" and not stage.completed_at:
        stage.completed_at = datetime.now(timezone.utc)

    db.session.commit()
    return jsonify(stage.to_dict())


@development_bp.route("/projects/<int:project_id>/stages/<int:stage_id>", methods=["DELETE"])
def delete_stage(project_id, stage_id):
    stage = db.get_or_404(DevelopmentStage, stage_id)
    db.session.delete(stage)
    db.session.commit()
    return "", 204


# ── Stage Tasks ──

@development_bp.route("/stages/<int:stage_id>/tasks", methods=["POST"])
def create_task(stage_id):
    db.get_or_404(DevelopmentStage, stage_id)
    data = request.get_json()
    task = StageTask(
        stage_id=stage_id,
        task_description=data["task_description"],
        is_completed=data.get("is_completed", False),
        order_index=data.get("order_index", 0),
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@development_bp.route("/stages/<int:stage_id>/tasks/<int:task_id>", methods=["PUT"])
def update_task(stage_id, task_id):
    task = db.get_or_404(StageTask, task_id)
    data = request.get_json()
    if "task_description" in data:
        task.task_description = data["task_description"]
    if "is_completed" in data:
        task.is_completed = data["is_completed"]
    if "order_index" in data:
        task.order_index = data["order_index"]
    db.session.commit()
    return jsonify(task.to_dict())


@development_bp.route("/stages/<int:stage_id>/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(stage_id, task_id):
    task = db.get_or_404(StageTask, task_id)
    db.session.delete(task)
    db.session.commit()
    return "", 204


# ── Owner listesi ──

@development_bp.route("/owners", methods=["GET"])
def list_owners():
    """Tüm benzersiz owner'ları listele."""
    owners = db.session.query(DevelopmentProject.owner).distinct().all()
    return jsonify([o[0] for o in owners if o[0]])


# ── Helpers ──

def _parse_date(date_str):
    if not date_str:
        return None
    return date.fromisoformat(date_str)


def _create_default_stages(project_id):
    """Standart model geliştirme aşamaları."""
    default_stages = [
        ("Veri Hazırlama", "Veri çekme, temizleme ve birleştirme"),
        ("Keşifsel Veri Analizi", "Değişken analizi, korelasyon, dağılım incelemeleri"),
        ("Değişken Seçimi", "WOE/IV analizi, değişken eleme"),
        ("Model Geliştirme", "Model eğitimi, parametre optimizasyonu"),
        ("Model Validasyonu", "Out-of-sample test, stabilite analizi"),
        ("Dokümantasyon", "Technical guide, skorkart dokümanları hazırlama"),
        ("Onay Süreci", "Komite sunumu ve onay"),
        ("Implementasyon", "Canlıya alma ve entegrasyon"),
    ]
    for i, (name, desc) in enumerate(default_stages):
        stage = DevelopmentStage(
            project_id=project_id,
            stage_name=name,
            description=desc,
            order_index=i,
        )
        db.session.add(stage)
