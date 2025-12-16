import boto3
import hashlib
import time
from datetime import datetime
import os

# ---------- CONFIG ----------
RESUME_FILE = "resume.md"
AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "beta")

ANALYTICS_TABLE = "ResumeAnalytics"
DEPLOYMENT_TABLE = "DeploymentTracking"
# ----------------------------

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
analytics_table = dynamodb.Table(ANALYTICS_TABLE)
deployment_table = dynamodb.Table(DEPLOYMENT_TABLE)

def read_resume():
    with open(RESUME_FILE, "r", encoding="utf-8") as f:
        return f.read()

def analyze_resume(text):
    word_count = len(text.split())

    required_sections = [
        "Summary",
        "Skills",
        "Experience",
        "Education",
        "Certifications"
    ]

    missing_sections = [
        s for s in required_sections if s.lower() not in text.lower()
    ]

    ats_score = max(60, 100 - (len(missing_sections) * 10))

    keywords = [
        "AWS", "Terraform", "Python", "CI/CD",
        "CloudFormation", "DevOps", "Docker"
    ]

    keywords_found = [k for k in keywords if k.lower() in text.lower()]

    return {
        "word_count": word_count,
        "ats_score": ats_score,
        "missing_sections": missing_sections,
        "keywords_found": keywords_found
    }

def write_analytics(data):
    analytics_table.put_item(
        Item={
            "resume_id": hashlib.md5(str(time.time()).encode()).hexdigest(),
            "timestamp": datetime.utcnow().isoformat(),
            "environment": ENVIRONMENT,
            **data
        }
    )

def write_deployment():
    deployment_table.put_item(
        Item={
            "deployment_id": hashlib.md5(str(time.time()).encode()).hexdigest(),
            "timestamp": datetime.utcnow().isoformat(),
            "environment": ENVIRONMENT,
            "status": "SUCCESS",
            "s3_path": f"s3://ai-resume-brr/{ENVIRONMENT}/index.html"
        }
    )

if __name__ == "__main__":
    print("Analyzing resume...")
    resume_text = read_resume()
    analysis = analyze_resume(resume_text)

    write_analytics(analysis)
    write_deployment()

    print("Resume analysis and deployment tracking saved.")
