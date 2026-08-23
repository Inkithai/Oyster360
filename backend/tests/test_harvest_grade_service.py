"""Tests for HarvestGradeService (app.services.harvest_grade_service)."""
from app.models.harvest_grade import HarvestGrade
from app.services.harvest_grade_service import HarvestGradeService


def test_record_grade_persists(db_session):
    svc = HarvestGradeService(db_session)
    grade = svc.record_grade(
        harvest_id=1, batch_id=10, grade="A", quantity_kg=12.5,
        price_per_kg=8.0, notes="premium", user_id=3,
    )
    assert grade.id
    assert grade.grade == "A"
    assert grade.quantity_kg == 12.5
    assert grade.graded_by == 3


def test_get_grades_by_batch_filters(db_session):
    svc = HarvestGradeService(db_session)
    svc.record_grade(1, 10, "A", 5, 8.0, "", 1)
    svc.record_grade(1, 10, "B", 3, 6.0, "", 1)
    svc.record_grade(2, 20, "A", 1, 8.0, "", 1)
    grades_batch_10 = svc.get_grades_by_batch(10)
    assert len(grades_batch_10) == 2
    assert all(isinstance(g, HarvestGrade) for g in grades_batch_10)
