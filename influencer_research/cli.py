"""Command-line interface: interactive mode, or one-shot with the query as arguments."""

import os
import sys
from datetime import datetime

from influencer_research.config import settings
from influencer_research.query_analyzer import QueryAnalyzer
from influencer_research.workflow import InfluencerResearchWorkflow


class InteractiveResearchCLI:
    """Interactive command-line interface for influencer research."""
    
    def __init__(self):
        self.workflow = None
        self.query_analyzer = QueryAnalyzer()
        # Ensure output directory exists at initialization
        self._ensure_output_directory()
    
    def _ensure_output_directory(self):
        """Ensure the output directory exists and is writable."""
        try:
            # Create the output directory
            os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
            
            # Test write permissions
            test_file = os.path.join(settings.OUTPUT_DIR, "test_write.tmp")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            
            print(f"✅ Output directory ready: {os.path.abspath(settings.OUTPUT_DIR)}")
            
        except Exception as e:
            print(f"⚠️ Warning: Issue with output directory {settings.OUTPUT_DIR}: {e}")
            # Try to create an alternative output directory
            alt_dir = os.path.join(os.getcwd(), "research_outputs")
            try:
                os.makedirs(alt_dir, exist_ok=True)
                settings.OUTPUT_DIR = alt_dir
                print(f"✅ Using alternative output directory: {os.path.abspath(alt_dir)}")
            except Exception as e2:
                print(f"❌ Cannot create output directory: {e2}")
                print("Reports will be saved to current directory as fallback")
    
    def display_welcome(self):
        """Display welcome screen with enhanced branding."""
        print("\n" + "="*80)
        print("🎯 AI INFLUENCER RESEARCH ASSISTANT")
        print("="*80)
        print("🚀 Powered by Multi-Agent AI | 🔍 Smart Query Analysis | 📊 Professional Reports")
        print("\nWelcome! I'll help you discover the perfect influencers for your campaigns.")
        print("I can search across all major platforms and provide verified contact details.")
        print(f"📁 Reports will be saved to: {os.path.abspath(settings.OUTPUT_DIR)}")
        
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
            print("\n🔍 What type of influencers are you looking for?")
            print("💡 Tip: Be specific about niche, platform, location, or audience size")
            query = input("\n> ").strip()
            
            if not query:
                print("❌ Please enter a search query.")
                continue
                
            if len(query) < 10:
                print("❌ Please provide more details (at least 10 characters).")
                continue
            
            # Analyze the query and show insights
            try:
                analysis = self.query_analyzer.analyze_query(query)
                print("\n🧠 SMART ANALYSIS:")
                print(f"   📍 Niche: {', '.join(analysis.niche)}")
                print(f"   📱 Platforms: {', '.join(analysis.platforms)}")
                print(f"   🌍 Geographic Focus: {', '.join(analysis.geographic_focus)}")
                if analysis.audience_size:
                    print(f"   👥 Audience Size: {analysis.audience_size}")
                
                # Show optimized search terms
                print("\n🎯 I'll search for:")
                for i, term in enumerate(analysis.search_terms[:5], 1):
                    print(f"   {i}. {term}")
            except Exception as e:
                print(f"⚠️ Query analysis failed: {e}")
                print("🔄 Continuing with raw query...")
            
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
        print("\n🚀 INITIALIZING RESEARCH WORKFLOW")
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
            import traceback
            traceback.print_exc()
            return None, 0
    
    def display_results(self, result: str, duration: float):
        """Display results with enhanced formatting."""
        print("\n" + "="*80)
        print("🎉 RESEARCH COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(f"⏱️  Total time: {duration:.1f} seconds")
        print(f"📄 Result length: {len(result)} characters")
        print(f"💾 Reports saved to: {os.path.abspath(settings.OUTPUT_DIR)}/")
        
        print("\n📊 RESEARCH SUMMARY:")
        print("-"*50)
        
        # Try to extract some quick stats from the result
        if result and result != "No results generated":
            lines = result.split('\n')
            word_count = len(result.split())
            print(f"   📝 Total content: {word_count} words, {len(lines)} lines")
            
            # Look for influencer mentions
            influencer_indicators = ['@', 'followers', 'engagement', 'contact']
            relevant_lines = [line for line in lines if any(indicator in line.lower() for indicator in influencer_indicators)]
            print(f"   👥 Potential influencer profiles found: {len(relevant_lines)}")
            
            # Check if we have a proper table structure
            table_rows = [line for line in lines if line.strip().startswith('|') and '---' not in line]
            if table_rows:
                print(f"   📋 Structured profiles: {max(0, len(table_rows) - 1)}")  # Subtract header row
        else:
            print("   ⚠️ No structured results generated")
        
        print("-"*50)
        print("\n📋 RESEARCH RESULTS PREVIEW:")
        print("="*80)
        
        # Show first 2000 characters as preview
        if result and len(result) > 2000:
            print(result[:2000] + "...")
            print("\n[... truncated for display. Full results saved to file ...]")
        else:
            print(result if result else "No results generated")
    
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
                
                if result and result != "No results generated":
                    self.display_results(result, duration)
                else:
                    print("❌ Research failed or returned no results.")
                    print("💡 Try a different query or check your API keys.")
                
                # Ask for another search
                print("\n🔄 Would you like to research different influencers? (y/n): ", end="")
                continue_search = input().strip().lower()
                
                if continue_search not in ['y', 'yes']:
                    break
            
            print("\n👋 Thank you for using AI Influencer Research Assistant!")
            print(f"💡 Your reports are saved in: {os.path.abspath(settings.OUTPUT_DIR)}")
            
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
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Main entry point - supports both CLI args and interactive mode."""
    if len(sys.argv) > 1:
        # Command line mode (backwards compatibility)
        query = " ".join(sys.argv[1:])
        try:
            settings.validate()
            
            # Ensure output directory exists
            os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
            
            workflow = InfluencerResearchWorkflow()
            result = workflow.run_research(query)
            print("RESULT:")
            print(result)
            print(f"\nReport saved to: {os.path.abspath(settings.OUTPUT_DIR)}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        # Interactive mode (new enhanced experience)
        cli = InteractiveResearchCLI()
        cli.run()


if __name__ == "__main__":
    main()