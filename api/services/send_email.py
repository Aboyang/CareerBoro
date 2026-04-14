import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self, from_address: str = "onboarding@resend.dev"):
        self.base_url = "https://api.resend.com/emails"
        self.from_address = from_address
        self.api_key = os.getenv("RESEND_API_KEY")
        if not self.api_key:
            raise ValueError("RESEND_API_KEY environment variable is not set")
        
    def clean_html(self, content: str) -> str:
        # Remove ```html and ```
        content = content.replace("```html", "").replace("```", "")

        # Trim whitespace
        content = content.strip()

        return content

    def send_mail(self, to: str, subject: str, content: str, attachments: list[dict] = None):
        content = self.clean_html(content)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "from": self.from_address,
            "to": to,
            "subject": subject,
            "html": content
        }

        if attachments:
            payload["attachments"] = attachments

        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as err:
            print(f"HTTP error sending email: {err} — {response.text}")
            raise
        except requests.exceptions.RequestException as err:
            print(f"Failed to send email: {err}")
            raise


# mailer = EmailService()

# result = mailer.send_mail(
#     to="tkaiyang2005@gmail.com",
#     subject="Hello!",
#     content="<h1>This is a test email</h1>",
#     text="This is a test email",
# )

# print(result)