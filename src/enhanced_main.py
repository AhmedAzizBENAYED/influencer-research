"""Enhanced main entry point with interactive CLI for influencer research."""

import sys
import pprint
import os
from datetime import datetime

# Add parent directory to Python path to access variables module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import settings
from variables.workflow.research_workflow import InfluencerResearchWorkflow
from src.utils.query_analyser import QueryAnalyzer


class InteractiveResearchCLI:
    """Interactive command-line interface for influencer research."""
    
    def __init__(self):
        self.workflow = None
        self.query_analyzer = QueryAnalyzer()
    
    def display_welcome(self):
        """Display welcome screen with enhanced branding."""
        print("\n" + "="*80)
        print("🎯 AI INFLUENCER RESEARCH ASSISTANT v2.0")
        print("="*80)
        print("🚀 Powered by Multi-Agent AI | 🔍 Smart Query Analysis | 📊 Professional Reports")
        print("\nWelcome! I'll help you discover the perfect influencers for your campaigns.")
        print("I can search across all major platforms and provide verified contact details.")
        
    def show_examples(self):
        """Show enhanced query examples."""
        examples = [
            "🤖 'Find AI and machine learning influencers with 50K+ followers'",
            "💪 'I want fitness YouTubers in Europe who focus on bodybuilding'", 
            "💄 'Search for beauty influencers on Instagram and TikTok in North America'",
            "🎮 'Find gaming streamers on Twitch with high engagement rates'",
            "🍳 'Look for food bloggers and cooking influencers worldwide'",
            "✈️ 'Find travel influencers who focus on budget travel and backpacking'",
            "💼 'Search for business and entrepreneurship thought leaders on LinkedIn'",
            "🎨 'Find creative and art influencers with authentic audiences'"
        ]
        
        print("\n📝 EXAMPLE QUERIES:")
        print("-" * 50)
        for example in examples:
            print(f"   {example}")
        print("-" * 50)
    
    def get_enhanced_query(self):
        """Get and analyze user query with smart suggestions."""
        self.show_examples()
        
        while True:
            print(f"\n🔍 What type of influencers are you looking for?")
            print("💡 Tip: Be specific about niche, platform, location, or audience size")
            query = input("\n> ").strip()
            
            if not query:
                print("❌ Please enter a search query.")
                continue
                
            if len(query) < 10:
                print("❌ Please provide more details (at least 10 characters).")
                continue
            
            # Analyze the query and show insights
            analysis = self.query_analyzer.analyze_query(query)
            print(f"\n🧠 SMART ANALYSIS:")
            print(f"   📍 Niche: {', '.join(analysis.niche)}")
            print(f"   📱 Platforms: {', '.join(analysis.platforms)}")
            print(f"   🌍 Geographic Focus: {', '.join(analysis.geographic_focus)}")
            if analysis.audience_size:
                print(f"   👥 Audience Size: {analysis.audience_size}")
            
            # Show optimized search terms
            print(f"\n🎯 I'll search for:")
            for i, term in enumerate(analysis.search_terms[:5], 1):
                print(f"   {i}. {term}")
            
            print(f"\n📝 Your query: '{query}'")
            confirm = input("✅ Proceed with this research? (y/n/edit): ").strip().lower()
            
            if confirm in ['y', 'yes']:
                return query
            elif confirm in ['edit', 'e']:
                continue
            elif confirm in ['n', 'no']:
                print("👋 Feel free to try a different search!")
                return None
            else:
                print("Please type 'y' for yes, 'n' for no, or 'edit' to modify.")
    
    def run_research_with_progress(self, query: str):
        """Run research with enhanced progress tracking."""
        print(f"\n🚀 INITIALIZING RESEARCH WORKFLOW")
        print("="*60)
        
        try:
            # Initialize workflow
            print("⚡ Loading AI agents...")
            self.workflow = InfluencerResearchWorkflow()
            print("✅ Multi-agent system ready!")
            
            # Start research
            print(f"\n🔍 RESEARCH TARGET: {query}")
            print("="*60)
            print("🔄 Stage 1: Query Analysis & Strategy Planning...")
            print("🔄 Stage 2: Multi-Platform Data Collection...")
            print("🔄 Stage 3: Contact Information Verification...")
            print("🔄 Stage 4: Quality Control & Validation...")
            print("🔄 Stage 5: Professional Report Generation...")
            print("\n⏳ This comprehensive research may take 3-5 minutes...")
            print("📊 Targeting 15-20 high-quality influencer profiles...\n")
            
            # Run the research
            start_time = datetime.now()
            result = self.workflow.run_research(query)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return result, duration
            
        except Exception as e:
            print(f"❌ Research error: {e}")
            return None, 0
    
    def display_results(self, result: str, duration: float):
        """Display results with enhanced formatting."""
        print("\n" + "="*80)
        print("🎉 RESEARCH COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(f"⏱️  Total time: {duration:.1f} seconds")
        print(f"📄 Result length: {len(result)} characters")
        print(f"💾 Report saved to: {settings.OUTPUT_DIR}/")
        
        print("\n📊 RESEARCH SUMMARY:")
        print("-"*50)
        
        # Try to extract some quick stats from the result
        if result:
            lines = result.split('\n')
            word_count = len(result.split())
            print(f"   📝 Total content: {word_count} words, {len(lines)} lines")
            
            # Look for influencer mentions
            influencer_indicators = ['@', 'followers', 'engagement', 'contact']
            relevant_lines = [line for line in lines if any(indicator in line.lower() for indicator in influencer_indicators)]
            print(f"   👥 Potential influencer profiles found: {len(relevant_lines)}")
        
        print("-"*50)
        print("\n📋 FULL RESEARCH RESULTS:")
        print("="*80)
        pprint.pprint(result, width=120)
    
    def run(self):
        """Main interactive loop."""
        try:
            # Validate configuration
            settings.validate()
            print("✅ API keys validated successfully")
            
            self.display_welcome()
            
            while True:
                query = self.get_enhanced_query()
                
                if not query:
                    break
                
                # Run research
                result, duration = self.run_research_with_progress(query)
                
                if result:
                    self.display_results(result, duration)
                else:
                    print("❌ Research failed. Please try again with a different query.")
                
                # Ask for another search
                print(f"\n🔄 Would you like to research different influencers? (y/n): ", end="")
                continue_search = input().strip().lower()
                
                if continue_search not in ['y', 'yes']:
                    break
            
            print("\n👋 Thank you for using AI Influencer Research Assistant!")
            print("💡 Your reports are saved in the outputs/ directory for future reference.")
            
        except KeyboardInterrupt:
            print("\n\n👋 Research cancelled by user. Goodbye!")
            sys.exit(0)
        except ValueError as e:
            print(f"❌ Configuration error: {e}")
            print("🔧 Please check your .env file and ensure all required API keys are set.")
            print("📖 See README.md for setup instructions.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            sys.exit(1)


def main():
    """Main entry point - supports both CLI args and interactive mode."""
    if len(sys.argv) > 1:
        # Command line mode (backwards compatibility)
        query = " ".join(sys.argv[1:])
        try:
            settings.validate()
            workflow = InfluencerResearchWorkflow()
            result = workflow.run_research(query)
            print("RESULT:")
            pprint.pprint(result, width=120)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        # Interactive mode (new enhanced experience)
        cli = InteractiveResearchCLI()
        cli.run()


if __name__ == "__main__":
    main()