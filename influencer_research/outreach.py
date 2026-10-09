"""LLM-personalized outreach emails and SMTP delivery (sandboxed to a test recipient)."""

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from influencer_research.config import settings

EMAIL_PROMPT = ChatPromptTemplate.from_template("""
You are a professional marketing specialist writing a personalized outreach email to an influencer.

INFLUENCER DETAILS:
- Name: {name}
- Platform(s): {platforms}
- Niche/Focus: {niche}
- Followers: {followers}
- Bio/Description: {bio}
- Recent content focus: {recent_content}

CAMPAIGN CONTEXT:
- Brand: {brand_name}
- Campaign Type: {campaign_type}
- Target Audience: {target_audience}
- Campaign Goals: {campaign_goals}

REQUIREMENTS:
1. Write a personalized, professional email that shows you've researched this specific influencer
2. Reference specific aspects of their content or niche that align with the campaign
3. Keep it concise but engaging (200-300 words)
4. Include a clear value proposition
5. End with a specific call-to-action
6. Use a professional but friendly tone
7. Make it feel authentic, not templated

EMAIL STRUCTURE:
- Engaging subject line
- Personal greeting using their name
- Brief introduction of yourself/brand
- Specific mention of why you chose them (reference their content/niche)
- Clear campaign proposal with benefits
- Call-to-action
- Professional closing

Generate a complete email including subject line.
""")


class EmailGenerator:
    """Writes a personalized outreach email from an influencer profile and campaign brief."""

    def __init__(self):
        self.init_error = None
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.EMAIL_MODEL_NAME,
                temperature=0.7,
                api_key=settings.GOOGLE_API_KEY,
            )
        except Exception as e:
            self.llm = None
            self.init_error = str(e)

    def generate_personalized_email(self, influencer_data: Dict, campaign_data: Dict) -> Dict:
        if not self.llm:
            return {
                'success': False,
                'error': f'Email generator not initialized ({self.init_error}). Check GOOGLE_API_KEY.',
            }

        brand_name = campaign_data.get('brand_name', 'Our Brand')
        try:
            response = self.llm.invoke(
                EMAIL_PROMPT.format(
                    name=influencer_data.get('Name', 'there'),
                    platforms=influencer_data.get('Platform(s)', 'social media'),
                    niche=influencer_data.get('Niche', 'your field'),
                    followers=influencer_data.get('Followers', 'your audience'),
                    bio=influencer_data.get('Bio/Description', 'your content'),
                    recent_content=influencer_data.get('Recent Content', 'your recent posts'),
                    brand_name=brand_name,
                    campaign_type=campaign_data.get('campaign_type', 'Brand Partnership'),
                    target_audience=campaign_data.get('target_audience', 'engaged social media users'),
                    campaign_goals=campaign_data.get('campaign_goals', 'increase brand awareness and engagement'),
                )
            )
        except Exception as e:
            return {'success': False, 'error': f'Failed to generate email: {e}'}

        email_content = response.content.strip()

        # Split off the "Subject:" line if the model produced one
        lines = email_content.split('\n')
        subject = f"Partnership Opportunity with {brand_name}"
        body = email_content
        for i, line in enumerate(lines):
            if line.lower().startswith('subject:'):
                subject = line.split(':', 1)[1].strip()
                body = '\n'.join(lines[i + 1:]).strip()
                break

        return {'success': True, 'subject': subject, 'body': body, 'full_email': email_content}


class EmailSender:
    """Sends generated emails over SMTP — always to OUTREACH_TEST_RECIPIENT, never to the influencer."""

    def __init__(self):
        self.test_email = settings.OUTREACH_TEST_RECIPIENT
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.email_user = settings.EMAIL_USER
        self.email_password = settings.EMAIL_PASSWORD
        self.configured = all([self.email_user, self.email_password, self.test_email])

    def send_email(self, subject: str, body: str, influencer_name: str = "Influencer") -> Dict:
        if not self.configured:
            return {
                'success': False,
                'error': 'Email not configured. Set EMAIL_USER and EMAIL_PASSWORD (and optionally OUTREACH_TEST_RECIPIENT).',
            }

        test_body = f"""
🧪 TEST EMAIL - Influencer Outreach System
==========================================
Target Influencer: {influencer_name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

[This is a test email. In production, this would be sent to the actual influencer.]

GENERATED EMAIL CONTENT:
{'-' * 50}
{body}
{'-' * 50}
"""
        msg = MIMEMultipart()
        msg['From'] = self.email_user
        msg['To'] = self.test_email
        msg['Subject'] = f"[TEST] {subject}"
        msg.attach(MIMEText(test_body, 'plain'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
        except Exception as e:
            return {'success': False, 'error': f'Failed to send email: {e}'}

        return {'success': True, 'message': f'Test email sent successfully to {self.test_email}'}
