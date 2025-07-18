"""
Proactive Work-Life Assistant - Streamlit Interface
"""
import streamlit as st
import os
import json
from datetime import datetime, date
from dotenv import load_dotenv
from src.core.assistant import Assistant
from src.utils.formatters import format_success_message, format_error_message

# --- NEW: Log viewer utility ---
def read_log_file(log_path, max_lines=100):
    if not os.path.exists(log_path):
        return ["No log file found."]
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines[-max_lines:]

# Robust .env loading
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "config", ".env"))
if not os.path.exists(env_path):
    raise FileNotFoundError(f".env file not found at {env_path}. Please create it and add your API keys.")
load_dotenv(env_path)

# Page configuration
st.set_page_config(
    page_title="Proactive Work-Life Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for modern styling
st.markdown("""
<style>
    /* Modern gradient background */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Enhanced header styling */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Card-like containers */
    .stApp > div > div > div > div > div > div {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Enhanced message styling */
    .success-message {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2);
    }
    
    .error-message {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 2px solid #dc3545;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(220, 53, 69, 0.2);
    }
    
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border: 2px solid #17a2b8;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(23, 162, 184, 0.2);
    }
    
    /* Quick action buttons */
    .quick-action-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 24px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .quick-action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online { background-color: #28a745; }
    .status-offline { background-color: #dc3545; }
    .status-warning { background-color: #ffc107; }
    
    /* Enhanced sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    
    /* Custom metric styling */
    .metric-container {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'assistant' not in st.session_state:
    st.session_state.assistant = Assistant()
    st.session_state.conversation_history = []
    st.session_state.current_user_email = None
    st.session_state.pending_confirmation = None

# Main header with enhanced styling
st.markdown('<h1 class="main-header">🤖 Proactive Work-Life Assistant</h1>', unsafe_allow_html=True)

# Enhanced sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # User email input with better styling
    user_email = st.text_input(
        "Your Email Address",
        value=st.session_state.current_user_email or "",
        placeholder="your.email@company.com",
        help="This email will be used for sending meeting invites and notifications"
    )
    
    if user_email != st.session_state.current_user_email:
        st.session_state.current_user_email = user_email
        st.success("✅ Email updated!")
    
    st.markdown("---")
    
    # Enhanced assistant status
    st.markdown("### 📊 Assistant Status")
    status = st.session_state.assistant.get_assistant_status()
    
    # Status indicators
    status_color = "🟢" if status['status'] == 'active' else "🔴"
    st.markdown(f"{status_color} **Status:** {status['status'].title()}")
    st.markdown(f"💬 **Conversations:** {status['conversation_count']}")
    
    # Service status with visual indicators
    st.markdown("### 🔧 Services")
    for service, service_status in status['services'].items():
        status_icon = "🟢" if service_status == 'active' else "🔴"
        st.markdown(f"{status_icon} {service.replace('_', ' ').title()}")
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    # Test API connections
    if st.button("🔍 Test All APIs", help="Test all API connections"):
        with st.spinner("Testing APIs..."):
            # Test each service
            test_results = {}
            
            # Test AI Service
            try:
                ai_test = st.session_state.assistant.ai_service.generate_response("Test", "Hello")
                test_results["AI Service"] = "✅ Working"
            except Exception as e:
                test_results["AI Service"] = f"❌ Error: {str(e)[:50]}"
            
            # Test Calendar Service
            try:
                cal_test = st.session_state.assistant.calendar_service.get_events(date.today(), date.today())
                test_results["Calendar Service"] = "✅ Working"
            except Exception as e:
                test_results["Calendar Service"] = f"❌ Error: {str(e)[:50]}"
            
            # Test Restaurant Service
            try:
                rest_test = st.session_state.assistant.restaurant_service.search_restaurants("Hyderabad", "Indian", 5000)
                test_results["Restaurant Service"] = f"✅ Working ({len(rest_test)} results)"
            except Exception as e:
                test_results["Restaurant Service"] = f"❌ Error: {str(e)[:50]}"
            
            # Display results
            for service, result in test_results.items():
                st.markdown(f"**{service}:** {result}")
    
    # Clear conversation
    if st.button("🗑️ Clear History", help="Clear all conversation history"):
        st.session_state.assistant.clear_conversation_history()
        st.session_state.conversation_history = []
        st.success("✅ History cleared!")

    # --- NEW: All API Log Viewers ---
    st.markdown("### 📜 Gemini API Logs")
    gemini_log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "gemini_api.log"))
    gemini_logs = read_log_file(gemini_log_path, max_lines=40)
    st.text_area("Gemini API Log", value=''.join(gemini_logs), height=200, key="gemini_log_viewer")
    st.markdown("### 📜 Calendar Logs")
    calendar_log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "calendar_api.log"))
    calendar_logs = read_log_file(calendar_log_path, max_lines=40)
    st.text_area("Calendar Log", value=''.join(calendar_logs), height=200, key="calendar_log_viewer")
    st.markdown("### 📜 Email Logs")
    email_log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "email_api.log"))
    email_logs = read_log_file(email_log_path, max_lines=40)
    st.text_area("Email Log", value=''.join(email_logs), height=200, key="email_log_viewer")
    st.markdown("### 📜 Restaurant Logs")
    restaurant_log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "restaurant_api.log"))
    restaurant_logs = read_log_file(restaurant_log_path, max_lines=40)
    st.text_area("Restaurant Log", value=''.join(restaurant_logs), height=200, key="restaurant_log_viewer")
    st.markdown("### 📜 Location Logs")
    location_log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "location_api.log"))
    location_logs = read_log_file(location_log_path, max_lines=40)
    st.text_area("Location Log", value=''.join(location_logs), height=200, key="location_log_viewer")
    st.markdown("---")

# Main content area with enhanced layout
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### 💬 Chat Interface")
    
    # Quick action buttons for common queries
    st.markdown("**⚡ Quick Actions:**")
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    
    with col_q1:
        if st.button("📅 Check Availability", help="Check team availability"):
            st.session_state.quick_query = "Check availability for Arnav, Yash, and Priyansh on August 12, 2025"
    
    with col_q2:
        if st.button("🍽️ Find Restaurants", help="Search for restaurants"):
            st.session_state.quick_query = "Find restaurants with Hyderabadi biryani in Hyderabad"
    
    with col_q3:
        if st.button("📧 Send Email", help="Send a test email"):
            st.session_state.quick_query = "Send a hi email to Bhavya"
    
    with col_q4:
        if st.button("🤝 Schedule Meeting", help="Schedule a team meeting"):
            st.session_state.quick_query = "Setup a meeting for Arnav, Yash, and Priyansh on August 10, 2025"
    
    # Chat input with enhanced styling
    user_query = st.text_area(
        "What would you like me to help you with?",
        value=getattr(st.session_state, 'quick_query', ''),
        placeholder="Example: Setup a meeting for Arnav, Yash, and Priyansh on August 10, 2025",
        height=120,
        help="Describe what you need help with. The assistant can schedule meetings, find restaurants, check availability, and more!"
    )
    
    # Clear quick query after use
    if hasattr(st.session_state, 'quick_query'):
        delattr(st.session_state, 'quick_query')

    # --- NEW: Handle session state for multi-step actions ---
    if 'last_result' not in st.session_state:
        st.session_state['last_result'] = None
    if 'selected_time_slot' not in st.session_state:
        st.session_state['selected_time_slot'] = None
    if 'selected_restaurant' not in st.session_state:
        st.session_state['selected_restaurant'] = None
    if 'pending_action_type' not in st.session_state:
        st.session_state['pending_action_type'] = None
    if 'pending_action_details' not in st.session_state:
        st.session_state['pending_action_details'] = None
    # --- END NEW ---

    # Send button with enhanced styling
    col_send1, col_send2, col_send3 = st.columns([1, 1, 1])
    with col_send2:
        send_button = st.button("🚀 Send Request", type="primary", use_container_width=True)
    
    if send_button:
        if user_query.strip():
            with st.spinner("🤖 Processing your request..."):
                result = st.session_state.assistant.process_user_query(
                    user_query, st.session_state.current_user_email
                )
            st.session_state.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user_query': user_query,
                'assistant_response': result
            })
            st.session_state['last_result'] = result  # Persist result for multi-step actions
            st.session_state['selected_time_slot'] = None
            st.session_state['selected_restaurant'] = None
            st.session_state['pending_action_type'] = None
            st.session_state['pending_action_details'] = None
        else:
            st.warning("⚠️ Please enter a query.")

    # --- NEW: Use last_result for multi-step actions ---
    result = st.session_state.get('last_result', None)
    if result:
        if result['success']:
            st.markdown(f'<div class="success-message">✅ {result["message"]}</div>', unsafe_allow_html=True)
            next_action = result.get('next_action')
            if next_action == 'select_time_slot':
                st.markdown("### ⏰ Available Time Slots")
                options = result.get('options', [])
                if options:
                    selected_option = st.radio(
                        "Choose a time slot:",
                        options,
                        format_func=lambda x: f"{x['time']} ({x['duration']} minutes)",
                        key="select_time_slot_radio"
                    )
                    st.session_state['selected_time_slot'] = selected_option
                    if st.button("✅ Confirm Meeting", type="primary", key="confirm_meeting_btn"):
                        meeting_details = result.get('meeting_details', {}).copy()
                        meeting_details.update({
                            'time': selected_option['time'].split(' - ')[0],
                            'attendees': result.get('employee_emails', [])
                        })
                        st.session_state['pending_action_type'] = 'meeting_scheduling'
                        st.session_state['pending_action_details'] = meeting_details
                        # Call confirm_action
                        confirmation_result = st.session_state.assistant.confirm_action(
                            'meeting_scheduling', meeting_details, st.session_state.current_user_email
                        )
                        st.session_state['last_result'] = confirmation_result
                        st.session_state['selected_time_slot'] = None
                        st.session_state['pending_action_type'] = None
                        st.session_state['pending_action_details'] = None
                        st.rerun()
            elif next_action == 'select_restaurant':
                st.markdown("### 🍽️ Restaurant Options")
                options = result.get('options', [])
                if options:
                    for i, restaurant in enumerate(options[:5], 1):
                        with st.expander(f"🍽️ {restaurant['name']} - ⭐ {restaurant['rating']}/5"):
                            col_r1, col_r2 = st.columns(2)
                            with col_r1:
                                st.markdown(f"**📍 Address:** {restaurant['address']}")
                                if restaurant.get('phone'):
                                    st.markdown(f"**📞 Phone:** {restaurant['phone']}")
                                st.markdown(f"**💰 Price:** {'$' * restaurant.get('price_level', 1)}")
                                if restaurant.get('website'):
                                    st.markdown(f"**🌐 Website:** [{restaurant['website']}]({restaurant['website']})")
                            with col_r2:
                                st.markdown(f"**⭐ Rating:** {restaurant['rating']}/5")
                                if restaurant.get('hours'):
                                    st.markdown(f"**🕒 Hours:** {'; '.join(restaurant['hours'][:3])}")
                                st.markdown(f"**📊 Source:** {restaurant['source']}")
                                if restaurant.get('user_ratings_total'):
                                    st.markdown(f"**👥 Reviews:** {restaurant['user_ratings_total']}")
                    selected_option = st.selectbox(
                        "Choose a restaurant:",
                        options,
                        format_func=lambda x: f"{x['name']} - ⭐ {x['rating']}/5",
                        key="select_restaurant_box"
                    )
                    st.session_state['selected_restaurant'] = selected_option
                    if st.button("✅ Confirm Restaurant", type="primary", key="confirm_restaurant_btn"):
                        restaurant_details = result.get('restaurant_details', {}).copy()
                        restaurant_details.update({
                            'name': selected_option['name'],
                            'address': selected_option['address'],
                            'cuisine': selected_option.get('cuisine', 'Various'),
                            'rating': selected_option['rating'],
                            'phone': selected_option.get('phone', 'N/A'),
                            'hours': selected_option.get('hours', []),
                            'website': selected_option.get('website', ''),
                            'source': selected_option['source']
                        })
                        st.session_state['pending_action_type'] = 'restaurant_booking'
                        st.session_state['pending_action_details'] = restaurant_details
                        confirmation_result = st.session_state.assistant.confirm_action(
                            'restaurant_booking', restaurant_details, st.session_state.current_user_email
                        )
                        st.session_state['last_result'] = confirmation_result
                        st.session_state['selected_restaurant'] = None
                        st.session_state['pending_action_type'] = None
                        st.session_state['pending_action_details'] = None
                        st.rerun()
            elif next_action == 'display_schedules':
                st.markdown("### 📅 Team Schedules")
                schedules = result.get('schedules', {})
                if schedules:
                    for email, schedule in schedules.items():
                        with st.expander(f"📅 Schedule for {email}"):
                            if schedule:
                                for event in schedule:
                                    st.markdown(f"• **{event['title']}:** {event['start_time']} - {event['end_time']}")
                            else:
                                st.info("No events scheduled")
                else:
                    st.info("No schedule data available")
            elif next_action == 'complete':
                st.markdown('<div class="success-message">🎉 Task completed successfully!</div>', unsafe_allow_html=True)
        elif result.get('next_action') == 'input_missing_fields':
            st.markdown(f'<div class="error-message">❌ {result["message"]}</div>', unsafe_allow_html=True)
            # Show input boxes for each missing field
            if 'missing_fields' in result:
                if 'missing_fields_inputs' not in st.session_state:
                    st.session_state['missing_fields_inputs'] = {}
                with st.form(key='missing_fields_form'):
                    for field in result['missing_fields']:
                        st.session_state['missing_fields_inputs'][field] = st.text_area(f"Please provide: {field}", value=st.session_state['missing_fields_inputs'].get(field, ''))
                    submit_missing = st.form_submit_button("Submit Missing Info")
                if submit_missing:
                    # Merge missing info into previous details and re-call assistant
                    # You may want to store the last user_query and details in session_state for robustness
                    last_query = st.session_state.conversation_history[-1]['user_query'] if st.session_state.conversation_history else user_query
                    # Compose a new message with the missing info appended
                    filled_info = '\n'.join([f"{k}: {v}" for k, v in st.session_state['missing_fields_inputs'].items()])
                    new_query = f"{last_query}\n{filled_info}"
                    with st.spinner("🤖 Processing your updated info..."):
                        new_result = st.session_state.assistant.process_user_query(
                            new_query, st.session_state.current_user_email
                        )
                    st.session_state.conversation_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'user_query': new_query,
                        'assistant_response': new_result
                    })
                    st.session_state['last_result'] = new_result
                    st.session_state['missing_fields_inputs'] = {}
                    if new_result.get('success'):
                        st.session_state['already_asked_for_missing'] = False
                    st.rerun()
        else:
            st.markdown(f'<div class="error-message">❌ {result["message"]}</div>', unsafe_allow_html=True)
    # --- END NEW ---

with col2:
    st.markdown("### 📝 Recent Conversations")
    
    if st.session_state.conversation_history:
        for i, conv in enumerate(reversed(st.session_state.conversation_history[-5:])):  # Show last 5
            with st.expander(f"💬 {conv['user_query'][:30]}..."):
                st.markdown(f"**👤 User:** {conv['user_query']}")
                st.markdown(f"**🤖 Assistant:** {conv['assistant_response'].get('message', 'No response')}")
                st.caption(f"🕒 {conv['timestamp'][:19]}")
    else:
        st.info("💡 No conversations yet. Try asking something!")

# Enhanced footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <h4>🚀 Proactive Work-Life Assistant v1.0.0</h4>
    <p>Built with ❤️ using Streamlit | Capabilities: Meeting Scheduling • Restaurant Booking • Availability Checking • Email Automation</p>
</div>
""", unsafe_allow_html=True)

# Enhanced example queries
with st.expander("💡 Example Queries & Features"):
    col_ex1, col_ex2 = st.columns(2)
    
    with col_ex1:
        st.markdown("""
        **📅 Meeting Scheduling:**
        - "Setup a meeting for Arnav, Yash, and Priyansh on August 10, 2025"
        - "Schedule a team meeting tomorrow at 2 PM"
        - "Organize a meeting about project planning next Friday"
        
        **🍽️ Restaurant Booking:**
        - "Find restaurants with Hyderabadi biryani in Hyderabad"
        - "Book a restaurant for team lunch in Bangalore"
        - "Find Italian restaurants near our office"
        """)
    
    with col_ex2:
        st.markdown("""
        **📊 Availability Checking:**
        - "Check availability for John and Sarah on Monday"
        - "When is the team free next week?"
        - "Find common free time for Arnav, Yash, and Priyansh"
        
        **📧 Email Automation:**
        - "Send a hi email to Bhavya"
        - "Send meeting invites to the team"
        - "Send restaurant booking confirmation"
        """)

# Run the app
if __name__ == "__main__":
    # This will be handled by Streamlit
    pass 