"""Tests for OnboardingService progress tracking (app.services.onboarding_service)."""
from datetime import datetime

from app.core.security import get_password_hash
from app.models.organization import Organization, OrganizationMember
from app.models.user import User
from app.services.onboarding_service import OnboardingService


def _user(db, email):
    user = User(name="U", email=email, password_hash=get_password_hash("pw"), role="ADMIN")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_status_unknown_user(db_session):
    assert OnboardingService(db_session).get_onboarding_status(99999) == {"completed": False, "step": 0}


def test_status_without_organization(db_session):
    user = _user(db_session, "norg@test.com")
    status = OnboardingService(db_session).get_onboarding_status(user.id)
    assert status["completed"] is False
    assert status["step"] == 1


def test_status_with_org_but_solo(db_session):
    user = _user(db_session, "solo@test.com")
    org = Organization(name="Solo", slug="solo", owner_id=user.id, created_at=datetime.utcnow())
    db_session.add(org)
    db_session.commit()
    # owner is a member (count == 1, needs >= 2)
    db_session.add(OrganizationMember(organization_id=org.id, user_id=user.id, role="OWNER", joined_at=datetime.utcnow()))
    db_session.commit()
    status = OnboardingService(db_session).get_onboarding_status(user.id)
    assert status["completed"] is False
    assert status["step"] == 2


def test_status_complete_with_teammate(db_session):
    user = _user(db_session, "lead@test.com")
    org = Organization(name="Team", slug="team", owner_id=user.id, created_at=datetime.utcnow())
    db_session.add(org)
    db_session.commit()
    db_session.add_all([
        OrganizationMember(organization_id=org.id, user_id=user.id, role="OWNER", joined_at=datetime.utcnow()),
        OrganizationMember(organization_id=org.id, user_id=user.id + 1000, role="MEMBER", joined_at=datetime.utcnow()),
    ])
    db_session.commit()
    status = OnboardingService(db_session).get_onboarding_status(user.id)
    assert status["completed"] is True
    assert status["step"] == 3
