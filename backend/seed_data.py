"""Demo verisi yüklemek için script. Çalıştırmak için: python seed_data.py"""

from datetime import date
from models import db
from models.scorecard import ModelInventory, TechnicalGuide, ValidationReport, GiniHistory, ModelRollout, ModelVariable
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
        oot_period_start=date(2023, 7, 1),
        oot_period_end=date(2023, 9, 30),
        validation_submission_date=date(2023, 7, 15),
        development_table="TUKETICI_APP_202301",
        target_variable="default_flag_12m",
        gini_development=0.62,
        gini_train=0.62,
        gini_cv=0.59,
        gini_itt=0.60,
        gini_oot=0.58,
        gini_validation=0.58,
        gini_current=0.55,
        final_score=0.87,
        status="active",
        owner="Alp Giray Kaçıra",
        description="Tüketici kredisi başvuru skorkartı - 12 aylık temerrüt olasılığı modeli.",
        connected_processes="Bu modelin servisi FPD (First Payment Default) modelinde de girdi olarak kullanılmaktadır.",
        psi_flag=False,
        alert_work_started=False,
        calibration_status="ok",
    )
    m2 = ModelInventory(
        model_name="KMH Davranış Skorkartı v2.0",
        scorecard_category="Davranış",
        product_type="KMH",
        development_period_start=date(2022, 7, 1),
        development_period_end=date(2022, 12, 31),
        oot_period_start=date(2023, 1, 1),
        oot_period_end=date(2023, 3, 31),
        validation_submission_date=date(2023, 1, 10),
        development_table="KMH_BEH_DEV_202207",
        target_variable="loss_rate",
        gini_development=0.48,
        gini_train=0.48,
        gini_cv=0.45,
        gini_itt=0.46,
        gini_oot=0.44,
        gini_validation=0.44,
        gini_current=0.42,
        final_score=0.78,
        status="active",
        owner="Ahmet Yılmaz",
        description="KMH (Kredili Mevduat Hesabı) davranışsal skor modeli.",
        psi_flag=True,
        alert_work_started=True,
        calibration_status="warning",
    )
    m3 = ModelInventory(
        model_name="Kredi Kartı Davranış Skorkartı v1.5",
        scorecard_category="Davranış",
        product_type="Kredi Kartı",
        development_period_start=date(2024, 1, 10),
        development_period_end=date(2024, 5, 15),
        oot_period_start=date(2024, 6, 1),
        oot_period_end=date(2024, 8, 31),
        validation_submission_date=date(2024, 6, 15),
        development_table="CC_BEH_DEV_202401",
        target_variable="dpd_90plus_6m",
        gini_development=0.71,
        gini_train=0.71,
        gini_cv=0.68,
        gini_itt=0.69,
        gini_oot=0.67,
        gini_validation=0.67,
        gini_current=0.65,
        final_score=0.92,
        status="active",
        owner="Elif Demir",
        description="Kredi kartı müşterileri için davranışsal skor modeli.",
        psi_flag=False,
        alert_work_started=False,
        calibration_status="ok",
    )
    m4 = ModelInventory(
        model_name="Konut Başvuru Skorkartı v1.0",
        scorecard_category="Başvuru",
        product_type="Konut",
        development_period_start=date(2021, 3, 1),
        development_period_end=date(2021, 9, 30),
        oot_period_start=date(2021, 10, 1),
        oot_period_end=date(2021, 12, 31),
        validation_submission_date=date(2021, 10, 20),
        development_table="KONUT_APP_DEV_2021",
        target_variable="default_flag_24m",
        gini_development=0.55,
        gini_train=0.55,
        gini_cv=0.52,
        gini_itt=0.53,
        gini_oot=0.51,
        gini_validation=0.51,
        gini_current=0.38,
        final_score=0.72,
        status="under_review",
        owner="Ahmet Yılmaz",
        description="Konut kredisi başvuru skoru - performans düşüşü nedeniyle inceleniyor.",
        dependency_warning="Bu ürün grubu düşük başvuru adedi nedeniyle Tüketici Başvuru Skorkartı altyapısını kullanan yardımcı bir modelden yararlanmaktadır. Söz konusu modelin kapatılması durumunda Konut skoru da sekteye uğrayabilir.",
        psi_flag=True,
        alert_work_started=False,
        calibration_status="critical",
    )
    m5 = ModelInventory(
        model_name="Oto Başvuru Skorkartı v1.2",
        scorecard_category="Başvuru",
        product_type="Oto",
        development_period_start=date(2020, 6, 1),
        development_period_end=date(2020, 12, 31),
        oot_period_start=date(2021, 1, 1),
        oot_period_end=date(2021, 3, 31),
        validation_submission_date=date(2021, 1, 5),
        development_table="OTO_APP_DEV_2020",
        target_variable="default_flag_12m",
        gini_development=0.41,
        gini_train=0.41,
        gini_cv=0.39,
        gini_itt=0.40,
        gini_oot=0.38,
        gini_validation=0.38,
        gini_current=0.35,
        final_score=0.68,
        status="retired",
        owner="Elif Demir",
        dependency_warning="Oto ürün grubunda düşük adet arzı nedeniyle başka bir model servisinden yararlanılmaktadır. Bu bağımlı model kapatılırsa oto skoru da etkilenir.",
        psi_flag=False,
        alert_work_started=False,
        calibration_status="ok",
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
    # Her model için: geliştirme dönemi (quarterly), OOT (quarterly), aylık izleme
    # Period formatları: "YYYY-QN" (quarterly), "YYYY-MM" (aylık izleme)
    # Uyarı mekanizması sadece "YYYY-MM" formatlı kayıtlar üzerinden çalışır.

    def _add_gini(model_id, records):
        """records: list of (period, gini_val, notes, sample, target_ratio=None)"""
        for rec in records:
            period, gini_val, notes, sample = rec[0], rec[1], rec[2], rec[3]
            target_ratio = rec[4] if len(rec) > 4 else None
            db.session.add(GiniHistory(
                model_id=model_id, period=period,
                gini_value=gini_val, notes=notes, sample_size=sample,
                target_ratio=target_ratio,
            ))

    # ── M1: Tüketici Başvuru v3.2 (gini_dev=0.62) ──
    # Geliştirme: 2023-01 → 2023-06 | İzleme başlangıcı: 2023-07 | Uyarı: EVET
    _add_gini(m1.id, [
        # Geliştirme dönemi quarterly
        ("2022-Q4", 0.630, "Geliştirme dönemi", 22000),
        ("2023-Q1", 0.622, "Geliştirme dönemi", 24000),
        # OOT validasyon
        ("2023-Q3", 0.580, "OOT Validasyon", 19000),
        # Aylık izleme 2023-07 → 2026-03 (trend: 0.600 → 0.552, yavaş düşüş)
        ("2023-07", 0.600, "Aylık izleme", 14800), ("2023-08", 0.597, "Aylık izleme", 15100),
        ("2023-09", 0.594, "Aylık izleme", 14900), ("2023-10", 0.591, "Aylık izleme", 15200),
        ("2023-11", 0.588, "Aylık izleme", 14700), ("2023-12", 0.585, "Aylık izleme", 13900),
        ("2024-01", 0.582, "Aylık izleme", 15300), ("2024-02", 0.579, "Aylık izleme", 14600),
        ("2024-03", 0.576, "Aylık izleme", 15000), ("2024-04", 0.573, "Aylık izleme", 15100),
        ("2024-05", 0.570, "Aylık izleme", 14800), ("2024-06", 0.567, "Aylık izleme", 14900),
        ("2024-07", 0.565, "Aylık izleme", 15200), ("2024-08", 0.563, "Aylık izleme", 14700),
        ("2024-09", 0.561, "Aylık izleme", 15000), ("2024-10", 0.560, "Aylık izleme", 15100),
        ("2024-11", 0.559, "Aylık izleme", 14900), ("2024-12", 0.558, "Aylık izleme", 14200),
        ("2025-01", 0.558, "Aylık izleme", 15400), ("2025-02", 0.556, "Aylık izleme", 14800),
        ("2025-03", 0.557, "Aylık izleme", 15100), ("2025-04", 0.556, "Aylık izleme", 15200),
        ("2025-05", 0.557, "Aylık izleme", 14900), ("2025-06", 0.558, "Aylık izleme", 15000),
        ("2025-07", 0.557, "Aylık izleme", 15300), ("2025-08", 0.556, "Aylık izleme", 14800),
        ("2025-09", 0.557, "Aylık izleme", 15100), ("2025-10", 0.556, "Aylık izleme", 15200),
        ("2025-11", 0.557, "Aylık izleme", 14900), ("2025-12", 0.555, "Aylık izleme", 14300),
        ("2026-01", 0.551, "Aylık izleme", 15100), ("2026-02", 0.558, "Aylık izleme", 14800),
        ("2026-03", 0.552, "Aylık izleme", 15000),
        # Son 3 ay farkları: 0.069, 0.062, 0.068 → UYARI ✓
    ])

    # ── M2: KMH Davranış v2.0 (gini_dev=0.48) ──
    # Geliştirme: 2022-07 → 2022-12 | İzleme başlangıcı: 2023-01 | Uyarı: EVET
    _add_gini(m2.id, [
        # Geliştirme dönemi quarterly
        ("2022-Q3", 0.481, "Geliştirme dönemi", 18000),
        # OOT validasyon
        ("2023-Q1", 0.440, "OOT Validasyon", 16000),
        # Aylık izleme 2023-01 → 2026-03 (trend: 0.462 → 0.420, kademeli düşüş)
        ("2023-01", 0.462, "Aylık izleme", 11200), ("2023-02", 0.460, "Aylık izleme", 10800),
        ("2023-03", 0.458, "Aylık izleme", 11400), ("2023-04", 0.455, "Aylık izleme", 11100),
        ("2023-05", 0.453, "Aylık izleme", 10900), ("2023-06", 0.451, "Aylık izleme", 11000),
        ("2023-07", 0.449, "Aylık izleme", 11300), ("2023-08", 0.448, "Aylık izleme", 10800),
        ("2023-09", 0.446, "Aylık izleme", 11100), ("2023-10", 0.445, "Aylık izleme", 11200),
        ("2023-11", 0.444, "Aylık izleme", 10900), ("2023-12", 0.443, "Aylık izleme", 10400),
        ("2024-01", 0.443, "Aylık izleme", 11300), ("2024-02", 0.442, "Aylık izleme", 10700),
        ("2024-03", 0.441, "Aylık izleme", 11000), ("2024-04", 0.442, "Aylık izleme", 11100),
        ("2024-05", 0.441, "Aylık izleme", 10800), ("2024-06", 0.440, "Aylık izleme", 10900),
        ("2024-07", 0.431, "Aylık izleme", 11200), ("2024-08", 0.429, "Aylık izleme", 10700),
        ("2024-09", 0.427, "Aylık izleme", 11000), ("2024-10", 0.426, "Aylık izleme", 11100),
        ("2024-11", 0.424, "Aylık izleme", 10900), ("2024-12", 0.423, "Aylık izleme", 10300),
        ("2025-01", 0.423, "Aylık izleme", 11200), ("2025-02", 0.422, "Aylık izleme", 10700),
        ("2025-03", 0.421, "Aylık izleme", 11000), ("2025-04", 0.422, "Aylık izleme", 11100),
        ("2025-05", 0.421, "Aylık izleme", 10800), ("2025-06", 0.422, "Aylık izleme", 10900),
        ("2025-07", 0.421, "Aylık izleme", 11200), ("2025-08", 0.420, "Aylık izleme", 10600),
        ("2025-09", 0.421, "Aylık izleme", 11000), ("2025-10", 0.422, "Aylık izleme", 11100),
        ("2025-11", 0.421, "Aylık izleme", 10800), ("2025-12", 0.420, "Aylık izleme", 10200),
        ("2026-01", 0.420, "Aylık izleme", 11100), ("2026-02", 0.421, "Aylık izleme", 10700),
        ("2026-03", 0.420, "Aylık izleme", 11000),
        # Son 3 ay farkları: 0.060, 0.059, 0.060 → UYARI ✓
    ])

    # ── M3: Kredi Kartı Davranış v1.5 (gini_dev=0.71) ──
    # Geliştirme: 2024-01 → 2024-05 | İzleme başlangıcı: 2024-07 | Uyarı: HAYIR
    _add_gini(m3.id, [
        # Geliştirme dönemi quarterly
        ("2024-Q1", 0.712, "Geliştirme dönemi", 28000),
        ("2024-Q2", 0.695, "Geliştirme dönemi", 26000),
        # OOT validasyon
        ("2024-Q3", 0.671, "OOT Validasyon", 22000),
        # Aylık izleme 2024-07 → 2026-03 (model stabil, son 3 ayda fark <0.05)
        ("2024-07", 0.680, "Aylık izleme", 18500), ("2024-08", 0.678, "Aylık izleme", 19200),
        ("2024-09", 0.675, "Aylık izleme", 18800), ("2024-10", 0.673, "Aylık izleme", 19100),
        ("2024-11", 0.671, "Aylık izleme", 18600), ("2024-12", 0.670, "Aylık izleme", 17900),
        ("2025-01", 0.672, "Aylık izleme", 19300), ("2025-02", 0.670, "Aylık izleme", 18700),
        ("2025-03", 0.669, "Aylık izleme", 19000), ("2025-04", 0.668, "Aylık izleme", 19200),
        ("2025-05", 0.670, "Aylık izleme", 18800), ("2025-06", 0.669, "Aylık izleme", 19100),
        ("2025-07", 0.668, "Aylık izleme", 19400), ("2025-08", 0.667, "Aylık izleme", 18900),
        ("2025-09", 0.668, "Aylık izleme", 19200), ("2025-10", 0.666, "Aylık izleme", 19300),
        ("2025-11", 0.667, "Aylık izleme", 18800), ("2025-12", 0.666, "Aylık izleme", 18200),
        ("2026-01", 0.666, "Aylık izleme", 19100), ("2026-02", 0.660, "Aylık izleme", 18700),
        ("2026-03", 0.651, "Aylık izleme", 19000),
        # Son 3 ay farkları: 0.044, 0.050, 0.059 → İlk ay <0.05, UYARI YOK ✓
    ])

    # ── M4: Konut Başvuru v1.0 (gini_dev=0.55, under_review) ──
    # Geliştirme: 2021-03 → 2021-09 | İzleme başlangıcı: 2022-01 | Uyarı: EVET (ciddi düşüş)
    _add_gini(m4.id, [
        # Geliştirme dönemi quarterly
        ("2021-Q2", 0.550, "Geliştirme dönemi", 17000),
        ("2021-Q3", 0.532, "Geliştirme dönemi", 16000),
        # OOT validasyon
        ("2022-Q1", 0.510, "OOT Validasyon", 14000),
        # Aylık izleme 2022-01 → 2026-03 (ciddi ve sürekli düşüş)
        ("2022-01", 0.503, "Aylık izleme", 8200), ("2022-02", 0.499, "Aylık izleme", 7900),
        ("2022-03", 0.496, "Aylık izleme", 8100), ("2022-04", 0.492, "Aylık izleme", 8300),
        ("2022-05", 0.489, "Aylık izleme", 7800), ("2022-06", 0.485, "Aylık izleme", 8000),
        ("2022-07", 0.481, "Aylık izleme", 8200), ("2022-08", 0.478, "Aylık izleme", 7900),
        ("2022-09", 0.474, "Aylık izleme", 8100), ("2022-10", 0.470, "Aylık izleme", 8300),
        ("2022-11", 0.467, "Aylık izleme", 7800), ("2022-12", 0.463, "Aylık izleme", 7600),
        ("2023-01", 0.459, "Aylık izleme", 8200), ("2023-02", 0.456, "Aylık izleme", 7900),
        ("2023-03", 0.452, "Aylık izleme", 8100), ("2023-04", 0.448, "Aylık izleme", 8200),
        ("2023-05", 0.445, "Aylık izleme", 7800), ("2023-06", 0.441, "Aylık izleme", 7900),
        ("2023-07", 0.437, "Aylık izleme", 8100), ("2023-08", 0.433, "Aylık izleme", 7900),
        ("2023-09", 0.430, "Aylık izleme", 8000), ("2023-10", 0.426, "Aylık izleme", 8200),
        ("2023-11", 0.422, "Aylık izleme", 7800), ("2023-12", 0.419, "Aylık izleme", 7500),
        ("2024-01", 0.415, "Aylık izleme", 8100), ("2024-02", 0.411, "Aylık izleme", 7800),
        ("2024-03", 0.408, "Aylık izleme", 8000), ("2024-04", 0.405, "Aylık izleme", 8200),
        ("2024-05", 0.402, "Aylık izleme", 7700), ("2024-06", 0.399, "Aylık izleme", 7900),
        ("2024-07", 0.396, "Aylık izleme", 8100), ("2024-08", 0.393, "Aylık izleme", 7800),
        ("2024-09", 0.390, "Aylık izleme", 8000), ("2024-10", 0.389, "Aylık izleme", 8200),
        ("2024-11", 0.387, "Aylık izleme", 7700), ("2024-12", 0.386, "Aylık izleme", 7400),
        ("2025-01", 0.386, "Aylık izleme", 8000), ("2025-02", 0.387, "Aylık izleme", 7700),
        ("2025-03", 0.385, "Aylık izleme", 7900), ("2025-04", 0.384, "Aylık izleme", 8100),
        ("2025-05", 0.385, "Aylık izleme", 7700), ("2025-06", 0.386, "Aylık izleme", 7800),
        ("2025-07", 0.384, "Aylık izleme", 8000), ("2025-08", 0.385, "Aylık izleme", 7700),
        ("2025-09", 0.384, "Aylık izleme", 7900), ("2025-10", 0.385, "Aylık izleme", 8100),
        ("2025-11", 0.384, "Aylık izleme", 7700), ("2025-12", 0.383, "Aylık izleme", 7300),
        ("2026-01", 0.382, "Aylık izleme", 7900), ("2026-02", 0.385, "Aylık izleme", 7700),
        ("2026-03", 0.381, "Aylık izleme", 8000),
        # Son 3 ay farkları: 0.168, 0.165, 0.169 → UYARI ✓ (kritik)
    ])

    # ── M5: Oto Başvuru v1.2 (gini_dev=0.41, retired 2024-06) ──
    # Geliştirme: 2020-06 → 2020-12 | İzleme: 2021-01 → 2024-06 (emekliye ayrıldı)
    _add_gini(m5.id, [
        # Geliştirme dönemi quarterly
        ("2020-Q3", 0.412, "Geliştirme dönemi", 12000),
        ("2020-Q4", 0.405, "Geliştirme dönemi", 11500),
        # OOT validasyon
        ("2021-Q2", 0.381, "OOT Validasyon", 9500),
        # Aylık izleme 2021-01 → 2024-06 (modelin emekliye ayrılmasına kadar)
        ("2021-01", 0.392, "Aylık izleme", 6800), ("2021-02", 0.390, "Aylık izleme", 6500),
        ("2021-03", 0.388, "Aylık izleme", 6700), ("2021-04", 0.386, "Aylık izleme", 6900),
        ("2021-05", 0.385, "Aylık izleme", 6400), ("2021-06", 0.383, "Aylık izleme", 6600),
        ("2021-07", 0.381, "Aylık izleme", 6800), ("2021-08", 0.380, "Aylık izleme", 6500),
        ("2021-09", 0.378, "Aylık izleme", 6700), ("2021-10", 0.376, "Aylık izleme", 6900),
        ("2021-11", 0.374, "Aylık izleme", 6400), ("2021-12", 0.372, "Aylık izleme", 6100),
        ("2022-01", 0.370, "Aylık izleme", 6700), ("2022-02", 0.368, "Aylık izleme", 6400),
        ("2022-03", 0.367, "Aylık izleme", 6600), ("2022-04", 0.365, "Aylık izleme", 6800),
        ("2022-05", 0.363, "Aylık izleme", 6300), ("2022-06", 0.362, "Aylık izleme", 6500),
        ("2022-07", 0.360, "Aylık izleme", 6700), ("2022-08", 0.359, "Aylık izleme", 6400),
        ("2022-09", 0.357, "Aylık izleme", 6600), ("2022-10", 0.356, "Aylık izleme", 6800),
        ("2022-11", 0.354, "Aylık izleme", 6300), ("2022-12", 0.353, "Aylık izleme", 5900),
        ("2023-01", 0.351, "Aylık izleme", 6600), ("2023-02", 0.350, "Aylık izleme", 6300),
        ("2023-03", 0.349, "Aylık izleme", 6500), ("2023-04", 0.348, "Aylık izleme", 6700),
        ("2023-05", 0.347, "Aylık izleme", 6200), ("2023-06", 0.346, "Aylık izleme", 6400),
        ("2023-07", 0.354, "Aylık izleme", 6600), ("2023-08", 0.353, "Aylık izleme", 6300),
        ("2023-09", 0.352, "Aylık izleme", 6500), ("2023-10", 0.351, "Aylık izleme", 6700),
        ("2023-11", 0.350, "Aylık izleme", 6200), ("2023-12", 0.350, "Aylık izleme", 5800),
        ("2024-01", 0.350, "Aylık izleme", 6500), ("2024-02", 0.350, "Aylık izleme", 6200),
        ("2024-03", 0.350, "Aylık izleme", 6400), ("2024-04", 0.349, "Aylık izleme", 6600),
        ("2024-05", 0.350, "Aylık izleme", 6100), ("2024-06", 0.350, "Aylık izleme", 6300),
        # Model 2024-07'de emekliye ayrıldı, izleme sona erdi
    ])

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

    # ── Model Rollout Kademeleri ──
    # M1: Tüketici - tam cademi
    for pct, dt in [(10, date(2023, 8, 1)), (25, date(2023, 8, 15)), (50, date(2023, 9, 1)), (100, date(2023, 10, 1))]:
        db.session.add(ModelRollout(model_id=m1.id, rollout_percentage=pct, rollout_date=dt))
    # M3: Kredi Kartı - tam kademe
    for pct, dt in [(10, date(2024, 9, 1)), (25, date(2024, 9, 20)), (50, date(2024, 10, 10)), (100, date(2024, 11, 1))]:
        db.session.add(ModelRollout(model_id=m3.id, rollout_percentage=pct, rollout_date=dt))

    # ── Model Değişkenleri ──
    # M1: Tüketici Başvuru
    m1_vars = [
        ModelVariable(model_id=m1.id, variable_name="utilization_ratio", variable_description="Bakiye / Limit oranı", iv_value=0.3812, importance_rank=1, median_train=0.42, coefficient=1.254, woe_bin_count=6),
        ModelVariable(model_id=m1.id, variable_name="dpd_count_6m", variable_description="Son 6 ay gecikme sayısı", iv_value=0.2940, importance_rank=2, median_train=0.0, coefficient=0.987, woe_bin_count=5),
        ModelVariable(model_id=m1.id, variable_name="credit_age_months", variable_description="Kredi geçmişi yaşı (ay)", iv_value=0.2105, importance_rank=3, median_train=48.0, coefficient=-0.612, woe_bin_count=7),
        ModelVariable(model_id=m1.id, variable_name="num_active_products", variable_description="Aktif ürün sayısı", iv_value=0.1654, importance_rank=4, median_train=2.0, coefficient=-0.334, woe_bin_count=5),
        ModelVariable(model_id=m1.id, variable_name="max_dpd_12m", variable_description="Son 12 ay maksimum gecikme gün sayısı", iv_value=0.1423, importance_rank=5, median_train=0.0, coefficient=0.821, woe_bin_count=6),
    ]
    db.session.add_all(m1_vars)

    # M3: Kredi Kartı Davranış
    m3_vars = [
        ModelVariable(model_id=m3.id, variable_name="cc_utilization_3m_avg", variable_description="Kredi kartı 3 aylık ortalama kullanım oranı", iv_value=0.4120, importance_rank=1, median_train=0.58, coefficient=1.543, woe_bin_count=7),
        ModelVariable(model_id=m3.id, variable_name="min_payment_ratio", variable_description="Asgari ödeme / Toplam borç oranı", iv_value=0.3540, importance_rank=2, median_train=0.85, coefficient=-1.231, woe_bin_count=6),
        ModelVariable(model_id=m3.id, variable_name="cash_advance_ratio", variable_description="Nakit avans kullanım oranı", iv_value=0.2180, importance_rank=3, median_train=0.0, coefficient=0.765, woe_bin_count=5),
        ModelVariable(model_id=m3.id, variable_name="payment_streak", variable_description="Ardışık tam ödeme sayısı", iv_value=0.1930, importance_rank=4, median_train=3.0, coefficient=-0.543, woe_bin_count=6),
    ]
    db.session.add_all(m3_vars)

    db.session.commit()
    print("Seed data loaded successfully!")
    print(f"  - {ModelInventory.query.count()} models")
    print(f"  - {TechnicalGuide.query.count()} technical guide sections")
    print(f"  - {ValidationReport.query.count()} validation reports")
    print(f"  - {GiniHistory.query.count()} gini history records")
    print(f"  - {ModelRollout.query.count()} rollout stages")
    print(f"  - {ModelVariable.query.count()} model variables")
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
