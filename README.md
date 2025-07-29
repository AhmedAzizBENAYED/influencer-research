# Influencer Research Application

A sophisticated AI-powered influencer research tool that uses multiple agents to find, verify, and report on influencers in any niche.

## Project Structure

```
influencer-research/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Main entry point
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py            # Configuration and environment variables
│   ├── tools/
│   │   ├── __init__.py
│   │   └── research_tools.py      # API integration tools
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── system_prompts.py      # Agent system prompts
│   ├── agents/
│   │   ├── __init__.py
│   │   └── research_agents.py     # Agent definitions and node logic
│   └── workflow/
│       ├── __init__.py
│       └── research_workflow.py   # Workflow orchestration
├── outputs/                       # Generated reports directory
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .env                          # Your actual environment variables (create this)
└── README.md                     # This file
```

## Setup Instructions

### 1. Clone and Navigate

```bash
git clone <your-repo>
cd influencer-research
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` file with your actual API keys:

```env
TAVILY_API_KEY=your_tavily_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
NOVADA_API_KEY=your_novada_api_key_here
RAPIDAPI_KEY=your_rapidapi_key_here
```

### 5. Create Output Directory

```bash
mkdir outputs
```

## Usage

### Basic Usage

Run with default query:
```bash
cd src
python main.py
```

### Custom Query

Run with your specific research query:
```bash
cd src
python main.py "find fitness influencers in Europe"
```

### Advanced Usage

You can also import and use the workflow programmatically:

```python
from workflow.research_workflow import InfluencerResearchWorkflow

workflow = InfluencerResearchWorkflow()
result = workflow.run_research("find tech influencers in Silicon Valley")
print(result)
```

## Features

- **Multi-Agent System**: Research, verification, and reporting agents work together
- **Multiple Data Sources**: Integrates with Tavily, NovaDA, RapidAPI services
- **Social Platform Coverage**: Instagram, TikTok, YouTube, Twitter, LinkedIn, Facebook
- **Contact Information**: Finds business emails, management contacts, phone numbers
- **Engagement Analysis**: Gathers follower counts, engagement rates, demographics
- **Quality Control**: Verification agent ensures data accuracy and completeness
- **Professional Reports**: Generated Markdown reports with structured data

## API Keys Required

1. **Tavily API**: Web search capabilities
2. **Google API**: Gemini AI model access
3. **NovaDA API**: Google search scraping
4. **RapidAPI**: Social media data access

## Output

The application generates:
- Console output with research progress
- Markdown reports saved to `outputs/` directory
- Structured data tables with influencer information
- Contact details and engagement metrics

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure all required keys are in your `.env` file
2. **Rate Limits**: The application includes timeout handling for API calls
3. **Module Not Found**: Make sure you're running from the `src/` directory

### Debug Mode

For verbose output, you can modify the logging level in `main.py` or add debug prints as needed.

## Development

The codebase is structured for easy extension:

- Add new tools in `src/tools/research_tools.py`
- Modify agent behavior in `src/prompts/system_prompts.py`
- Extend workflow logic in `src/workflow/research_workflow.py`

## Contributing

1. Follow the existing code structure
2. Add type hints for new functions
3. Update documentation for new features
4. Test with various influencer niches

## License

[Add your license information here]