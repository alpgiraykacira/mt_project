"""Demo verisi yüklemek için script. Çalıştırmak için: python seed_data.py"""

from datetime import date
from models import db
from models.scorecard import ModelInventory, TechnicalGuide, ValidationReport, GiniHistory
from models.development import DevelopmentProject, DevelopmentStage, StageTask


def seed_db():
    """Seed logic only — must be called inside an active app context."""

    # ── Mevcut Modeller ──
    m1 = ModelInventory(
        model_name="Tüketici Başvuru Skorkartı v3.2",
        scorecard_category="Başvuru",
        product_type="Tüketici",
        development_period_start=date(2023, 1, 15),
        development_period_end=date(2023, 6, 30),
        development_table="TUKETICI_APP_202301",
        target_variable="default_flag_12m",
        gini_development=0.62,
        gini_validation=0.58,
        gini_current=0.55,
        final_score=0.87,
        status="active",
        owner="Alp Giray Kaçıra",
        description="Tüketici kredisi başvuru skorkartı - 12 aylık temerrüt olasılığı modeli.",
    )
    m2 = ModelInventory(
        model_name="KMH Davranış Skorkartı v2.0",
        scorecard_category="Davranış",
        product_type="KMH",
        development_period_start=date(2022, 7, 1),
        development_period_end=date(2022, 12, 31),
        development_table="KMH_BEH_DEV_202207",
        target_variable="loss_rate",
        gini_development=0.48,
        gini_validation=0.44,
        gini_current=0.42,
        final_score=0.78,
        status="active",
        owner="Ahmet Yılmaz",
        description="KMH (Kredili Mevduat Hesabı) davranışsal skor modeli.",
    )
    m3 = ModelInventory(
        model_name="Kredi Kartı Davranış Skorkartı v1.5",
        scorecard_category="Davranış",
        product_type="Kredi Kartı",
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
        model_name="Konut Başvuru Skorkartı v1.0",
        scorecard_category="Başvuru",
        product_type="Konut",
        development_period_start=date(2021, 3, 1),
        development_period_end=date(2021, 9, 30),
        development_table="KONUT_APP_DEV_2021",
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
        model_name="Oto Başvuru Skorkartı v1.2",
        scorecard_category="Başvuru",
        product_type="Oto",
        development_period_start=date(2020, 6, 1),
        development_period_end=date(2020, 12, 31),
        development_table="OTO_APP_DEV_2020",
        target_variable="default_flag_12m",
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
                query_code=f"SELECT * FROM {model.development_table}\nWHERE observation_date BETWEEN '2023-01-01' AND '2023-06-30'\n  AND product_type = '{model.product_type}';",
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
        project_name="Tüketici Başvuru Skorkartı v4.0 Geliştirme",
        scorecard_category="Başvuru",
        product_type="Tüketici",
        owner="Alp Giray Kaçıra",
        status="in_progress",
        priority="high",
        start_date=date(2025, 9, 1),
        target_end_date=date(2026, 3, 31),
        description="Mevcut tüketici başvuru skorkartının yenilenmesi. Yeni değişkenler ve ML teknikleri eklenecek.",
    )
    p2 = DevelopmentProject(
        project_name="KMH Davranış Skorkartı v3.0",
        scorecard_category="Davranış",
        product_type="KMH",
        owner="Ahmet Yılmaz",
        status="in_progress",
        priority="medium",
        start_date=date(2025, 11, 1),
        target_end_date=date(2026, 5, 31),
        description="KMH segmenti için yeni davranışsal skor modeli geliştirmesi.",
    )
    p3 = DevelopmentProject(
        project_name="Konut Başvuru Skorkartı Yenileme",
        scorecard_category="Başvuru",
        product_type="Konut",
        owner="Elif Demir",
        status="in_progress",
        priority="critical",
        start_date=date(2025, 7, 1),
        target_end_date=date(2026, 1, 31),
        description="Performans düşüşü olan konut kredisi başvuru skorkartının yenilenmesi.",
    )
    db.session.add_all([p1, p2, p3])
    db.session.flush()

    # ── Aşamalar (hiyerarşik) ──
    def add_stage(project_id, code, name, desc="", order=0, parent=None, status="pending"):
        s = DevelopmentStage(
            project_id=project_id, parent_id=parent,
            stage_code=code, stage_name=name, description=desc,
            status=status, order_index=order,
        )
        db.session.add(s)
        db.session.flush()
        return s.id

    # p1: Aşama 3'te - ilk 2 tamamlandı
    add_stage(p1.id, "1", "Geliştirme Dönemi & Performans Period & Hedef Değişken & Sampling Yapma & İstisna Kararı", order=0, status="completed")
    add_stage(p1.id, "2", "Data kaynaklarının belirlenmesi", order=1, status="completed")
    s1_3 = add_stage(p1.id, "3", "Segmentasyon Kararı & Model Geliştirme", order=2, status="in_progress")
    s1_3_1 = add_stage(p1.id, "3.1", "Mevcut Değişkenler", order=0, parent=s1_3, status="in_progress")
    add_stage(p1.id, "3.1.0", "Referans Set & Default", order=0, parent=s1_3_1, status="completed")
    kkb_id = add_stage(p1.id, "3.1.1", "KKB", order=1, parent=s1_3_1, status="in_progress")
    add_stage(p1.id, "3.1.2", "Banka içi Datamartlar", order=2, parent=s1_3_1, status="pending")
    add_stage(p1.id, "3.1.3", "G6, BBE, IMS", order=3, parent=s1_3_1, status="pending")
    s1_3_2 = add_stage(p1.id, "3.2", "Yeni Değişken Keşif", order=1, parent=s1_3, status="pending")
    add_stage(p1.id, "3.2.1", "Hesap Hareketleri", order=0, parent=s1_3_2)
    add_stage(p1.id, "3.2.2", "Kredi Kartı hareketleri", order=1, parent=s1_3_2)
    add_stage(p1.id, "3.2.3", "Telekom verileri", order=2, parent=s1_3_2)
    add_stage(p1.id, "4", "Ağırlıklandırma", order=3)
    add_stage(p1.id, "5", "Backscoring (Geçmiş & Güncel)", order=4)
    add_stage(p1.id, "6", "Kalibrasyon", order=5)
    add_stage(p1.id, "7", "Dokümantasyon", order=6)
    add_stage(p1.id, "8", "Sunum", order=7)

    # Tasks for p1 KKB stage
    db.session.add_all([
        StageTask(stage_id=kkb_id, task_description="KKB ham veri çekimi", is_completed=True, order_index=0),
        StageTask(stage_id=kkb_id, task_description="KKB değişken türetimi", is_completed=False, order_index=1),
        StageTask(stage_id=kkb_id, task_description="KKB WOE/IV analizi", is_completed=False, order_index=2),
    ])

    # p2: Aşama 2'de - ilk 1 tamamlandı
    add_stage(p2.id, "1", "Geliştirme Dönemi & Performans Period & Hedef Değişken & Sampling Yapma & İstisna Kararı", order=0, status="completed")
    add_stage(p2.id, "2", "Data kaynaklarının belirlenmesi", order=1, status="in_progress")
    s2_3 = add_stage(p2.id, "3", "Segmentasyon Kararı & Model Geliştirme", order=2)
    s2_3_1 = add_stage(p2.id, "3.1", "Mevcut Değişkenler", order=0, parent=s2_3)
    add_stage(p2.id, "3.1.0", "Referans Set & Default", order=0, parent=s2_3_1)
    add_stage(p2.id, "3.1.1", "KKB", order=1, parent=s2_3_1)
    add_stage(p2.id, "3.1.2", "Banka içi Datamartlar", order=2, parent=s2_3_1)
    add_stage(p2.id, "3.1.3", "G6, BBE, IMS", order=3, parent=s2_3_1)
    s2_3_2 = add_stage(p2.id, "3.2", "Yeni Değişken Keşif", order=1, parent=s2_3)
    add_stage(p2.id, "3.2.1", "Hesap Hareketleri", order=0, parent=s2_3_2)
    add_stage(p2.id, "3.2.2", "Kredi Kartı hareketleri", order=1, parent=s2_3_2)
    add_stage(p2.id, "3.2.3", "Telekom verileri", order=2, parent=s2_3_2)
    add_stage(p2.id, "4", "Ağırlıklandırma", order=3)
    add_stage(p2.id, "5", "Backscoring (Geçmiş & Güncel)", order=4)
    add_stage(p2.id, "6", "Kalibrasyon", order=5)
    add_stage(p2.id, "7", "Dokümantasyon", order=6)
    add_stage(p2.id, "8", "Sunum", order=7)

    # p3: Aşama 6'da - ilk 5 aşama tamamlandı
    add_stage(p3.id, "1", "Geliştirme Dönemi & Performans Period & Hedef Değişken & Sampling Yapma & İstisna Kararı", order=0, status="completed")
    add_stage(p3.id, "2", "Data kaynaklarının belirlenmesi", order=1, status="completed")
    s3_3 = add_stage(p3.id, "3", "Segmentasyon Kararı & Model Geliştirme", order=2, status="completed")
    s3_3_1 = add_stage(p3.id, "3.1", "Mevcut Değişkenler", order=0, parent=s3_3, status="completed")
    add_stage(p3.id, "3.1.0", "Referans Set & Default", order=0, parent=s3_3_1, status="completed")
    add_stage(p3.id, "3.1.1", "KKB", order=1, parent=s3_3_1, status="completed")
    add_stage(p3.id, "3.1.2", "Banka içi Datamartlar", order=2, parent=s3_3_1, status="completed")
    add_stage(p3.id, "3.1.3", "G6, BBE, IMS", order=3, parent=s3_3_1, status="completed")
    s3_3_2 = add_stage(p3.id, "3.2", "Yeni Değişken Keşif", order=1, parent=s3_3, status="completed")
    add_stage(p3.id, "3.2.1", "Hesap Hareketleri", order=0, parent=s3_3_2, status="completed")
    add_stage(p3.id, "3.2.2", "Kredi Kartı hareketleri", order=1, parent=s3_3_2, status="completed")
    add_stage(p3.id, "3.2.3", "Telekom verileri", order=2, parent=s3_3_2, status="completed")
    add_stage(p3.id, "4", "Ağırlıklandırma", order=3, status="completed")
    add_stage(p3.id, "5", "Backscoring (Geçmiş & Güncel)", order=4, status="completed")
    add_stage(p3.id, "6", "Kalibrasyon", order=5, status="in_progress")
    add_stage(p3.id, "7", "Dokümantasyon", order=6)
    add_stage(p3.id, "8", "Sunum", order=7)

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
