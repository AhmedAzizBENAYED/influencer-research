"""
Streamlit-compatible adapter for the influencer research workflow.
This provides better integration with Streamlit's session state and real-time updates.
"""

import streamlit as st
import threading
import queue
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from variables.workflow.research_workflow import InfluencerResearchWorkflow
from src.config.settings import settings


class StreamlitWorkflowAdapter:
    """
    Adapter class that makes the research workflow work better with Streamlit.
    Provides progress tracking, cancellation, and real-time updates.
    """
    
    def __init__(self):
        self.workflow = None
        self.is_running = False
        self.progress_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.cancel_event = threading.Event()
        
    def initialize_workflow(self) -> bool:
        """Initialize the workflow with error handling."""
        try:
            if self.workflow is None:
                self.workflow = InfluencerResearchWorkflow()
            return True
        except Exception as e:
            st.error(f"Failed to initialize workflow: {e}")
            return False
    
    def run_research_async(self, query: str, progress_callback: Optional[Callable] = None) -> Dict:
        """
        Run research in a separate thread with progress updates.
        
        Args:
            query: The research query
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with research results and metadata
        """
        if not self.initialize_workflow():
            return {"status": "error", "message": "Failed to initialize workflow"}
        
        self.is_running = True
        self.cancel_event.clear()
        
        def research_thread():
            """Background thread for running research."""
            try:
                # Send progress updates
                self.progress_queue.put({"phase": "initializing", "progress": 0.1, "message": "Initializing agents..."})
                
                if self.cancel_event.is_set():
                    return
                
                self.progress_queue.put({"phase": "analyzing", "progress": 0.2, "message": "Analyzing query..."})
                time.sleep(0.5)  # Brief pause for UI updates
                
                if self.cancel_event.is_set():
                    return
                
                self.progress_queue.put({"phase": "searching", "progress": 0.4, "message": "Searching for influencers..."})
                
                # Run the actual research
                start_time = time.time()
                result = self.workflow.run_research(query)
                duration = time.time() - start_time
                
                if self.cancel_event.is_set():
                    return
                
                self.progress_queue.put({"phase": "finalizing", "progress": 0.9, "message": "Finalizing report..."})
                
                # Prepare final result
                final_result = {
                    "status": "completed" if result and result != "No results generated" else "failed",
                    "query": query,
                    "result": result,
                    "duration": duration,
                    "timestamp": datetime.now().isoformat(),
                    "word_count": len(result.split()) if result else 0,
                    "char_count": len(result) if result else 0
                }
                
                self.progress_queue.put({"phase": "complete", "progress": 1.0, "message": "Research completed!"})
                self.result_queue.put(final_result)
                
            except Exception as e:
                error_result = {
                    "status": "error",
                    "query": query,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                self.result_queue.put(error_result)
            finally:
                self.is_running = False
        
        # Start research in background thread
        thread = threading.Thread(target=research_thread, daemon=True)
        thread.start()
        
        return {"status": "started", "message": "Research started in background"}
    
    def get_progress_update(self) -> Optional[Dict]:
        """Get the latest progress update if available."""
        try:
            return self.progress_queue.get_nowait()
        except queue.Empty:
            return None
    
    def get_result(self) -> Optional[Dict]:
        """Get the research result if available."""
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None
    
    def cancel_research(self):
        """Cancel the ongoing research."""
        self.cancel_event.set()
        self.is_running = False
    
    def is_research_running(self) -> bool:
        """Check if research is currently running."""
        return self.is_running


class StreamlitProgressTracker:
    """Helper class for managing Streamlit progress indicators."""
    
    def __init__(self):
        self.progress_bar = None
        self.status_text = None
        self.time_text = None
        self.start_time = None
        
    def initialize_display(self):
        """Initialize the progress display elements."""
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        self.time_text = st.empty()
        self.start_time = time.time()
        
    def update_progress(self, progress_data: Dict):
        """Update the progress display."""
        if not self.progress_bar:
            return
            
        progress = progress_data.get("progress", 0)
        message = progress_data.get("message", "Processing...")
        phase = progress_data.get("phase", "unknown")
        
        # Update progress bar
        self.progress_bar.progress(progress)
        
        # Update status message with styling
        if phase == "complete":
            self.status_text.markdown(
                f'<div class="status-complete">✅ {message}</div>', 
                unsafe_allow_html=True
            )
        elif phase == "error":
            self.status_text.markdown(
                f'<div class="status-error">❌ {message}</div>', 
                unsafe_allow_html=True
            )
        else:
            self.status_text.markdown(
                f'<div class="status-running">🔄 {message}</div>', 
                unsafe_allow_html=True
            )
        
        # Update elapsed time
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.time_text.text(f"⏱️ Elapsed: {elapsed:.1f}s")
    
    def cleanup(self):
        """Clean up the progress display."""
        if self.progress_bar:
            self.progress_bar.empty()
        if self.status_text:
            self.status_text.empty()
        if self.time_text:
            self.time_text.empty()


def create_research_interface():
    """
    Create an enhanced research interface with real-time progress tracking.
    This function can be called from your main Streamlit app.
    """
    
    # Initialize adapter in session state
    if 'workflow_adapter' not in st.session_state:
        st.session_state.workflow_adapter = StreamlitWorkflowAdapter()
    
    if 'progress_tracker' not in st.session_state:
        st.session_state.progress_tracker = StreamlitProgressTracker()
    
    adapter = st.session_state.workflow_adapter
    tracker = st.session_state.progress_tracker
    
    # Query input
    query = st.text_area(
        "Enter your research query:",
        placeholder="Find AI and machine learning influencers with 50K+ followers",
        height=100
    )
    
    # Control buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        start_button = st.button(
            "🚀 Start Research", 
            type="primary", 
            disabled=adapter.is_research_running() or len(query.strip()) < 10
        )
    
    with col2:
        if adapter.is_research_running():
            if st.button("🛑 Cancel", type="secondary"):
                adapter.cancel_research()
                st.rerun()
    
    with col3:
        if st.button("🔄 Reset"):
            # Clear session state
            for key in ['current_result', 'research_complete']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Handle research start
    if start_button and query.strip():
        result = adapter.run_research_async(query.strip())
        if result["status"] == "started":
            st.session_state.research_started = True
            tracker.initialize_display()
            st.rerun()
    
    # Handle ongoing research
    if adapter.is_research_running():
        # Check for progress updates
        progress_update = adapter.get_progress_update()
        if progress_update:
            tracker.update_progress(progress_update)
        
        # Check for completion
        result = adapter.get_result()
        if result:
            st.session_state.current_result = result
            st.session_state.research_complete = True
            tracker.cleanup()
            st.rerun()
        else:
            # Auto-refresh while research is running
            time.sleep(1)
            st.rerun()
    
    # Display results
    if st.session_state.get('research_complete') and st.session_state.get('current_result'):
        result = st.session_state.current_result
        
        st.markdown("---")
        st.header("📊 Research Results")
        
        if result["status"] == "completed":
            # Success metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("⏱️ Duration", f"{result['duration']:.1f}s")
            with col2:
                st.metric("📝 Words", f"{result['word_count']:,}")
            with col3:
                st.metric("📄 Characters", f"{result['char_count']:,}")
            with col4:
                st.metric("✅ Status", "Complete")
            
            # Display the actual result
            st.subheader("Research Report")
            st.markdown(result["result"])
            
            # Download options
            st.subheader("📥 Download Options")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    "📄 Download Markdown",
                    data=result["result"],
                    file_name=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
            
            with col2:
                import json
                json_data = json.dumps(result, indent=2)
                st.download_button(
                    "📊 Download JSON",
                    data=json_data,
                    file_name=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col3:
                st.info(f"📁 Also saved to: {settings.OUTPUT_DIR}")
                
        elif result["status"] == "error":
            st.error(f"❌ Research failed: {result.get('error', 'Unknown error')}")
        
        else:
            st.warning("⚠️ Research completed but no results were generated")


# Example usage function
def demo_streamlit_research():
    """
    Demo function showing how to integrate the research interface.
    Call this from your main streamlit app.
    """
    st.title("🎯 AI Influencer Research Assistant")
    st.markdown("---")
    
    # Add custom CSS
    st.markdown("""
    <style>
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
    </style>
    """, unsafe_allow_html=True)
    
    # Create the research interface
    create_research_interface()


if __name__ == "__main__":
    # Run the demo
    demo_streamlit_research()