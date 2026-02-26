"""Demo verisi yüklemek için script. Çalıştırmak için: python seed_data.py"""

from datetime import date
from models import db
from models.scorecard import ModelInventory, TechnicalGuide, ValidationReport, GiniHistory
from models.development import DevelopmentProject, DevelopmentStage, StageTask


def seed_db():
    """Seed logic only — must be called inside an active app context."""

    # ── Mevcut Modeller ──
    m1 = ModelInventory(
        model_name="Retail PD Scorecard v3.2",
        model_type="PD",
        segment="Bireysel - Genel Amaçlı",
        development_period_start=date(2023, 1, 15),
        development_period_end=date(2023, 6, 30),
        development_table="RETAIL_DEV_202301",
        target_variable="default_flag_12m",
        gini_development=0.62,
        gini_validation=0.58,
        gini_current=0.55,
        final_score=0.87,
        status="active",
        owner="Alp Giray Kaçıra",
        description="Bireysel müşteriler için 12 aylık temerrüt olasılığı modeli.",
    )
    m2 = ModelInventory(
        model_name="SME LGD Model v2.0",
        model_type="LGD",
        segment="KOBİ",
        development_period_start=date(2022, 7, 1),
        development_period_end=date(2022, 12, 31),
        development_table="SME_LGD_DEV_202207",
        target_variable="loss_rate",
        gini_development=0.48,
        gini_validation=0.44,
        gini_current=0.42,
        final_score=0.78,
        status="active",
        owner="Ahmet Yılmaz",
        description="KOBİ segmenti için kayıp oranı tahmin modeli.",
    )
    m3 = ModelInventory(
        model_name="Credit Card Behavioural Score",
        model_type="Behavioural",
        segment="Bireysel - Kredi Kartı",
        development_period_start=date(2024, 1, 10),
        development_period_end=date(2024, 5, 15),
        development_table="CC_BEH_DEV_202401",
        target_variable="dpd_90plus_6m",
        gini_development=0.71,
        gini_validation=0.67,
        gini_current=0.65,
        final_score=0.92,
        status="active",
        owner="Elif Demir",
        description="Kredi kartı müşterileri için davranışsal skor modeli.",
    )
    m4 = ModelInventory(
        model_name="Mortgage Application Score v1.0",
        model_type="Application",
        segment="Bireysel - Konut",
        development_period_start=date(2021, 3, 1),
        development_period_end=date(2021, 9, 30),
        development_table="MORTGAGE_APP_DEV_2021",
        target_variable="default_flag_24m",
        gini_development=0.55,
        gini_validation=0.51,
        gini_current=0.38,
        final_score=0.72,
        status="under_review",
        owner="Ahmet Yılmaz",
        description="Konut kredisi başvuru skoru - performans düşüşü nedeniyle inceleniyor.",
    )
    m5 = ModelInventory(
        model_name="Commercial EAD Model v1.5",
        model_type="EAD",
        segment="Ticari",
        development_period_start=date(2020, 6, 1),
        development_period_end=date(2020, 12, 31),
        development_table="COMM_EAD_DEV_2020",
        target_variable="ead_ratio",
        gini_development=0.41,
        gini_validation=0.38,
        gini_current=0.35,
        final_score=0.68,
        status="retired",
        owner="Elif Demir",
    )
    db.session.add_all([m1, m2, m3, m4, m5])
    db.session.flush()

    # ── Technical Guides ──
    for model in [m1, m3]:
        guides = [
            TechnicalGuide(
                model_id=model.id,
                section_title="Veri Çekme Sorgusu",
                section_type="query",
                content="Ana geliştirme veri seti için kullanılan sorgu.",
                query_code=f"SELECT * FROM {model.development_table}\nWHERE observation_date BETWEEN '2023-01-01' AND '2023-06-30'\n  AND segment = '{model.segment}';",
                order_index=0,
            ),
            TechnicalGuide(
                model_id=model.id,
                section_title="WOE Hesaplama Metodolojisi",
                section_type="methodology",
                content="Weight of Evidence (WOE) hesaplaması için fine classing ve coarse classing adımları uygulanmıştır. IV > 0.02 olan değişkenler ön seçime dahil edilmiştir.",
                order_index=1,
            ),
            TechnicalGuide(
                model_id=model.id,
                section_title="Final Değişken Listesi",
                section_type="variable_calc",
                content="Modelde kullanılan değişkenler ve dönüştürme formülleri.",
                query_code="-- Değişken 1: Toplam Bakiye / Limit Oranı\nCASE WHEN limit_amount > 0 THEN total_balance / limit_amount ELSE 0 END AS utilization_ratio\n\n-- Değişken 2: Son 6 ay gecikme sayısı\nSUM(CASE WHEN dpd > 0 THEN 1 ELSE 0 END) OVER (PARTITION BY customer_id ORDER BY period ROWS 5 PRECEDING) AS dpd_count_6m",
                order_index=2,
            ),
        ]
        db.session.add_all(guides)

    # ── Validation Reports ──
    for model in [m1, m2, m3]:
        reports = [
            ValidationReport(
                model_id=model.id,
                report_name=f"{model.model_name} - Geliştirme Validasyon Raporu",
                report_type="outgoing",
                file_path=f"/reports/validation/{model.development_table}_validation.pdf",
                report_date=model.development_period_end,
                notes="Bağımsız validasyon birimine gönderilen rapor.",
            ),
            ValidationReport(
                model_id=model.id,
                report_name=f"{model.model_name} - Validasyon Sonuç Raporu",
                report_type="incoming",
                file_path=f"/reports/validation/{model.development_table}_result.pdf",
                report_date=model.development_period_end,
                notes="Validasyon biriminden gelen onay raporu.",
            ),
        ]
        db.session.add_all(reports)

    # ── Gini History ──
    gini_data = {
        m1.id: [
            ("2023-Q3", 0.60), ("2023-Q4", 0.59), ("2024-Q1", 0.58),
            ("2024-Q2", 0.57), ("2024-Q3", 0.56), ("2024-Q4", 0.55),
            ("2025-Q1", 0.55),
        ],
        m2.id: [
            ("2023-Q1", 0.46), ("2023-Q2", 0.45), ("2023-Q3", 0.44),
            ("2023-Q4", 0.43), ("2024-Q1", 0.43), ("2024-Q2", 0.42),
        ],
        m3.id: [
            ("2024-Q3", 0.66), ("2024-Q4", 0.66), ("2025-Q1", 0.65),
        ],
    }
    for model_id, records in gini_data.items():
        for period, gini_val in records:
            db.session.add(GiniHistory(
                model_id=model_id, period=period,
                gini_value=gini_val, sample_size=15000,
            ))

    # ── Geliştirme Projeleri ──
    p1 = DevelopmentProject(
        project_name="Retail PD v4.0 Geliştirme",
        model_type="PD",
        segment="Bireysel - Genel Amaçlı",
        owner="Alp Giray Kaçıra",
        status="in_progress",
        priority="high",
        start_date=date(2025, 9, 1),
        target_end_date=date(2026, 3, 31),
        description="Mevcut PD v3.2 modelinin yenilenmesi. Yeni değişkenler ve ML teknikleri eklenecek.",
    )
    p2 = DevelopmentProject(
        project_name="KOBİ Behavioural Score",
        model_type="Behavioural",
        segment="KOBİ",
        owner="Ahmet Yılmaz",
        status="in_progress",
        priority="medium",
        start_date=date(2025, 11, 1),
        target_end_date=date(2026, 5, 31),
        description="KOBİ segmenti için yeni davranışsal skor modeli geliştirmesi.",
    )
    p3 = DevelopmentProject(
        project_name="Mortgage PD Model Yenileme",
        model_type="PD",
        segment="Bireysel - Konut",
        owner="Elif Demir",
        status="in_progress",
        priority="critical",
        start_date=date(2025, 7, 1),
        target_end_date=date(2026, 1, 31),
        description="Performans düşüşü olan konut kredisi PD modelinin yenilenmesi.",
    )
    db.session.add_all([p1, p2, p3])
    db.session.flush()

    # ── Aşamalar ve Görevler ──
    stages_config = [
        ("Veri Hazırlama", "Veri çekme, temizleme ve birleştirme"),
        ("Keşifsel Veri Analizi", "Değişken analizi, korelasyon, dağılım incelemeleri"),
        ("Değişken Seçimi", "WOE/IV analizi, değişken eleme"),
        ("Model Geliştirme", "Model eğitimi, parametre optimizasyonu"),
        ("Model Validasyonu", "Out-of-sample test, stabilite analizi"),
        ("Dokümantasyon", "Technical guide, skorkart dokümanları hazırlama"),
        ("Onay Süreci", "Komite sunumu ve onay"),
        ("Implementasyon", "Canlıya alma ve entegrasyon"),
    ]

    # p1: Aşama 4'te (model geliştirme) - ilk 3 tamamlandı
    for i, (name, desc) in enumerate(stages_config):
        status = "completed" if i < 3 else ("in_progress" if i == 3 else "pending")
        deadline = date(2025, 10 + i if 10 + i <= 12 else i - 2, 15) if i < 6 else date(2026, i - 4, 28)
        stage = DevelopmentStage(
            project_id=p1.id, stage_name=name, description=desc,
            status=status, order_index=i, deadline=deadline,
        )
        db.session.add(stage)
        db.session.flush()
        if i == 3:
            tasks = [
                StageTask(stage_id=stage.id, task_description="Logistic regression baseline model", is_completed=True, order_index=0),
                StageTask(stage_id=stage.id, task_description="XGBoost model denemesi", is_completed=True, order_index=1),
                StageTask(stage_id=stage.id, task_description="Ensemble model karşılaştırması", is_completed=False, order_index=2),
                StageTask(stage_id=stage.id, task_description="Final model seçimi ve kalibrasyon", is_completed=False, order_index=3),
            ]
            db.session.add_all(tasks)

    # p2: Aşama 2'de (EDA) - ilk 1 tamamlandı
    for i, (name, desc) in enumerate(stages_config):
        status = "completed" if i < 1 else ("in_progress" if i == 1 else "pending")
        stage = DevelopmentStage(
            project_id=p2.id, stage_name=name, description=desc,
            status=status, order_index=i,
            deadline=date(2025, 12 + i if 12 + i <= 12 else i, 15) if i < 4 else date(2026, i - 1, 28),
        )
        db.session.add(stage)

    # p3: Aşama 6'da (Dokümantasyon) - ilk 5 tamamlandı
    for i, (name, desc) in enumerate(stages_config):
        status = "completed" if i < 5 else ("in_progress" if i == 5 else "pending")
        stage = DevelopmentStage(
            project_id=p3.id, stage_name=name, description=desc,
            status=status, order_index=i,
            deadline=date(2025, 8 + i if 8 + i <= 12 else i - 4, 15),
        )
        db.session.add(stage)

    db.session.commit()
    print("Seed data loaded successfully!")
    print(f"  - {ModelInventory.query.count()} models")
    print(f"  - {TechnicalGuide.query.count()} technical guide sections")
    print(f"  - {ValidationReport.query.count()} validation reports")
    print(f"  - {GiniHistory.query.count()} gini history records")
    print(f"  - {DevelopmentProject.query.count()} development projects")
    print(f"  - {DevelopmentStage.query.count()} development stages")
    print(f"  - {StageTask.query.count()} tasks")


def seed():
    """Standalone entry point: creates app, drops/recreates tables, then seeds."""
    from app import create_app
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_db()


if __name__ == "__main__":
    seed()
