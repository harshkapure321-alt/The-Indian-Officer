import uuid

from app.models.case import Case
from app.models.enums import CaseSourceType, CaseStatus, CaseType
from app.models.topic import Topic
from app.utils.seed_geography import GEOGRAPHY_CATEGORIES, seed_geography
from tests.conftest import login_headers

SECRET = "TOP-SECRET-ANSWER"


def _make_case(db, subject, topic, code, status, owner_user_id=None):
    case = Case(
        case_code=code,
        title=f"Case {code}",
        case_type=CaseType.discovery,
        subject_id=subject.id,
        topic_id=topic.id,
        description="desc",
        status=status,
        source_type=CaseSourceType.simulated,
        answer_key={"stage_1": SECRET},
        evaluation_rubric={"secret_rubric": SECRET},
        case_content={"stages": [SECRET]},
        owner_user_id=owner_user_id,
    )
    db.add(case)
    db.commit()
    return case


def test_subject_endpoints_require_auth(client, db):
    subject = seed_geography(db)
    assert client.get("/api/v1/subjects").status_code == 401
    assert client.get(f"/api/v1/subjects/{subject.id}").status_code == 401
    assert client.get(f"/api/v1/subjects/{subject.id}/topics").status_code == 401


def test_list_and_get_subject(client, db):
    subject = seed_geography(db)
    headers = login_headers(client)

    listing = client.get("/api/v1/subjects", headers=headers).json()["data"]
    assert [s["name"] for s in listing] == ["Geography"]

    one = client.get(f"/api/v1/subjects/{subject.id}", headers=headers)
    assert one.status_code == 200
    assert one.json()["data"]["coverage_status"] == "not_started"  # infrastructure != validated


def test_unknown_subject_is_404(client):
    headers = login_headers(client)
    assert client.get(f"/api/v1/subjects/{uuid.uuid4()}", headers=headers).status_code == 404


def test_seed_is_idempotent_and_has_nine_ordered_categories(client, db):
    seed_geography(db)
    subject = seed_geography(db)  # second run must not duplicate
    headers = login_headers(client)
    topics = client.get(f"/api/v1/subjects/{subject.id}/topics", headers=headers).json()["data"]
    assert [t["name"] for t in topics] == GEOGRAPHY_CATEGORIES
    assert all(t["validation_status"] == "not_started" for t in topics)


def test_topic_tree_nests_subtopics(client, db):
    subject = seed_geography(db)
    parent = db.query(Topic).filter_by(subject_id=subject.id, name="Earth and Its Fundamentals").one()
    db.add(Topic(subject_id=subject.id, parent_topic_id=parent.id, name="Latitude, Longitude and Time", sequence_number=1))
    db.commit()
    headers = login_headers(client)

    tree = client.get(f"/api/v1/subjects/{subject.id}/topics", headers=headers).json()["data"]
    node = next(t for t in tree if t["name"] == "Earth and Its Fundamentals")
    assert [c["name"] for c in node["children"]] == ["Latitude, Longitude and Time"]

    detail = client.get(f"/api/v1/topics/{parent.id}", headers=headers).json()["data"]
    assert [s["name"] for s in detail["subtopics"]] == ["Latitude, Longitude and Time"]


def test_topic_cases_only_published_and_never_expose_answers(client, db):
    subject = seed_geography(db)
    topic = db.query(Topic).filter_by(subject_id=subject.id, name="Earth and Its Fundamentals").one()
    _make_case(db, subject, topic, "D-PUB", CaseStatus.published)
    _make_case(db, subject, topic, "D-DRAFT", CaseStatus.draft)
    _make_case(db, subject, topic, "D-ARCH", CaseStatus.archived)
    _make_case(db, subject, topic, "D-PRIVATE", CaseStatus.published, owner_user_id=uuid.uuid4())
    headers = login_headers(client)

    resp = client.get(f"/api/v1/topics/{topic.id}/cases", headers=headers)
    assert resp.status_code == 200
    assert [c["case_code"] for c in resp.json()["data"]] == ["D-PUB"]
    assert SECRET not in resp.text
    for forbidden in ("answer_key", "evaluation_rubric", "case_content"):
        assert forbidden not in resp.text


def test_topic_cases_requires_auth(client, db):
    subject = seed_geography(db)
    topic = db.query(Topic).filter_by(subject_id=subject.id).first()
    assert client.get(f"/api/v1/topics/{topic.id}/cases").status_code == 401
