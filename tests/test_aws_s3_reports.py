import boto3
import pytest
from moto import mock_aws

BUCKET = "qa-banking-test-evidence"


@pytest.fixture()
def s3_client():
    with mock_aws():
        client = boto3.client("s3", region_name="eu-west-3")
        client.create_bucket(
            Bucket=BUCKET,
            CreateBucketConfiguration={"LocationConstraint": "eu-west-3"},
        )
        yield client


def test_bucket_created_with_expected_region(s3_client):
    resp = s3_client.get_bucket_location(Bucket=BUCKET)
    assert resp["LocationConstraint"] == "eu-west-3"


import json
from datetime import datetime, timezone


def test_upload_test_evidence_and_verify_integrity(s3_client):
    evidence = {
        "run_id": "BUILD-142",
        "suite": "transactions_api",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "results": {"passed": 12, "failed": 0, "skipped": 0},
    }
    key = f"evidence/{evidence['run_id']}/summary.json"

    s3_client.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=json.dumps(evidence).encode("utf-8"),
        ContentType="application/json",
    )

    obj = s3_client.get_object(Bucket=BUCKET, Key=key)
    retrieved = json.loads(obj["Body"].read())

    assert retrieved == evidence
    assert retrieved["results"]["failed"] == 0


def test_evidence_listing_for_audit_trail(s3_client):
    for run_id in ["BUILD-140", "BUILD-141", "BUILD-142"]:
        s3_client.put_object(
            Bucket=BUCKET,
            Key=f"evidence/{run_id}/summary.json",
            Body=b"{}",
        )

    listing = s3_client.list_objects_v2(Bucket=BUCKET, Prefix="evidence/")
    keys = [obj["Key"] for obj in listing["Contents"]]

    assert len(keys) == 3
    assert all(k.startswith("evidence/BUILD-") for k in keys)