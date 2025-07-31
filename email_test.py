"""Enhanced workflow for influencer research with email outreach capabilities - Test Version."""
import os
import sys
import json
import smtplib
import logging
from datetime import datetime
from typing import Dict, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functools import partial
from langgraph.graph import StateGraph, START, END, MessagesState

from variables.agents.research_agents import ResearchAgents, research_node, verify_node, report_node
from src.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailAgent:
    """Agent responsible for generating and sending professional emails to influencers."""
    
    def __init__(self, smtp_server: str = None, smtp_port: int = 587, 
                 email_user: str = None, email_password: str = None):
        """Initialize email agent with SMTP configuration."""
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.email_user = email_user or os.getenv('EMAIL_USER')
        self.email_password = email_password or os.getenv('EMAIL_PASSWORD')
        
        if not all([self.email_user, self.email_password]):
            logger.warning("Email credentials not provided. Email sending will be disabled.")
    
    def generate_professional_email(self, influencer_data: Dict, 
                                  campaign_details: Dict = None) -> str:
        """Generate a professional outreach email for an influencer."""
        
        name = influencer_data.get('name', 'there')
        platform = influencer_data.get('platform', 'social media')
        niche = influencer_data.get('niche', 'your field')
        followers = influencer_data.get('followers', 'your audience')
        
        # Default campaign details
        if not campaign_details:
            campaign_details = {
                'brand_name': 'Our Brand',
                'campaign_type': 'Brand Partnership',
                'compensation': 'competitive compensation',
                'timeline': 'flexible timeline'
            }
        
        email_templates = {
            'collaboration': f"""
Subject: Partnership Opportunity with {campaign_details.get('brand_name', 'Our Brand')}

Dear {name},

I hope this email finds you well. My name is [Your Name], and I represent {campaign_details.get('brand_name', 'Our Brand')}.

I've been following your {platform} content and am genuinely impressed by your authentic voice in the {niche} space. Your engagement with {followers} followers shows the genuine connection you've built with your audience.

We're currently launching a {campaign_details.get('campaign_type', 'brand partnership')} campaign that aligns perfectly with your content style and values. We believe your unique perspective would resonate strongly with our target audience.

What we're offering:
• {campaign_details.get('compensation', 'Competitive compensation')}
• {campaign_details.get('timeline', 'Flexible timeline')}
• Full creative freedom while meeting brand guidelines
• Long-term partnership potential

We'd love to discuss this opportunity further and answer any questions you might have. Would you be available for a brief call this week?

Looking forward to potentially working together.

Best regards,
[Your Name]
[Your Title]
{campaign_details.get('brand_name', 'Our Brand')}
[Contact Information]

P.S. We're particularly excited about your recent content on [specific post/topic] - it perfectly captures what we're looking for in a brand partner.
""",
            
            'product_review': f"""
Subject: Product Collaboration Invitation - {campaign_details.get('brand_name', 'Our Brand')}

Hello {name},

I've been following your {platform} content and love how you authentically share your experiences in the {niche} space with your {followers} followers.

We'd love to send you our latest product line for an honest review. There's no pressure - we simply believe our products align with your content style and would provide genuine value to your audience.

What's included:
• Complimentary product package (value $[X])
• {campaign_details.get('compensation', 'Additional compensation for content creation')}
• First access to new product launches
• Exclusive discount code for your audience

If you're interested, please let me know your mailing address, and we'll send everything over with no strings attached. We trust your judgment completely.

Would love to hear your thoughts!

Warm regards,
[Your Name]
{campaign_details.get('brand_name', 'Our Brand')}
""",
            
            'event_invitation': f"""
Subject: Exclusive Event Invitation - {campaign_details.get('brand_name', 'Our Brand')}

Hi {name},

Your work in the {niche} space has caught our attention, and we'd be honored to have you join us for an exclusive {campaign_details.get('campaign_type', 'brand event')}.

Event Details:
• Date: [Event Date]
• Location: [Event Location]
• Duration: [Event Duration]
• Plus-one welcome

What's included:
• All expenses covered
• {campaign_details.get('compensation', 'Event fee')}
• Networking with industry leaders
• Exclusive product previews
• Professional content creation support

We believe your unique perspective would add tremendous value to the event, and we'd love to collaborate on content that showcases your experience.

Please let me know if you're available and interested. Happy to provide more details!

Best,
[Your Name]
{campaign_details.get('brand_name', 'Our Brand')}
"""
        }
        
        # Default to collaboration template
        template_type = campaign_details.get('template_type', 'collaboration')
        return email_templates.get(template_type, email_templates['collaboration'])
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   attachments: List[str] = None) -> bool:
        """Send email to influencer."""
        
        if not all([self.email_user, self.email_password]):
            logger.error("Email credentials not configured. Cannot send email.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.isfile(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False


def email_generation_node(state: MessagesState, email_agent: EmailAgent) -> MessagesState:
    """Node for generating professional emails based on research results."""
    
    last_message = state["messages"][-1].content
    
    # Extract influencer data from the research results
    # This assumes the research results contain structured data about influencers
    try:
        # Parse influencer data from the last message
        # You might need to adjust this parsing based on your actual data format
        influencers = []
        if "FINAL ANSWER" in last_message:
            # Extract structured data - this is a simplified example
            # You'll need to implement proper parsing based on your data format
            lines = last_message.split('\n')
            current_influencer = {}
            
            for line in lines:
                if 'Name:' in line:
                    current_influencer['name'] = line.split('Name:')[-1].strip()
                elif 'Email:' in line:
                    current_influencer['email'] = line.split('Email:')[-1].strip()
                elif 'Platform:' in line:
                    current_influencer['platform'] = line.split('Platform:')[-1].strip()
                elif 'Niche:' in line:
                    current_influencer['niche'] = line.split('Niche:')[-1].strip()
                elif 'Followers:' in line:
                    current_influencer['followers'] = line.split('Followers:')[-1].strip()
                    # When we have all required fields, add to list
                    if all(k in current_influencer for k in ['name', 'email']):
                        influencers.append(current_influencer.copy())
                        current_influencer = {}
        
        # Generate emails for each influencer
        generated_emails = []
        for influencer in influencers:
            if influencer.get('email'):
                email_content = email_agent.generate_professional_email(influencer)
                generated_emails.append({
                    'influencer': influencer,
                    'email_content': email_content
                })
        
        response = f"""
EMAIL GENERATION COMPLETED

Generated {len(generated_emails)} professional outreach emails.

EMAIL TEMPLATES CREATED:
{'='*50}

"""
        
        for i, email_data in enumerate(generated_emails, 1):
            response += f"""
INFLUENCER {i}: {email_data['influencer'].get('name', 'Unknown')}
Email: {email_data['influencer'].get('email', 'No email')}
Platform: {email_data['influencer'].get('platform', 'Unknown')}

GENERATED EMAIL:
{'-'*30}
{email_data['email_content']}

{'='*50}
"""
        
        response += f"""

NEXT STEPS:
1. Review and customize each email template
2. Use the send_emails() method to send them out
3. Track responses and engagement

FINAL ANSWER: Email generation completed for {len(generated_emails)} influencers.
"""
        
    except Exception as e:
        response = f"Error generating emails: {str(e)}\nFINAL ANSWER: Email generation failed."
    
    return {"messages": [("assistant", response)]}


def email_sending_node(state: MessagesState, email_agent: EmailAgent) -> MessagesState:
    """Node for sending generated emails to influencers."""
    
    last_message = state["messages"][-1].content
    
    # This would typically extract the generated emails and send them
    # For now, we'll provide a summary of what would be sent
    
    response = """
EMAIL SENDING SIMULATION

⚠️ IMPORTANT: Before sending emails, ensure you have:
1. Configured SMTP settings in environment variables:
   - SMTP_SERVER (default: smtp.gmail.com)
   - SMTP_PORT (default: 587)
   - EMAIL_USER (your email address)
   - EMAIL_PASSWORD (your email password or app password)

2. Reviewed and customized each email template
3. Obtained proper consent for email outreach
4. Ensured compliance with anti-spam regulations

EMAIL SENDING STATUS:
- Total emails to send: [X]
- Successfully sent: [X]
- Failed to send: [X]
- Bounced emails: [X]

TRACKING RECOMMENDATIONS:
1. Monitor open rates and responses
2. Follow up with non-responders after 1 week
3. Track conversion rates and partnerships formed
4. Maintain a CRM system for ongoing relationships

FINAL ANSWER: Email outreach system is ready for deployment.
"""
    
    return {"messages": [("assistant", response)]}


class EnhancedInfluencerResearchWorkflow:
    """Enhanced workflow orchestrator with email outreach capabilities."""
    
    def __init__(self, campaign_details: Dict = None):
        self.agents = ResearchAgents()
        self.research_agent = self.agents.create_research_agent()
        self.verifier_agent = self.agents.create_verifier_agent()
        self.reporter_agent = self.agents.create_reporter_agent()
        self.email_agent = EmailAgent()
        self.campaign_details = campaign_details or {}
        self.graph = self._build_workflow()
    
    def _build_workflow(self):
        """Build the enhanced workflow graph with email capabilities."""
        workflow = StateGraph(MessagesState)
        
        # Add existing nodes
        workflow.add_node(
            "researcher", 
            partial(research_node, research_agent=self.research_agent)
        )
        workflow.add_node(
            "verifier_agent", 
            partial(verify_node, verifier_agent=self.verifier_agent)
        )
        workflow.add_node(
            "reporter", 
            partial(report_node, reporter_agent=self.reporter_agent)
        )
        
        # Add new email nodes
        workflow.add_node(
            "email_generator",
            partial(email_generation_node, email_agent=self.email_agent)
        )
        workflow.add_node(
            "email_sender",
            partial(email_sending_node, email_agent=self.email_agent)
        )
        
        # Add edges for complete workflow
        workflow.add_edge(START, "researcher")
        workflow.add_edge("researcher", "verifier_agent")
        workflow.add_edge("verifier_agent", "reporter")
        workflow.add_edge("reporter", "email_generator")
        workflow.add_edge("email_generator", "email_sender")
        workflow.add_edge("email_sender", END)
        
        return workflow.compile()
    
    def test_email_system(self, friend_email: str, friend_name: str = "Friend") -> bool:
        """Test the email system by sending a test email to your friend."""
        
        print("🧪 TESTING EMAIL SYSTEM")
        print("=" * 50)
        print(f"Sending test email to: {friend_email}")
        print()
        
        # Create test influencer data (your friend as mock influencer)
        test_influencer = {
            'name': friend_name,
            'platform': 'Instagram',
            'niche': 'lifestyle and travel',
            'followers': '10K'
        }
        
        # Test campaign details
        test_campaign = {
            'brand_name': 'Test Brand Co.',
            'campaign_type': 'Email System Test',
            'compensation': '$1,000 per post',
            'timeline': 'Flexible timeline',
            'template_type': 'collaboration'
        }
        
        try:
            # Generate test email
            print("📝 Generating test email...")
            email_content = self.email_agent.generate_professional_email(
                test_influencer, test_campaign
            )
            
            # Extract subject from email content
            lines = email_content.strip().split('\n')
            subject = "Test Email - Influencer Research System"
            for line in lines:
                if line.startswith('Subject:'):
                    subject = line.replace('Subject:', '').strip()
                    break
            
            # Add test message prefix
            test_message = f"""
🧪 THIS IS A TEST EMAIL FROM YOUR INFLUENCER RESEARCH SYSTEM 🧪

Hi {friend_name}!

This is a test email from your new influencer research and outreach system. 
The system is working correctly if you receive this email.

Below is a sample of what would be sent to real influencers:

{'-'*60}
{email_content}
{'-'*60}

Best regards,
Your Influencer Research System

P.S. - The email system is working perfectly! 🎉
"""
            
            # Send test email
            print("📧 Sending test email...")
            success = self.email_agent.send_email(
                to_email=friend_email,
                subject=f"🧪 {subject}",
                body=test_message
            )
            
            if success:
                print("✅ Test email sent successfully!")
                print(f"📬 Check {friend_email} for the test email")
                return True
            else:
                print("❌ Failed to send test email")
                return False
                
        except Exception as e:
            print(f"❌ Error testing email system: {str(e)}")
            logger.error(f"Email test failed: {str(e)}")
            return False
    
    def run_complete_workflow(self, query: str, send_emails: bool = False) -> str:
        """Run the complete research and outreach workflow."""
        print("🚀 Starting Enhanced Multi-Agent Influencer Research & Outreach Workflow...")
        print("   👤 Researcher: Analyzing query and gathering data...")
        print("   🔍 Verifier: Will validate findings...")
        print("   📄 Reporter: Will generate final report...")
        print("   ✉️  Email Generator: Will create outreach emails...")
        print("   📧 Email Sender: Will handle email distribution...")
        print()
        
        events = self.graph.stream(
            {
                "messages": [
                    ("user", f"""
Research Query: {query}

Please conduct a comprehensive influencer research based on this query, followed by email outreach generation.

Research Requirements:
1. Analyze the query to understand requirements
2. Develop a multi-phase search approach
3. Use all available tools to gather data
4. Provide detailed profiles with verified information INCLUDING EMAIL ADDRESSES
5. Include industry insights and recommendations
6. Aim for 15-20 high-quality influencer profiles

Email Outreach Requirements:
1. Generate professional outreach emails for each influencer
2. Customize based on their niche and platform
3. Include clear value propositions
4. Maintain professional tone throughout

Campaign Details: {json.dumps(self.campaign_details, indent=2)}
                """)
                ],
            },
            {"recursion_limit": settings.RECURSION_LIMIT},
        )
        
        final_result = None
        step_count = 0
        
        for event in events:
            step_count += 1
            
            if 'researcher' in event:
                content = event['researcher']['messages'][-1].content
                print(f"🔍 Research Step {step_count}: {len(content)} characters generated")
                if "FINAL ANSWER" in content:
                    print("✅ Research phase completed!")
                final_result = content
                
            elif 'verifier_agent' in event:
                print(f"🔍 Verification Step {step_count}: Checking data quality...")
                if "FINAL ANSWER" in event['verifier_agent']['messages'][-1].content:
                    print("✅ Verification completed - data approved!")
                    
            elif 'reporter' in event:
                print(f"📄 Report Generation Step {step_count}: Creating final document...")
                final_result = event['reporter']['messages'][-1].content
                
            elif 'email_generator' in event:
                print(f"✉️  Email Generation Step {step_count}: Creating outreach emails...")
                final_result = event['email_generator']['messages'][-1].content
                if "FINAL ANSWER" in final_result:
                    print("✅ Email generation completed!")
                    
            elif 'email_sender' in event:
                print(f"📧 Email Sending Step {step_count}: Preparing email distribution...")
                final_result = event['email_sender']['messages'][-1].content
                if "FINAL ANSWER" in final_result:
                    print("✅ Complete workflow finished!")
        
        # Save results to file
        self.save_results(final_result, query)
        
        return final_result or "No results generated"
    
    def save_results(self, results: str, query: str):
        """Save workflow results to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"influencer_research_report_{timestamp}.txt"
        
        try:
            os.makedirs("reports", exist_ok=True)
            filepath = os.path.join("reports", filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"INFLUENCER RESEARCH & OUTREACH REPORT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Query: {query}\n")
                f.write("="*80 + "\n\n")
                f.write(results)
            
            print(f"📁 Results saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")
            return None
    
    def send_bulk_emails(self, influencer_list: List[Dict], 
                        campaign_details: Dict = None) -> Dict:
        """Send bulk emails to a list of influencers."""
        
        if not campaign_details:
            campaign_details = self.campaign_details
        
        results = {
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        for influencer in influencer_list:
            if not influencer.get('email'):
                results['failed'] += 1
                results['errors'].append(f"No email for {influencer.get('name', 'Unknown')}")
                continue
            
            try:
                email_content = self.email_agent.generate_professional_email(
                    influencer, campaign_details
                )
                
                # Extract subject from email content
                lines = email_content.strip().split('\n')
                subject = f"Partnership Opportunity with {campaign_details.get('brand_name', 'Our Brand')}"
                for line in lines:
                    if line.startswith('Subject:'):
                        subject = line.replace('Subject:', '').strip()
                        break
                
                if self.email_agent.send_email(
                    influencer['email'], 
                    subject, 
                    email_content
                ):
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to send to {influencer['email']}")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error with {influencer.get('email', 'Unknown')}: {str(e)}")
        
        return results
    
    def visualize_workflow(self):
        """Generate workflow visualization if possible."""
        try:
            from IPython.display import Image, display
            display(Image(self.graph.get_graph().draw_mermaid_png()))
        except Exception as e:
            print(f"Could not generate workflow visualization: {e}")
            print("Install IPython and graphviz for visualization support")


# Usage example for testing with your friend
if __name__ == "__main__":
    # Configure email settings first
    print("📧 EMAIL SYSTEM TEST")
    print("=" * 50)
    print("Make sure to set these environment variables:")
    print("- SMTP_SERVER (default: smtp.gmail.com)")
    print("- SMTP_PORT (default: 587)")
    print("- EMAIL_USER (your email address)")
    print("- EMAIL_PASSWORD (your email app password)")
    print()
    
    # Test configuration
    friend_email = input("Enter your friend's email for testing: ")
    friend_name = input("Enter your friend's name (optional): ") or "Friend"
    
    if friend_email:
        # Define campaign details for testing
        campaign_config = {
            'brand_name': 'Test Brand Co.',
            'campaign_type': 'Email System Testing',
            'compensation': 'System validation',
            'timeline': 'Immediate test',
            'template_type': 'collaboration'
        }
        
        # Initialize workflow
        workflow = EnhancedInfluencerResearchWorkflow(campaign_config)
        
        # Test email system
        success = workflow.test_email_system(friend_email, friend_name)
        
        if success:
            print("\n✅ Email system is working correctly!")
            print("You can now use it with your full workflow.")
        else:
            print("\n❌ Email system test failed.")
            print("Check your SMTP configuration and try again.")
    else:
        print("No email provided. Skipping test.")