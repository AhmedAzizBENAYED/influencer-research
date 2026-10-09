"""Research agents for the influencer sourcing workflow."""

from typing import Literal

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, MessagesState
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from influencer_research.config import settings
from influencer_research.prompts import get_reporter_prompt, get_researcher_prompt, get_verifier_prompt
from influencer_research.query_analyzer import QueryAnalyzer
from influencer_research.tools import get_reporter_tools, get_research_tools

_query_analyzer = QueryAnalyzer()


class ResearchAgents:
    """Factory for the three ReAct agents sharing one Gemini client."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            api_key=settings.GOOGLE_API_KEY,
            temperature=settings.MODEL_TEMPERATURE,
        )

    def create_research_agent(self):
        return create_react_agent(self.llm, tools=get_research_tools(), prompt=get_researcher_prompt())

    def create_verifier_agent(self):
        # The verifier reasons over the researcher's citations only — no tools
        return create_react_agent(self.llm, tools=[], prompt=get_verifier_prompt())

    def create_reporter_agent(self):
        return create_react_agent(self.llm, tools=get_reporter_tools(), prompt=get_reporter_prompt())


def enhance_query(query: str) -> str:
    """Prepend a structured breakdown of the brief (niche, platforms, region, ...) to guide the researcher."""
    analysis = _query_analyzer.analyze_query(query)

    return f"""
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
Focus on finding {settings.MIN_INFLUENCERS_REQUIRED}-20 high-quality influencers that match these criteria.
"""


def research_node(
    state: MessagesState,
    research_agent
) -> Command[Literal["verifier_agent"]]:
    """Run the researcher on the enhanced brief, then always hand off to the verifier.

    The researcher's "FINAL ANSWER" only means its draft is complete; routing to END here
    would skip verification and report generation.
    """
    original_message = state["messages"][0].content
    enhanced_query = enhance_query(original_message)

    enhanced_state = state.copy()
    enhanced_state["messages"] = [HumanMessage(content=enhanced_query)]
    
    result = research_agent.invoke(enhanced_state)
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="researcher"
    )
    return Command(
        update={
            "messages": result["messages"],
        },
        goto="verifier_agent",
    )


def verify_node(
    state: MessagesState,
    verifier_agent
) -> Command[Literal["researcher", "reporter"]]:
    """Approve the dossier (-> reporter) or send it back to the researcher."""
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
    """Turn the latest research notes into the final Markdown report."""
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