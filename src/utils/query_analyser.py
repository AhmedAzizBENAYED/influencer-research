"""Query analysis utilities for enhanced search strategy."""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class QueryAnalysis:
    """Structured analysis of user query."""
    niche: List[str]
    platforms: List[str] 
    geographic_focus: List[str]
    audience_size: Optional[str]
    content_type: List[str]
    demographics: List[str]
    keywords: List[str]
    search_terms: List[str]


class QueryAnalyzer:
    """Analyzes user queries to extract search parameters."""
    
    PLATFORMS = {
        'instagram': ['instagram', 'ig', 'insta'],
        'tiktok': ['tiktok', 'tik tok'],
        'youtube': ['youtube', 'yt', 'youtuber'],
        'twitter': ['twitter', 'x.com', 'tweet'],
        'linkedin': ['linkedin'],
        'facebook': ['facebook', 'fb'],
        'twitch': ['twitch', 'streaming', 'streamer']
    }
    
    AUDIENCE_SIZES = {
        'micro': ['micro', '10k', '50k', 'small'],
        'macro': ['macro', '100k', 'medium'],
        'mega': ['mega', 'million', '1m', 'large', 'top']
    }
    
    NICHES = {
        'tech': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'tech', 'technology', 'software', 'coding', 'programming'],
        'fitness': ['fitness', 'gym', 'workout', 'health', 'wellness', 'bodybuilding', 'yoga'],
        'beauty': ['beauty', 'makeup', 'skincare', 'cosmetics', 'fashion'],
        'gaming': ['gaming', 'gamer', 'esports', 'games', 'streaming'],
        'food': ['food', 'cooking', 'chef', 'recipe', 'culinary', 'restaurant'],
        'travel': ['travel', 'vacation', 'tourism', 'adventure'],
        'lifestyle': ['lifestyle', 'daily life', 'vlog', 'personal'],
        'business': ['business', 'entrepreneur', 'startup', 'marketing', 'finance'],
        'education': ['education', 'teaching', 'learning', 'academic', 'tutorial']
    }
    
    GEOGRAPHIC_REGIONS = {
        'north_america': ['usa', 'us', 'america', 'canada', 'north america'],
        'europe': ['europe', 'eu', 'uk', 'britain', 'germany', 'france', 'spain', 'italy'],
        'asia': ['asia', 'japan', 'korea', 'china', 'india', 'singapore'],
        'global': ['global', 'worldwide', 'international', 'all countries']
    }
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze user query and extract structured information."""
        query_lower = query.lower()
        
        # Extract all components first
        niche = self._extract_niches(query_lower)
        platforms = self._extract_platforms(query_lower)
        geographic_focus = self._extract_geography(query_lower)
        audience_size = self._extract_audience_size(query_lower)
        content_type = self._extract_content_types(query_lower)
        demographics = self._extract_demographics(query_lower)
        keywords = self._extract_keywords(query)
        
        # Generate search terms using the extracted components
        search_terms = self._generate_search_terms(niche, platforms, geographic_focus)
        
        return QueryAnalysis(
            niche=niche,
            platforms=platforms,
            geographic_focus=geographic_focus,
            audience_size=audience_size,
            content_type=content_type,
            demographics=demographics,
            keywords=keywords,
            search_terms=search_terms
        )
    
    def _extract_niches(self, query: str) -> List[str]:
        """Extract niche/industry from query."""
        found_niches = []
        for niche, keywords in self.NICHES.items():
            if any(keyword in query for keyword in keywords):
                found_niches.append(niche)
        return found_niches or ['general']
    
    def _extract_platforms(self, query: str) -> List[str]:
        """Extract platform preferences from query."""
        found_platforms = []
        for platform, keywords in self.PLATFORMS.items():
            if any(keyword in query for keyword in keywords):
                found_platforms.append(platform)
        return found_platforms or ['all']
    
    def _extract_geography(self, query: str) -> List[str]:
        """Extract geographic focus from query."""
        found_regions = []
        for region, keywords in self.GEOGRAPHIC_REGIONS.items():
            if any(keyword in query for keyword in keywords):
                found_regions.append(region)
        return found_regions or ['global']
    
    def _extract_audience_size(self, query: str) -> Optional[str]:
        """Extract audience size preference from query."""
        for size, keywords in self.AUDIENCE_SIZES.items():
            if any(keyword in query for keyword in keywords):
                return size
        return None
    
    def _extract_content_types(self, query: str) -> List[str]:
        """Extract content type preferences from query."""
        content_types = []
        type_keywords = {
            'educational': ['educational', 'tutorial', 'teaching', 'learning'],
            'entertainment': ['funny', 'entertaining', 'comedy', 'fun'],
            'promotional': ['brand', 'sponsored', 'marketing', 'advertising'],
            'lifestyle': ['lifestyle', 'daily', 'personal', 'vlog']
        }
        
        for content_type, keywords in type_keywords.items():
            if any(keyword in query for keyword in keywords):
                content_types.append(content_type)
        
        return content_types or ['all']
    
    def _extract_demographics(self, query: str) -> List[str]:
        """Extract demographic preferences from query."""
        demographics = []
        demo_keywords = {
            'young_adults': ['young', 'gen z', 'millennial', '18-30'],
            'professionals': ['professional', 'business', 'corporate', 'executive'],
            'students': ['student', 'college', 'university', 'academic'],
            'parents': ['parent', 'family', 'mom', 'dad', 'children']
        }
        
        for demo, keywords in demo_keywords.items():
            if any(keyword in query for keyword in keywords):
                demographics.append(demo)
        
        return demographics
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query."""
        # Remove common stop words and extract meaningful terms
        stop_words = {'i', 'want', 'to', 'find', 'the', 'in', 'and', 'or', 'with', 'for', 'on'}
        words = re.findall(r'\b\w+\b', query.lower())
        return [word for word in words if word not in stop_words and len(word) > 2]
    
    def _generate_search_terms(self, niche: List[str], platforms: List[str], geographic_focus: List[str]) -> List[str]:
        """Generate optimized search terms based on extracted components."""
        search_terms = []
        
        # Base terms
        for n in niche:
            search_terms.extend([
                f"{n} influencers 2024",
                f"top {n} creators",
                f"best {n} social media accounts",
                f"{n} thought leaders"
            ])
        
        # Platform-specific terms
        for platform in platforms:
            if platform != 'all':
                for n in niche:
                    search_terms.append(f"best {platform} {n} accounts")
        
        # Geographic terms
        for region in geographic_focus:
            if region != 'global':
                for n in niche:
                    search_terms.append(f"{n} influencers {region}")
        
        return search_terms[:10]  # Limit to top 10 search terms