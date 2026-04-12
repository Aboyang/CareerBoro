import boto3
import uuid

class JobDB:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")
        self.table = self.dynamodb.Table("jobs")

    def save_job_to_db(
        self,
        role: str,
        company: str,
        job_desc: str,
        apply_link: str,
        research: str = "",
        webpages_read: list = [] 
    ):
        job_id = str(uuid.uuid4())

        item = {
            "job_id": job_id,
            "role": role,
            "company": company,
            "job_desc": job_desc,
            "apply_link": apply_link,
            "research": research,
            "webpages_read": webpages_read
        }

        response = self.table.put_item(Item=item)

        return response, job_id
