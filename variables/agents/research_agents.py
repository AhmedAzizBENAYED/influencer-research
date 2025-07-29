"""Research agents for the influencer sourcing workflow."""

from typing import Literal
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState, END
from langgraph.types import Command

from src.config.settings import settings
from variables.prompts.system_prompts import get_researcher_prompt, get_verifier_prompt, get_reporter_prompt
from variables.tools.research_tools import get_research_tools, get_reporter_tools
from src.utils.query_analyser import QueryAnalyzer


class ResearchAgents:
    """Factory class for creating research agents."""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            api_key=settings.GOOGLE_API_KEY,
            temperature=0.3  # Slightly more creative for better research
        )
        self.query_analyzer = QueryAnalyzer()
    
    def create_research_agent(self):
        """Create the research agent."""
        return create_react_agent(
            self.llm,
            tools=get_research_tools(),
            prompt=get_researcher_prompt(),
        )
    
    def create_verifier_agent(self):
        """Create the verifier agent."""
        return create_react_agent(
            self.llm,
            tools=[],  # Verifier doesn't need tools in original code
            prompt=get_verifier_prompt(),
        )
    
    def create_reporter_agent(self):
        """Create the reporter agent."""
        return create_react_agent(
            self.llm,
            tools=get_reporter_tools(),
            prompt=get_reporter_prompt(),
        )
    
    def enhance_query(self, query: str) -> str:
        """Enhance user query with structured analysis."""
        analysis = self.query_analyzer.analyze_query(query)
        
        enhanced_query = f"""
ORIGINAL QUERY: {query}

ANALYSIS BREAKDOWN:
• Niche/Industry: {', '.join(analysis.niche)}
• Target Platforms: {', '.join(analysis.platforms)}
• Geographic Focus: {', '.join(analysis.geographic_focus)}
• Audience Size: {analysis.audience_size or 'Any size'}
• Content Types: {', '.join(analysis.content_type)}
• Demographics: {', '.join(analysis.demographics) if analysis.demographics else 'General audience'}

OPTIMIZED SEARCH TERMS:
{chr(10).join(f'• {term}' for term in analysis.search_terms)}

Please use this analysis to conduct comprehensive research across multiple platforms and sources.
Focus on finding 15-20 high-quality influencers that match these criteria.
"""
        return enhanced_query


def get_next_node(last_message: BaseMessage, goto: str):
    """Determine the next node based on the last message."""
    if "FINAL ANSWER" in last_message.content:
        return END
    return goto


def research_node(
    state: MessagesState,
    research_agent
) -> Command[Literal["verifier_agent"]]:
    """Research node logic with enhanced query processing."""
    # Extract original query and enhance it
    original_message = state["messages"][0].content
    agents = ResearchAgents()
    enhanced_query = agents.enhance_query(original_message)
    
    # Create new state with enhanced query
    enhanced_state = state.copy()
    enhanced_state["messages"] = [HumanMessage(content=enhanced_query)]
    
    result = research_agent.invoke(enhanced_state)
    goto = get_next_node(result["messages"][-1], "verifier_agent")
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="researcher"
    )
    return Command(
        update={
            "messages": result["messages"],
        },
        goto=goto,
    )


def verify_node(
    state: MessagesState,
    verifier_agent
) -> Command[Literal["researcher", "reporter"]]:
    """Verifier node logic with enhanced validation."""
    result = verifier_agent.invoke(state)
    
    if "FINAL ANSWER" in result["messages"][-1].content:
        goto = "reporter"
    else:
        goto = "researcher"
    
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="verifier_agent"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )


def report_node(
    state: MessagesState,
    reporter_agent
) -> Command[Literal[END]]:
    """Reporter node logic with enhanced report generation."""
    last_ai = next(m for m in reversed(state["messages"]) if m.type == "ai")
    notes = last_ai.content

    result = reporter_agent.invoke(
        {
            "messages": [
                ("user",
                 f"Raw research notes:\n{notes}\n\n"
                 "Please generate a comprehensive influencer research report with:\n"
                 "1. Executive Summary\n"
                 "2. Influencer Profiles Table\n"
                 "3. Detailed Individual Profiles\n"
                 "4. Industry Insights & Trends\n"
                 "5. Contact Strategy Recommendations\n"
                 "6. Next Steps & Opportunities\n"
                 "Make it professional and actionable for marketing teams.")
            ]
        }
    )

    return Command(
        update={
            "messages": [result["messages"][-1]],
        },
        goto=END,
    )