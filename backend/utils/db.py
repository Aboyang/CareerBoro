import boto3
import uuid

dynamodb = boto3.resource(
    "dynamodb",
    region_name="ap-southeast-1"
)

table = dynamodb.Table("jobs")

def save_job_to_db():
    job_id = str(uuid.uuid4())

    item = {
        "job_id": job_id,         
        "role": "C++ Software Engineering Intern – Summer 2026",
        "company": "Hudson River Trading (HRT)",

        "job_desc": "HRT is hiring software engineering interns to work on independent programming projects that power its algorithmic trading systems. Interns use C or C++ to build and maintain high-performance infrastructure that is critical to trading operations—e.g., low-latency services, data pipelines, and internal APIs. You’ll get structured and hands-on training, then move quickly into real projects, learning about HRT’s research and trading infrastructure beyond just your immediate work. Requirements: full-time student (BS/MS/PhD) in CS or related, eligible for full-time roles in 2027; strong C/C++ programming; excellent problem-solving and communication; interest in writing efficient, elegant code. No prior finance/trading knowledge required.",

        "apply_link": "https://www.linkedin.com/jobs/view/4372020904/",

        "research": "Recent HRT initiatives include gRPC streaming for trading APIs, NIC-to-NVMe high-speed data pipelines, and signal compression systems for market data efficiency.",

        "webpages_read": [
            "https://www.hudsonrivertrading.com/hrtbeat/intern-spotlight-software-engineering-summer-projects/"
        ]
    }

    response = table.put_item(Item=item)
    print("Inserted job with id:", job_id)
    return response