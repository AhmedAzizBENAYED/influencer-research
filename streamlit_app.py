"""
Enhanced Streamlit Web Interface for AI Influencer Research Assistant
with LLM-generated personalized email outreach
"""

import streamlit as st
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from src.config.settings import settings
    from variables.workflow.research_workflow import InfluencerResearchWorkflow
    from src.utils.query_analyser import QueryAnalyzer
    # Import LLM for email generation
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.prompts import ChatPromptTemplate
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all project dependencies are installed and paths are correct.")
    st.stop()


class EmailGenerator:
    """LLM-powered email generator for personalized influencer outreach."""
    
    def __init__(self):
        """Initialize the email generator with LLM."""
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",  # Or "gemini-1.5-pro", or other available Gemini models
                temperature=0.7,
                # You might not need to explicitly pass api_key if GOOGLE_API_KEY is in your environment
                # However, you can pass it as google_api_key=os.getenv('GOOGLE_API_KEY') if needed
            
                api_key=os.getenv('GOOGLE_API_KEY')
            )
            
            # Email generation prompt template
            self.email_prompt = ChatPromptTemplate.from_template("""
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
            
        except Exception as e:
            st.error(f"Failed to initialize email generator: {e}")
            self.llm = None
    
    def generate_personalized_email(self, influencer_data: Dict, campaign_data: Dict) -> Dict:
        """Generate a personalized email for a specific influencer."""
        
        if not self.llm:
            return {
                'success': False,
                'error': 'Email generator not initialized. Check OpenAI API key.'
            }
        
        try:
            # Prepare influencer data
            name = influencer_data.get('Name', 'there')
            platforms = influencer_data.get('Platform(s)', 'social media')
            niche = influencer_data.get('Niche', 'your field')
            followers = influencer_data.get('Followers', 'your audience')
            bio = influencer_data.get('Bio/Description', 'your content')
            recent_content = influencer_data.get('Recent Content', 'your recent posts')
            
            # Default campaign data
            brand_name = campaign_data.get('brand_name', 'Our Brand')
            campaign_type = campaign_data.get('campaign_type', 'Brand Partnership')
            target_audience = campaign_data.get('target_audience', 'engaged social media users')
            campaign_goals = campaign_data.get('campaign_goals', 'increase brand awareness and engagement')
            
            # Generate email using LLM
            response = self.llm.invoke(
                self.email_prompt.format(
                    name=name,
                    platforms=platforms,
                    niche=niche,
                    followers=followers,
                    bio=bio,
                    recent_content=recent_content,
                    brand_name=brand_name,
                    campaign_type=campaign_type,
                    target_audience=target_audience,
                    campaign_goals=campaign_goals
                )
            )
            
            email_content = response.content.strip()
            
            # Extract subject line if present
            lines = email_content.split('\n')
            subject = f"Partnership Opportunity with {brand_name}"
            body = email_content
            
            for i, line in enumerate(lines):
                if line.lower().startswith('subject:'):
                    subject = line.replace('Subject:', '').replace('subject:', '').strip()
                    body = '\n'.join(lines[i+1:]).strip()
                    break
            
            return {
                'success': True,
                'subject': subject,
                'body': body,
                'full_email': email_content
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to generate email: {str(e)}'
            }


class EmailSender:
    """Handle email sending functionality."""
    
    def __init__(self):
        """Initialize email sender with SMTP configuration."""
        # Test email configuration (hardcoded for testing)
        self.test_email = "ahmedaziz.benayed03@gmail.com"  # Replace with your test email
        
        # SMTP configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        
        self.configured = all([self.email_user, self.email_password])
    
    def send_email(self, subject: str, body: str, influencer_name: str = "Influencer") -> Dict:
        """Send email to the test email address."""
        
        if not self.configured:
            return {
                'success': False,
                'error': 'Email credentials not configured. Set EMAIL_USER and EMAIL_PASSWORD environment variables.'
            }
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = self.test_email
            msg['Subject'] = f"[TEST] {subject}"
            
            # Add test disclaimer to body
            test_body = f"""
🧪 TEST EMAIL - Influencer Outreach System
==========================================
Target Influencer: {influencer_name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

[This is a test email. In production, this would be sent to the actual influencer.]

GENERATED EMAIL CONTENT:
{'-'*50}
{body}
{'-'*50}

This email was generated using AI and would be sent to: {influencer_name}
System Status: Working correctly ✅
"""
            
            msg.attach(MIMEText(test_body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            return {
                'success': True,
                'message': f'Test email sent successfully to {self.test_email}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to send email: {str(e)}'
            }


class StreamlitInfluencerApp:
    """Enhanced Streamlit application for influencer research with personalized outreach."""
    
    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()
        self.email_generator = EmailGenerator()
        self.email_sender = EmailSender()
        
    def setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="AI Influencer Research Assistant",
            page_icon="🎯",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS for better styling
        st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 0.5rem 0;
        }
        
        .status-running {
            background-color: #ffd700;
            color: #000;
            padding: 0.5rem;
            border-radius: 5px;
            text-align: center;
        }
        
        .status-complete {
            background-color: #90EE90;
            color: #000;
            padding: 0.5rem;
            border-radius: 5px;
            text-align: center;
        }
        
        .status-error {
            background-color: #FFB6C1;
            color: #000;
            padding: 0.5rem;
            border-radius: 5px;
            text-align: center;
        }
        
        .influencer-card {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            background: #f9f9f9;
        }
        
        .contact-button {
            background-color: #28a745;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
        }
        
        .contact-button:hover {
            background-color: #218838;
        }
        
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'research_history' not in st.session_state:
            st.session_state.research_history = []
        if 'current_research' not in st.session_state:
            st.session_state.current_research = None
        if 'workflow' not in st.session_state:
            st.session_state.workflow = None
        if 'query_analyzer' not in st.session_state:
            st.session_state.query_analyzer = None
        if 'parsed_influencers' not in st.session_state:
            st.session_state.parsed_influencers = []
        if 'campaign_config' not in st.session_state:
            st.session_state.campaign_config = {
                'brand_name': 'Your Brand',
                'campaign_type': 'Brand Partnership',
                'target_audience': 'engaged social media users',
                'campaign_goals': 'increase brand awareness and engagement'
            }
    
    def render_header(self):
        """Render the main header."""
        st.markdown('<h1 class="main-header">🎯 AI Influencer Research & Outreach Assistant</h1>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Status indicators
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card"><h3>🚀</h3><p>Multi-Agent AI</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-card"><h3>🔍</h3><p>Smart Analysis</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="metric-card"><h3>📊</h3><p>Professional Reports</p></div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="metric-card"><h3>✉️</h3><p>AI Email Outreach</p></div>', unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the sidebar with configuration and history."""
        with st.sidebar:
            st.header("🔧 Configuration")
            
            # Campaign Configuration
            with st.expander("📧 Campaign Settings", expanded=True):
                st.session_state.campaign_config['brand_name'] = st.text_input(
                    "Brand Name", 
                    value=st.session_state.campaign_config['brand_name']
                )
                st.session_state.campaign_config['campaign_type'] = st.selectbox(
                    "Campaign Type",
                    ["Brand Partnership", "Product Review", "Event Promotion", "Sponsored Content", "Ambassador Program"],
                    index=0
                )
                st.session_state.campaign_config['target_audience'] = st.text_input(
                    "Target Audience",
                    value=st.session_state.campaign_config['target_audience']
                )
                st.session_state.campaign_config['campaign_goals'] = st.text_area(
                    "Campaign Goals",
                    value=st.session_state.campaign_config['campaign_goals'],
                    height=100
                )
            
            # Email Configuration Status
            with st.expander("📧 Email Settings"):
                if self.email_sender.configured:
                    st.success("✅ Email configuration ready")
                    st.info(f"Test emails will be sent to: {self.email_sender.test_email}")
                else:
                    st.error("❌ Email not configured")
                    st.warning("Set EMAIL_USER and EMAIL_PASSWORD environment variables")
                
                if st.button("🧪 Test Email System"):
                    self.test_email_system()
            
            # API Status Check
            if st.button("🔍 Check API Status"):
                self.check_api_status()
            
            st.header("📊 Research Statistics")
            if st.session_state.research_history:
                total_searches = len(st.session_state.research_history)
                successful_searches = len([r for r in st.session_state.research_history if r.get('status') == 'completed'])
                
                st.metric("Total Searches", total_searches)
                st.metric("Successful", successful_searches)
                st.metric("Success Rate", f"{(successful_searches/total_searches)*100:.1f}%")
            else:
                st.info("No research history yet")
            
            st.header("🕒 Recent Searches")
            if st.session_state.research_history:
                for i, research in enumerate(st.session_state.research_history[-3:]):
                    with st.expander(f"Search {len(st.session_state.research_history)-i}"):
                        st.write(f"**Query:** {research['query'][:50]}...")
                        st.write(f"**Status:** {research['status']}")
                        st.write(f"**Time:** {research['timestamp']}")
    
    def test_email_system(self):
        """Test the email system functionality."""
        with st.spinner("🧪 Testing email system..."):
            result = self.email_sender.send_email(
                subject="Email System Test",
                body="This is a test email to verify the email system is working correctly.",
                influencer_name="Test System"
            )
            
            if result['success']:
                st.success(result['message'])
            else:
                st.error(result['error'])
    
    def check_api_status(self):
        """Check API configuration status."""
        try:
            settings.validate()
            st.success("✅ All API keys configured correctly!")
        except ValueError as e:
            st.error(f"❌ Configuration error: {e}")
    
    def parse_influencers_from_result(self, result: str) -> List[Dict]:
        """Parse influencer data from research results."""
        influencers = []
        
        try:
            lines = result.split('\n')
            table_lines = [line for line in lines if line.strip().startswith('|') and '---' not in line]
            
            if len(table_lines) > 1:  # Header + data rows
                headers = [col.strip() for col in table_lines[0].split('|')[1:-1]]
                
                for line in table_lines[1:]:
                    cols = [col.strip() for col in line.split('|')[1:-1]]
                    if len(cols) == len(headers):
                        influencer = dict(zip(headers, cols))
                        influencers.append(influencer)
            
        except Exception as e:
            st.error(f"Error parsing influencers: {e}")
        
        return influencers
    
    def render_contact_button(self, influencer: Dict, index: int):
        """Render contact button for an influencer."""
        if st.button(f"📧 Contact", key=f"contact_{index}", help=f"Generate personalized email for {influencer.get('Name', 'this influencer')}"):
            self.generate_and_show_email(influencer, index)
    
    def generate_and_show_email(self, influencer: Dict, index: int):
        """Generate and display personalized email for an influencer."""
        st.markdown("---")
        st.subheader(f"✉️ Personalized Email for {influencer.get('Name', 'Influencer')}")
        
        with st.spinner("🤖 AI is generating a personalized email..."):
            email_result = self.email_generator.generate_personalized_email(
                influencer, st.session_state.campaign_config
            )
        
        if email_result['success']:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**📧 Generated Email:**")
                
                # Display subject
                st.write(f"**Subject:** {email_result['subject']}")
                
                # Display email body in a text area for editing
                edited_body = st.text_area(
                    "Email Body (editable):",
                    value=email_result['body'],
                    height=400,
                    key=f"email_body_{index}"
                )
                
                # Send email button
                col_send, col_copy = st.columns(2)
                
                with col_send:
                    if st.button(f"📨 Send Test Email", key=f"send_{index}"):
                        self.send_email_to_test(
                            email_result['subject'], 
                            edited_body, 
                            influencer.get('Name', 'Influencer')
                        )
                
                with col_copy:
                    st.code(f"Subject: {email_result['subject']}\n\n{edited_body}", language='text')
            
            with col2:
                st.write("**👤 Influencer Details:**")
                for key, value in influencer.items():
                    if value and value.strip():
                        st.write(f"**{key}:** {value}")
                
                st.write("**📊 Campaign Context:**")
                for key, value in st.session_state.campaign_config.items():
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        
        else:
            st.error(f"❌ Failed to generate email: {email_result['error']}")
    
    def send_email_to_test(self, subject: str, body: str, influencer_name: str):
        """Send the generated email to test address."""
        with st.spinner("📨 Sending test email..."):
            result = self.email_sender.send_email(subject, body, influencer_name)
            
            if result['success']:
                st.success(f"✅ {result['message']}")
                st.balloons()
            else:
                st.error(f"❌ {result['error']}")
    
    def render_query_interface(self):
        """Render the main query interface."""
        st.header("🔍 Research Query")
        
        # Query examples
        with st.expander("💡 See Example Queries", expanded=False):
            examples = [
                "Find AI and machine learning influencers with 50K+ followers",
                "I want fitness YouTubers in Europe who focus on bodybuilding",
                "Search for beauty influencers on Instagram and TikTok in North America",
                "Find gaming streamers on Twitch with high engagement rates",
                "Look for food bloggers and cooking influencers worldwide",
                "Find travel influencers who focus on budget travel and backpacking",
                "Search for business and entrepreneurship thought leaders on LinkedIn",
                "Find creative and art influencers with authentic audiences"
            ]
            
            for example in examples:
                if st.button(f"🎯 {example}", key=f"example_{hash(example)}"):
                    st.session_state.selected_example = example
                    st.rerun()
        
        # Main query input
        query_placeholder = "Enter your influencer research query here..."
        if hasattr(st.session_state, 'selected_example'):
            query_placeholder = st.session_state.selected_example
            del st.session_state.selected_example
        
        if hasattr(st.session_state, 'rerun_query'):
            query_placeholder = st.session_state.rerun_query
            del st.session_state.rerun_query
        
        query = st.text_area(
            "What type of influencers are you looking for?",
            value=query_placeholder if query_placeholder != "Enter your influencer research query here..." else "",
            height=100,
            placeholder=query_placeholder
        )
        
        # Query analysis
        if query and len(query) > 10:
            if st.session_state.query_analyzer is None:
                st.session_state.query_analyzer = QueryAnalyzer()
            
            with st.expander("🧠 Smart Query Analysis", expanded=True):
                try:
                    analysis = st.session_state.query_analyzer.analyze_query(query)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**📍 Detected Niches:**")
                        for niche in analysis.niche:
                            st.write(f"• {niche}")
                        
                        st.write("**📱 Target Platforms:**")
                        for platform in analysis.platforms:
                            st.write(f"• {platform}")
                    
                    with col2:
                        st.write("**🌍 Geographic Focus:**")
                        for geo in analysis.geographic_focus:
                            st.write(f"• {geo}")
                        
                        if analysis.audience_size:
                            st.write(f"**👥 Audience Size:** {analysis.audience_size}")
                    
                    st.write("**🎯 Optimized Search Terms:**")
                    for i, term in enumerate(analysis.search_terms[:5], 1):
                        st.write(f"{i}. {term}")
                        
                except Exception as e:
                    st.warning(f"Query analysis failed: {e}")
        
        # Research controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            start_research = st.button("🚀 Start Research", type="primary", disabled=len(query) < 10)
        
        with col2:
            if st.button("🔄 Clear Query"):
                st.rerun()
        
        with col3:
            if st.button("📊 View Results"):
                if st.session_state.current_research:
                    st.session_state.show_results = True
        
        return query, start_research
    
    def run_research(self, query: str):
        """Execute the research workflow with real-time updates."""
        # Initialize workflow
        if st.session_state.workflow is None:
            with st.spinner("⚡ Initializing AI agents..."):
                try:
                    st.session_state.workflow = InfluencerResearchWorkflow()
                    st.success("✅ Multi-agent system ready!")
                except Exception as e:
                    st.error(f"❌ Failed to initialize workflow: {e}")
                    return None
        
        # Create progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        time_text = st.empty()
        
        # Research phases
        phases = [
            "🔍 Query Analysis & Strategy Planning",
            "📊 Multi-Platform Data Collection", 
            "✅ Contact Information Verification",
            "🔍 Quality Control & Validation",
            "📄 Professional Report Generation"
        ]
        
        start_time = time.time()
        
        try:
            # Update progress through phases
            for i, phase in enumerate(phases):
                progress_bar.progress((i + 1) / len(phases))
                status_text.markdown(f'<div class="status-running">{phase}</div>', unsafe_allow_html=True)
                time_text.text(f"⏱️ Elapsed: {time.time() - start_time:.1f}s")
                
                if i == 0:
                    time.sleep(1)  # Simulate phase timing
                elif i < len(phases) - 1:
                    time.sleep(2)
            
            # Run actual research
            status_text.markdown('<div class="status-running">🔄 Running comprehensive research...</div>', unsafe_allow_html=True)
            
            result = st.session_state.workflow.run_research(query)
            
            # Complete
            total_time = time.time() - start_time
            progress_bar.progress(1.0)
            status_text.markdown('<div class="status-complete">🎉 Research completed successfully!</div>', unsafe_allow_html=True)
            time_text.text(f"✅ Completed in {total_time:.1f}s")
            
            # Parse influencers for contact functionality
            parsed_influencers = self.parse_influencers_from_result(result)
            st.session_state.parsed_influencers = parsed_influencers
            
            # Store result
            research_record = {
                'query': query,
                'result': result,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'duration': total_time,
                'status': 'completed' if result and result != "No results generated" else 'failed',
                'influencers': parsed_influencers
            }
            
            st.session_state.research_history.append(research_record)
            st.session_state.current_research = research_record
            
            return research_record
            
        except Exception as e:
            progress_bar.progress(0)
            status_text.markdown(f'<div class="status-error">❌ Research failed: {str(e)}</div>', unsafe_allow_html=True)
            
            # Store failed result
            research_record = {
                'query': query,
                'result': None,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'duration': time.time() - start_time,
                'status': 'failed',
                'error': str(e)
            }
            
            st.session_state.research_history.append(research_record)
            return None
    
    def display_results_with_contact(self, research_record: Dict):
        """Display research results with contact buttons for each influencer."""
        if not research_record or not research_record.get('result'):
            st.error("❌ No results to display")
            return
        
        result = research_record['result']
        
        st.header("📊 Research Results & Contact Management")
        
        # Results summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("⏱️ Duration", f"{research_record['duration']:.1f}s")
        with col2:
            st.metric("📄 Content Length", f"{len(result):,} chars")
        with col3:
            word_count = len(result.split()) if result else 0
            st.metric("📝 Word Count", f"{word_count:,}")
        with col4:
            influencer_count = len(research_record.get('influencers', []))
            st.metric("👥 Profiles Found", influencer_count)
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["👥 Influencers & Contact", "📋 Full Report", "📊 Analytics", "📁 Export"])
        
        with tab1:
            st.subheader("🎯 Influencer Profiles with Contact Options")
            
            if research_record.get('influencers'):
                st.info(f"💡 Click 'Contact' next to any influencer to generate a personalized AI-written email!")
                
                # Display influencers in a more interactive format
                for i, influencer in enumerate(research_record['influencers']):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"### {i+1}. {influencer.get('Name', 'Unknown Influencer')}")
                            
                            # Create columns for influencer details
                            detail_cols = st.columns(3)
                            
                            with detail_cols[0]:
                                st.write(f"**Platform(s):** {influencer.get('Platform(s)', 'N/A')}")
                                st.write(f"**Followers:** {influencer.get('Followers', 'N/A')}")
                            
                            with detail_cols[1]:
                                st.write(f"**Niche:** {influencer.get('Niche', 'N/A')}")
                                st.write(f"**Engagement:** {influencer.get('Engagement Rate', 'N/A')}")
                            
                            with detail_cols[2]:
                                st.write(f"**Location:** {influencer.get('Location', 'N/A')}")
                                st.write(f"**Contact:** {influencer.get('Contact Info', 'N/A')}")
                            
                            # Show bio/description if available
                            if influencer.get('Bio/Description'):
                                st.write(f"**Bio:** {influencer.get('Bio/Description')[:150]}...")
                        
                        with col2:
                            st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
                            self.render_contact_button(influencer, i)
                        
                        st.markdown("---")
                
                # Bulk contact options
                st.subheader("📧 Bulk Contact Options")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📨 Generate All Emails", help="Generate personalized emails for all influencers"):
                        self.generate_bulk_emails(research_record['influencers'])
                
                with col2:
                    selected_count = st.number_input("Select first N influencers", min_value=1, max_value=len(research_record['influencers']), value=min(5, len(research_record['influencers'])))
                    if st.button(f"📧 Contact First {selected_count}"):
                        self.generate_bulk_emails(research_record['influencers'][:selected_count])
                
                with col3:
                    if st.button("📊 Export Contact List", help="Export influencer contact information"):
                        self.export_contact_list(research_record['influencers'])
            
            else:
                st.warning("No structured influencer data found. The AI may not have generated results in the expected table format.")
                st.info("Try rephrasing your query to be more specific about the type of influencers you're looking for.")
        
        with tab2:
            st.subheader("Complete Research Report")
            if result:
                st.markdown(result)
            else:
                st.warning("No results generated")
        
        with tab3:
            st.subheader("Data Analysis & Insights")
            if research_record.get('influencers'):
                self.analyze_influencer_data(research_record['influencers'])
            else:
                st.info("No structured data available for analysis")
        
        with tab4:
            st.subheader("Export & Download Options")
            self.render_export_options(research_record)
    
    def generate_bulk_emails(self, influencers: List[Dict]):
        """Generate emails for multiple influencers."""
        st.subheader(f"📧 Bulk Email Generation for {len(influencers)} Influencers")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        generated_emails = []
        
        for i, influencer in enumerate(influencers):
            progress_bar.progress((i + 1) / len(influencers))
            status_text.text(f"Generating email for {influencer.get('Name', f'Influencer {i+1}')}...")
            
            email_result = self.email_generator.generate_personalized_email(
                influencer, st.session_state.campaign_config
            )
            
            if email_result['success']:
                generated_emails.append({
                    'influencer': influencer,
                    'email': email_result
                })
            
            time.sleep(0.5)  # Small delay to show progress
        
        progress_bar.progress(1.0)
        status_text.text("✅ All emails generated!")
        
        # Display generated emails
        st.success(f"🎉 Successfully generated {len(generated_emails)} personalized emails!")
        
        for i, email_data in enumerate(generated_emails):
            influencer = email_data['influencer']
            email = email_data['email']
            
            with st.expander(f"📧 Email for {influencer.get('Name', f'Influencer {i+1}')}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Subject:** {email['subject']}")
                    st.text_area(
                        "Email Body:",
                        value=email['body'],
                        height=300,
                        key=f"bulk_email_{i}"
                    )
                    
                    if st.button(f"📨 Send to Test Email", key=f"bulk_send_{i}"):
                        self.send_email_to_test(
                            email['subject'],
                            email['body'],
                            influencer.get('Name', f'Influencer {i+1}')
                        )
                
                with col2:
                    st.write("**Influencer Details:**")
                    for key, value in influencer.items():
                        if value and str(value).strip():
                            st.write(f"**{key}:** {value}")
    
    def export_contact_list(self, influencers: List[Dict]):
        """Export influencer contact information as CSV."""
        try:
            df = pd.DataFrame(influencers)
            csv_data = df.to_csv(index=False)
            
            st.download_button(
                label="⬇️ Download Contact List (CSV)",
                data=csv_data,
                file_name=f"influencer_contacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            st.success("📊 Contact list ready for download!")
            
        except Exception as e:
            st.error(f"Failed to export contact list: {e}")
    
    def analyze_influencer_data(self, influencers: List[Dict]):
        """Analyze and visualize influencer data."""
        try:
            df = pd.DataFrame(influencers)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Platform distribution
                if 'Platform(s)' in df.columns:
                    platforms = df['Platform(s)'].str.split(',').explode().str.strip()
                    platform_counts = platforms.value_counts().head(10)
                    
                    if not platform_counts.empty:
                        fig = px.pie(
                            values=platform_counts.values, 
                            names=platform_counts.index,
                            title="📱 Platform Distribution"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Niche distribution
                if 'Niche' in df.columns:
                    niche_counts = df['Niche'].value_counts().head(8)
                    if not niche_counts.empty:
                        fig = px.bar(
                            x=niche_counts.values,
                            y=niche_counts.index,
                            orientation='h',
                            title="🎯 Niche Distribution"
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Location distribution
                if 'Location' in df.columns:
                    location_counts = df['Location'].value_counts().head(10)
                    if not location_counts.empty:
                        fig = px.bar(
                            x=location_counts.index,
                            y=location_counts.values,
                            title="🌍 Geographic Distribution"
                        )
                        fig.update_xaxis(tickangle=45)
                        st.plotly_chart(fig, use_container_width=True)
                
                # Summary statistics
                st.subheader("📊 Summary Statistics")
                st.metric("Total Influencers", len(influencers))
                
                if 'Platform(s)' in df.columns:
                    unique_platforms = df['Platform(s)'].str.split(',').explode().str.strip().nunique()
                    st.metric("Unique Platforms", unique_platforms)
                
                if 'Niche' in df.columns:
                    unique_niches = df['Niche'].nunique()
                    st.metric("Unique Niches", unique_niches)
                
                if 'Location' in df.columns:
                    unique_locations = df['Location'].nunique()
                    st.metric("Unique Locations", unique_locations)
        
        except Exception as e:
            st.error(f"Analysis failed: {e}")
    
    def render_export_options(self, research_record: Dict):
        """Render export and download options."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Download as Markdown"):
                self.download_as_markdown(research_record)
        
        with col2:
            if st.button("📊 Download as JSON"):
                self.download_as_json(research_record)
        
        with col3:
            if st.button("📈 Download as CSV"):
                self.download_as_csv(research_record)
        
        # File location info
        st.info(f"📁 Files are also automatically saved to: {settings.OUTPUT_DIR}")
    
    def download_as_markdown(self, research_record: Dict):
        """Prepare markdown download."""
        content = f"""# Influencer Research Report
## Query: {research_record['query']}
## Generated: {research_record['timestamp']}
## Duration: {research_record['duration']:.1f} seconds

---

{research_record['result']}

---

## Campaign Configuration
- **Brand Name:** {st.session_state.campaign_config['brand_name']}
- **Campaign Type:** {st.session_state.campaign_config['campaign_type']}
- **Target Audience:** {st.session_state.campaign_config['target_audience']}
- **Campaign Goals:** {st.session_state.campaign_config['campaign_goals']}
"""
        st.download_button(
            label="⬇️ Download Markdown",
            data=content,
            file_name=f"influencer_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
    
    def download_as_json(self, research_record: Dict):
        """Prepare JSON download."""
        export_data = {
            **research_record,
            'campaign_config': st.session_state.campaign_config
        }
        json_data = json.dumps(export_data, indent=2)
        st.download_button(
            label="⬇️ Download JSON",
            data=json_data,
            file_name=f"research_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    def download_as_csv(self, research_record: Dict):
        """Extract and prepare CSV download."""
        try:
            if research_record.get('influencers'):
                df = pd.DataFrame(research_record['influencers'])
                csv_data = df.to_csv(index=False)
                
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv_data,
                    file_name=f"influencer_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No structured table data found for CSV export")
                
        except Exception as e:
            st.error(f"CSV export failed: {e}")
    
    def run(self):
        """Main application loop."""
        self.render_header()
        self.render_sidebar()
        
        # Main content area
        query, start_research = self.render_query_interface()
        
        # Handle research execution
        if start_research and query and len(query) >= 10:
            st.markdown("---")
            st.header("🔄 Research in Progress")
            
            research_record = self.run_research(query)
            
            if research_record and research_record.get('result'):
                st.success("✅ Research completed successfully!")
                time.sleep(1)  # Brief pause before showing results
                st.session_state.show_results = True
        
        # Display results if available
        if hasattr(st.session_state, 'show_results') and st.session_state.show_results:
            if st.session_state.current_research:
                st.markdown("---")
                self.display_results_with_contact(st.session_state.current_research)
        
        # Handle invalid queries
        if start_research and (not query or len(query) < 10):
            st.error("❌ Please provide a detailed query (at least 10 characters)")


def main():
    """Main entry point for Streamlit app."""
    try:
        app = StreamlitInfluencerApp()
        app.run()
    except Exception as e:
        st.error(f"Application error: {e}")
        st.error("Please check your configuration and try again.")


if __name__ == "__main__":
    main()