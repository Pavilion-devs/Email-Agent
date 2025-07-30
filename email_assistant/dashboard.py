"""Streamlit Dashboard for Smart Email Assistant Demo."""

import streamlit as st
import pandas as pd
from datetime import datetime
import json
from .controller import EmailAssistantController
from .email_fetcher import EmailFetcher

def run_dashboard():
    """Run the Streamlit dashboard."""
    st.set_page_config(
        page_title="Smart Email Assistant",
        page_icon="📧",
        layout="wide"
    )
    
    st.title("🤖 Smart Email Assistant Dashboard")
    st.markdown("*AI-powered email categorization, response generation, and meeting scheduling*")
    
    # Initialize session state
    if 'controller' not in st.session_state:
        try:
            st.session_state.controller = EmailAssistantController()
            st.session_state.emails_processed = False
            st.session_state.results = []
        except Exception as e:
            st.error(f"Failed to initialize Email Assistant: {str(e)}")
            st.info("Make sure you have set up your Gmail API credentials and OpenAI API key.")
            return
    
    # Sidebar controls
    st.sidebar.header("Controls")
    
    if st.sidebar.button("🔄 Fetch & Process Emails", type="primary"):
        with st.spinner("Fetching and processing emails..."):
            try:
                emails = st.session_state.controller._fetch_emails()
                if emails:
                    st.session_state.results = st.session_state.controller._process_emails(emails)
                    st.session_state.emails_processed = True
                    st.success(f"Processed {len(st.session_state.results)} emails!")
                else:
                    st.warning("No emails found to process.")
            except Exception as e:
                st.error(f"Error processing emails: {str(e)}")
    
    # Configuration
    st.sidebar.header("Configuration")
    max_emails = st.sidebar.slider("Max emails to process", 5, 100, 50)
    show_details = st.sidebar.checkbox("Show detailed results", True)
    
    # Main dashboard
    if st.session_state.emails_processed and st.session_state.results:
        display_dashboard(st.session_state.results, show_details)
    else:
        display_welcome()

def display_welcome():
    """Display welcome screen."""
    st.markdown("""
    ## Welcome to Smart Email Assistant! 🎉
    
    This AI-powered assistant can:
    - 📂 **Categorize emails** into Important, Newsletters, Promotions, Meetings, and Personal
    - ✍️ **Generate responses** for emails that need replies
    - 📅 **Detect meeting requests** and suggest available times
    - 🏷️ **Auto-label** emails in Gmail
    
    ### Getting Started
    1. Make sure you have your Gmail API credentials set up
    2. Set your OpenAI API key in the environment
    3. Click "Fetch & Process Emails" in the sidebar
    
    ### Demo Features
    - Real-time email processing
    - AI categorization with confidence scoring
    - Auto-generated responses preview
    - Meeting detection and scheduling
    """)
    
    st.info("Click 'Fetch & Process Emails' in the sidebar to get started!")

def display_dashboard(results, show_details=True):
    """Display the main dashboard with results."""
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Emails", len(results))
    
    with col2:
        meeting_count = sum(1 for r in results if r.get('is_meeting_request'))
        st.metric("Meeting Requests", meeting_count)
    
    with col3:
        response_count = sum(1 for r in results if r.get('should_respond'))
        st.metric("Need Responses", response_count)
    
    with col4:
        unread_count = sum(1 for r in results if r.get('is_unread'))
        st.metric("Unread", unread_count)
    
    # Category distribution
    st.subheader("📊 Email Categories")
    
    categories = {}
    for result in results:
        category = result.get('ai_category', 'Unknown')
        categories[category] = categories.get(category, 0) + 1
    
    if categories:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            category_df = pd.DataFrame(list(categories.items()), columns=['Category', 'Count'])
            st.dataframe(category_df, use_container_width=True)
        
        with col2:
            st.bar_chart(category_df.set_index('Category'))
    
    # Email details
    if show_details:
        st.subheader("📧 Email Details")
        
        # Filter controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category_filter = st.selectbox(
                "Filter by category:",
                ["All"] + list(categories.keys())
            )
        
        with col2:
            meeting_filter = st.selectbox(
                "Filter by type:",
                ["All", "Meeting Requests", "Regular Emails"]
            )
        
        with col3:
            response_filter = st.selectbox(
                "Filter by response:",
                ["All", "Needs Response", "No Response Needed"]
            )
        
        # Apply filters
        filtered_results = apply_filters(results, category_filter, meeting_filter, response_filter)
        
        # Display filtered results
        for i, result in enumerate(filtered_results):
            display_email_card(result, i)

def apply_filters(results, category_filter, meeting_filter, response_filter):
    """Apply filters to email results."""
    filtered = results
    
    if category_filter != "All":
        filtered = [r for r in filtered if r.get('ai_category') == category_filter]
    
    if meeting_filter == "Meeting Requests":
        filtered = [r for r in filtered if r.get('is_meeting_request')]
    elif meeting_filter == "Regular Emails":
        filtered = [r for r in filtered if not r.get('is_meeting_request')]
    
    if response_filter == "Needs Response":
        filtered = [r for r in filtered if r.get('should_respond')]
    elif response_filter == "No Response Needed":
        filtered = [r for r in filtered if not r.get('should_respond')]
    
    return filtered

def display_email_card(result, index):
    """Display individual email card."""
    with st.expander(f"📧 {result.get('subject', 'No Subject')[:60]}..."):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**From:** {result.get('sender', 'Unknown')}")
            st.write(f"**Date:** {result.get('date', 'Unknown')}")
            st.write(f"**Category:** {result.get('ai_category', 'Unknown')}")
            st.write(f"**Snippet:** {result.get('snippet', 'No preview available')}")
        
        with col2:
            # Status indicators
            if result.get('is_meeting_request'):
                st.success("📅 Meeting Request")
            
            if result.get('should_respond'):
                st.info("✍️ Needs Response")
            
            if result.get('is_unread'):
                st.warning("🔴 Unread")
        
        # Meeting details
        if result.get('is_meeting_request') and result.get('meeting_details'):
            st.subheader("📅 Meeting Details")
            details = result['meeting_details']
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Type:** {details.get('meeting_type', 'Unknown')}")
                st.write(f"**Duration:** {details.get('duration', 60)} minutes")
            
            with col2:
                st.write(f"**Purpose:** {details.get('purpose', 'Not specified')}")
                st.write(f"**Urgency:** {details.get('urgency', 'Medium')}")
            
            # Suggested times
            if result.get('suggested_times'):
                st.write("**Suggested Times:**")
                for time in result['suggested_times'][:3]:
                    st.write(f"• {time['formatted_start']} to {time['formatted_end']}")
        
        # Generated response
        if result.get('generated_response'):
            st.subheader("✍️ Generated Response")
            response = result['generated_response']
            
            st.text_area(
                "Response:",
                value=response,
                height=150,
                key=f"response_{index}",
                help="This response was generated by AI. Review before sending."
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Approve & Send", key=f"approve_{index}"):
                    st.success("Response approved! (Demo mode - not actually sent)")
            
            with col2:
                if st.button(f"✏️ Edit Response", key=f"edit_{index}"):
                    st.info("Edit mode activated! (Feature coming soon)")

def display_analytics():
    """Display analytics and insights."""
    st.subheader("📈 Analytics & Insights")
    
    # This could include:
    # - Processing time metrics
    # - Categorization accuracy
    # - Response generation success rate
    # - Meeting scheduling efficiency
    
    st.info("Analytics features coming soon!")

if __name__ == "__main__":
    run_dashboard()