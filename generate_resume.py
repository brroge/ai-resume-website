import boto3
import markdown
import os

# ---------- CONFIG ----------
RESUME_FILE = "resume.md"
OUTPUT_FILE = "index.html"

S3_BUCKET = os.environ.get("S3_BUCKET", "ai-resume-brr")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "beta")  # beta or prod
# ----------------------------

def read_markdown():
    with open(RESUME_FILE, "r", encoding="utf-8") as f:
        return f.read()

def convert_to_html(markdown_text):
    body = markdown.markdown(markdown_text, extensions=["extra"])
    html = f"""
    <html>
      <head>
        <title>Barnell Rogers | Resume</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
          body {{
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: auto;
            padding: 40px;
            line-height: 1.6;
          }}
          h1, h2, h3 {{
            color: #222;
          }}
          hr {{
            margin: 30px 0;
          }}
        </style>
      </head>
      <body>
        {body}
      </body>
    </html>
    """
    return html

def upload_to_s3():
    s3 = boto3.client("s3", region_name=AWS_REGION)
    s3.upload_file(
        OUTPUT_FILE,
        S3_BUCKET,
        f"{ENVIRONMENT}/index.html",
        ExtraArgs={"ContentType": "text/html"}
    )

if __name__ == "__main__":
    print("Generating resume website...")
    markdown_text = read_markdown()
    html = convert_to_html(markdown_text)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    upload_to_s3()
    print(f"Resume deployed to s3://{S3_BUCKET}/{ENVIRONMENT}/index.html")
