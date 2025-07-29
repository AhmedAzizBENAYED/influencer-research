"""Main entry point for the influencer research application."""
import os
import sys
import pprint
from config.settings import settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from variables.workflow.research_workflow import InfluencerResearchWorkflow


def get_user_query():
    """Get research query from user with enhanced prompting."""
    print("🎯 INFLUENCER RESEARCH ASSISTANT")
    print("=" * 50)
    print("Welcome! I'll help you find influencers in any niche or topic.")
    print("\nExamples of what you can search for:")
    print("• 'I want to find fitness influencers in Europe'")
    print("• 'Find tech YouTubers with 100k+ subscribers'")
    print("• 'Look for beauty influencers on Instagram and TikTok'")
    print("• 'Find AI and machine learning thought leaders'")
    print("• 'Search for gaming streamers on Twitch'")
    print("• 'Find food bloggers in North America'")
    print("\n" + "=" * 50)
    
    while True:
        query = input("\n🔍 What type of influencers are you looking for?\n> ").strip()
        
        if not query:
            print("❌ Please enter a search query.")
            continue
            
        if len(query) < 10:
            print("❌ Please provide a more detailed description (at least 10 characters).")
            continue
            
        # Confirm the query
        print(f"\n📝 You want to research: '{query}'")
        confirm = input("Is this correct? (y/n): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            return query
        elif confirm in ['n', 'no']:
            print("Let's try again...")
            continue
        else:
            print("Please answer 'y' for yes or 'n' for no.")


def main():
    """Main application entry point."""
    try:
        # Validate configuration
        settings.validate()
        print("✅ Configuration validated successfully\n")
        
        # Get query from command line arguments or prompt user
        if len(sys.argv) > 1:
            query = " ".join(sys.argv[1:])
            print(f"🔍 Using command line query: {query}")
        else:
            query = get_user_query()
        
        # Initialize workflow
        print("\n🚀 Initializing influencer research workflow...")
        workflow = InfluencerResearchWorkflow()
        
        print(f"🔍 Starting research for: {query}")
        print("⏳ This may take a few minutes as we search multiple platforms...")
        print("=" * 80)
        
        # Run research
        result = workflow.run_research(query)
        
        # Display results
        print("\n" + "=" * 80)
        print("📊 RESEARCH RESULTS:")
        print("=" * 80)
        pprint.pprint(result, width=120)
        
        print(f"\n✅ Research completed! Check the {settings.OUTPUT_DIR}/ directory for saved reports.")
        print("\n🔄 Run the program again to search for different influencers!")
        
    except KeyboardInterrupt:
        print("\n\n👋 Research cancelled by user. Goodbye!")
        sys.exit(0)
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please check your .env file and ensure all required API keys are set.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()