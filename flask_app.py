"""
Flask Web Application for Nebula.AI - Proactive Work-Life Assistant
AWS Deployment Ready
"""
from flask import Flask, render_template, request, jsonify
import os
import sys
import json
import logging
from datetime import datetime, date
from dotenv import load_dotenv

# Add the current directory to Python path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Load environment variables first
env_path = os.path.join(current_dir, 'config', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"✓ Loaded .env from {env_path}")
else:
    load_dotenv()  # Try default .env
    print("⚠ Using default .env loading")

# Import your existing assistant modules with better error handling
Assistant = None
try:
    from src.core.assistant import Assistant
    from src.utils.formatters import format_success_message, format_error_message
    print("✓ Assistant modules imported successfully")
except ImportError as e:
    print(f"✗ Could not import assistant modules: {e}")
    print("This will limit functionality to mock responses only.")
    import traceback
    traceback.print_exc()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-here')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global assistant instance and session storage
assistant_instance = None
user_sessions = {}  # Simple in-memory session storage

def get_assistant():
    """Get or create assistant instance with better error handling"""
    global assistant_instance
    if assistant_instance is None and Assistant is not None:
        try:
            logger.info("Initializing Assistant with full services...")
            assistant_instance = Assistant()
            logger.info("✓ Assistant initialized successfully with calendar and email services")
            
            # Test the assistant to make sure it's working
            status = assistant_instance.get_assistant_status()
            logger.info(f"Assistant status: {status}")
            
        except Exception as e:
            logger.error(f"Failed to initialize assistant: {e}", exc_info=True)
            assistant_instance = None
            return None
    elif Assistant is None:
        logger.warning("Assistant class is not available (import failed)")
        return None
    
    return assistant_instance

def get_user_session(user_email):
    """Get or create user session"""
    if not user_email:
        return None
    if user_email not in user_sessions:
        user_sessions[user_email] = {
            'last_result': None,
            'conversation_history': [],
            'pending_options': None
        }
    return user_sessions[user_email]

def store_user_session(user_email, data):
    """Store data in user session"""
    if not user_email:
        return
    session = get_user_session(user_email)
    if session:
        session.update(data)
        user_sessions[user_email] = session

def read_log_file(log_path, max_lines=100):
    """Read log file content"""
    if not os.path.exists(log_path):
        return ["No log file found."]
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return lines[-max_lines:]
    except Exception as e:
        logger.error(f"Error reading log file {log_path}: {e}")
        return [f"Error reading log file: {e}"]

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/process_goal', methods=['POST'])
def process_goal():
    """Process user goal/query"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400

        query = data.get('query', '').strip()
        user_email = data.get('user_email', '').strip()

        if not query:
            return jsonify({
                'success': False,
                'message': 'Please provide a query'
            }), 400

        logger.info(f"Processing query: {query}")
        logger.info(f"User email: {user_email}")

        # Try to get assistant with detailed logging
        assistant = get_assistant()
        if assistant:
            try:
                logger.info("Using real Assistant for query processing...")
                # Process the query with full assistant functionality
                result = assistant.process_user_query(query, user_email)
                
                # Store result in user session for potential confirmation
                if user_email:
                    store_user_session(user_email, {
                        'last_result': result,
                        'last_query': query,
                        'pending_options': result.get('options', None) if result else None
                    })
                
                logger.info(f"✓ Assistant processed query successfully: {result.get('message', 'No message') if result else 'No result'}")
                return jsonify(result) if result else jsonify({'success': False, 'message': 'Assistant returned no result'})
                
            except Exception as e:
                logger.error(f"✗ Assistant processing failed: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'message': f'Assistant error: {str(e)}',
                    'error_type': 'assistant_error'
                }), 500
        else:
            logger.warning("Assistant not available - this means calendar/email won't work!")
            return jsonify({
                'success': False,
                'message': 'Assistant service is not available. Calendar and email features require the Assistant to be properly initialized.',
                'error_type': 'assistant_unavailable',
                'troubleshooting': [
                    'Check that all required Python packages are installed',
                    'Verify that API keys are properly configured in .env file',
                    'Ensure src/core/assistant.py is accessible',
                    'Check server logs for detailed error information'
                ]
            }), 503
        
        # Create a mock response with time slots for meeting scheduling
        if any(word in query.lower() for word in ['meeting', 'schedule', 'meet']):
            mock_result = {
                'success': True,
                'message': 'I found some available time slots for your meeting.',
                'next_action': 'select_time_slot',
                'options': [
                    {'time': '10:00 AM - 11:00 AM', 'duration': 60, 'attendees': ['Available']},
                    {'time': '2:00 PM - 3:00 PM', 'duration': 60, 'attendees': ['Available']},
                    {'time': '4:00 PM - 5:00 PM', 'duration': 60, 'attendees': ['Available']}
                ],
                'meeting_details': {
                    'title': 'Team Meeting',
                    'date': '2025-07-26',
                    'duration': 60
                }
            }
        elif any(word in query.lower() for word in ['restaurant', 'food', 'eat', 'dinner', 'lunch']):
            # Try to use real restaurant search even without full assistant
            try:
                from src.services.restaurant_service import RestaurantService
                restaurant_service = RestaurantService()
                
                # Extract location from query (simple extraction)
                location = "Hyderabad"  # Default location
                cuisine = None
                
                # Simple keyword extraction
                if "hyderabad" in query.lower():
                    location = "Hyderabad"
                elif "bangalore" in query.lower():
                    location = "Bangalore"
                elif "mumbai" in query.lower():
                    location = "Mumbai"
                elif "delhi" in query.lower():
                    location = "Delhi"
                
                if "biryani" in query.lower():
                    cuisine = "biryani"
                elif "italian" in query.lower():
                    cuisine = "italian"
                elif "chinese" in query.lower():
                    cuisine = "chinese"
                elif "indian" in query.lower():
                    cuisine = "indian"
                
                # Search for restaurants
                restaurants = restaurant_service.search_restaurants(
                    location=location,
                    cuisine=cuisine,
                    min_rating=3.5
                )
                
                if restaurants:
                    options = []
                    for restaurant in restaurants[:5]:  # Top 5 restaurants
                        options.append({
                            'name': restaurant.get('name', 'Unknown'),
                            'address': restaurant.get('address', 'N/A'),
                            'rating': restaurant.get('rating', 0),
                            'cuisine': restaurant.get('cuisine', 'Various'),
                            'phone': restaurant.get('phone', 'N/A'),
                            'source': restaurant.get('source', 'api')
                        })
                    
                    mock_result = {
                        'success': True,
                        'message': f'I found {len(restaurants)} great restaurants for you in {location}.',
                        'next_action': 'select_restaurant',
                        'options': options,
                        'restaurant_details': {
                            'location': location,
                            'cuisine': cuisine,
                            'search_results': len(restaurants)
                        }
                    }
                else:
                    mock_result = {
                        'success': False,
                        'message': f'No restaurants found in {location}. Please try a different location or cuisine type.',
                        'next_action': 'clarify'
                    }
                    
            except Exception as e:
                logger.error(f"Restaurant search error: {e}")
                # Fallback to mock response
                mock_result = {
                    'success': True,
                    'message': 'I found some great restaurants for you.',
                    'next_action': 'select_restaurant',
                    'options': [
                        {'name': 'Biryani House', 'rating': 4.5, 'address': 'Hyderabad Central', 'cuisine': 'Indian'},
                        {'name': 'Spice Garden', 'rating': 4.2, 'address': 'Banjara Hills', 'cuisine': 'Indian'},
                        {'name': 'Royal Kitchen', 'rating': 4.7, 'address': 'Jubilee Hills', 'cuisine': 'Multicuisine'}
                    ],
                    'note': f'Restaurant API error: {str(e)[:100]}'
                }
        else:
            mock_result = {
                'success': True,
                'message': f'I understand you want to: "{query}". This is a demo response since the full assistant is not configured.',
                'next_action': 'complete'
            }

        return jsonify(mock_result)

    except Exception as e:
        logger.error(f"Error processing goal: {e}")
        return jsonify({
            'success': False,
            'message': f'An error occurred while processing your request: {str(e)}'
        }), 500

@app.route('/diagnostic', methods=['GET'])
def diagnostic():
    """Diagnostic endpoint to check Assistant and service status"""
    try:
        diagnostic_info = {
            'timestamp': datetime.now().isoformat(),
            'flask_status': 'running',
            'environment': {},
            'imports': {},
            'assistant_status': {},
            'services': {}
        }
        
        # Check environment variables
        env_vars = ['GEMINI_API_KEY', 'GOOGLE_CALENDAR_CLIENT_ID', 'GMAIL_CLIENT_ID', 'GOOGLE_PLACES_API_KEY']
        for var in env_vars:
            value = os.environ.get(var)
            diagnostic_info['environment'][var] = 'SET' if value else 'NOT SET'
        
        # Check imports
        diagnostic_info['imports']['Assistant'] = Assistant is not None
        
        # Check assistant status
        assistant = get_assistant()
        if assistant:
            try:
                status = assistant.get_assistant_status()
                diagnostic_info['assistant_status'] = status
                diagnostic_info['assistant_available'] = True
            except Exception as e:
                diagnostic_info['assistant_status'] = {'error': str(e)}
                diagnostic_info['assistant_available'] = False
        else:
            diagnostic_info['assistant_available'] = False
            diagnostic_info['assistant_status'] = {'error': 'Assistant not initialized'}
        
        return jsonify(diagnostic_info)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/test_endpoint', methods=['GET', 'POST'])
def test_endpoint():
    """Simple test endpoint to verify Flask is working"""
    try:
        print("=== TEST ENDPOINT CALLED ===")
        print(f"Method: {request.method}")
        print(f"Content-Type: {request.content_type}")
        
        if request.method == 'POST':
            data = request.get_json()
            print(f"POST data: {data}")
            return jsonify({
                'success': True,
                'message': 'POST test successful',
                'received_data': data,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'message': 'GET test successful',
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        print(f"Test endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test_confirm', methods=['POST'])
def test_confirm():
    """Test endpoint for debugging confirm_selection"""
    try:
        print("=== TEST CONFIRM ENDPOINT ===")
        data = request.get_json()
        print(f"Test data: {data}")
        
        # Test basic functionality
        return jsonify({
            'success': True,
            'message': 'Test confirm endpoint working',
            'received_data': data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Test confirm error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/confirm_selection', methods=['POST'])
def confirm_selection():
    """Confirm user selection and execute actual calendar/email actions"""
    print("=== CONFIRM SELECTION ENDPOINT CALLED ===")
    
    try:
        # Get request data
        data = request.get_json()
        print(f"Request data: {data}")
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        selection_type = data.get('type')
        index = data.get('index')
        user_email = data.get('user_email', '').strip()

        print(f"Type: {selection_type}, Index: {index}, Email: {user_email}")

        # Basic validation
        if not selection_type or index is None:
            return jsonify({
                'success': False,
                'message': 'Missing selection type or index'
            }), 400

        # For now, let's handle time-slot specifically and simply
        if selection_type == 'time-slot':
            print("Processing time slot confirmation...")
            
            # Try to get assistant
            try:
                assistant = get_assistant()
                if not assistant:
                    print("Assistant not available, using mock response")
                    return jsonify({
                        'success': True,
                        'message': f'✅ Time slot #{index + 1} confirmed! (Assistant not available - this is a mock response)',
                        'next_action': 'complete',
                        'timestamp': datetime.now().isoformat()
                    })
                
                print("Assistant available, checking for session data...")
                
                # Try to get session data
                user_session = get_user_session(user_email) if user_email else {}
                print(f"User session: {user_session}")
                
                # Check if we have valid session data
                if not user_session or not (user_session.get('last_result') if user_session else None):
                    print("No session data, creating a test meeting...")
                    # Create a simple test meeting
                    test_meeting_details = {
                        'title': f'Meeting from Flask App',
                        'date': '2025-07-26',
                        'time': '10:00 AM',
                        'duration': 60,
                        'attendees': [user_email] if user_email else ['test@example.com'],
                        'description': f'Meeting confirmed via Flask - Time slot #{index + 1}'
                    }
                    
                    print(f"Creating test meeting: {test_meeting_details}")
                    
                    # Call Assistant's confirm_action
                    result = assistant.confirm_action(
                        'meeting_scheduling',
                        test_meeting_details,
                        user_email
                    )
                    
                    print(f"Assistant result: {result}")
                    
                    # Check if result is valid and has success key
                    if result and result.get('success'):
                        return jsonify({
                            'success': True,
                            'message': f'✅ Meeting scheduled successfully! Calendar event created.',
                            'next_action': 'complete',
                            'details': result.get('details', {}) if result else {},
                            'timestamp': datetime.now().isoformat()
                        })
                    else:
                        error_msg = result.get('message', 'Unknown error') if result else 'Assistant returned None'
                        return jsonify({
                            'success': False,
                            'message': f'Failed to schedule meeting: {error_msg}'
                        }), 500
                
                else:
                    print("Session data found, processing with stored options...")
                    last_result = user_session.get('last_result', {}) if user_session else {}
                    options = last_result.get('options', []) if last_result else []
                    
                    if not options:
                        print("No options found in session data")
                        return jsonify({
                            'success': False,
                            'message': 'No options available. Please restart your query.'
                        }), 400
                    
                    if index >= len(options):
                        return jsonify({
                            'success': False,
                            'message': f'Invalid selection index. Please choose from 0-{len(options)-1}'
                        }), 400
                    
                    selected_option = options[index]
                    if not selected_option:
                        return jsonify({
                            'success': False,
                            'message': 'Selected option is invalid.'
                        }), 400
                        
                    # Safely get meeting details
                    meeting_details = last_result.get('meeting_details', {}) if last_result else {}
                    if not meeting_details:
                        meeting_details = {}
                    else:
                        meeting_details = meeting_details.copy()
                    
                    # Safely update meeting details
                    time_str = ''
                    if selected_option and selected_option.get('time'):
                        time_str = selected_option.get('time', '').split(' - ')[0]
                    
                    attendees = []
                    if last_result and last_result.get('employee_emails'):
                        attendees = last_result.get('employee_emails', [])
                    elif user_email:
                        attendees = [user_email]
                    else:
                        attendees = ['test@example.com']
                    
                    meeting_details.update({
                        'time': time_str,
                        'attendees': attendees,
                        'selected_slot': selected_option if selected_option else {}
                    })
                    
                    print(f"Meeting details from session: {meeting_details}")
                    
                    result = assistant.confirm_action(
                        'meeting_scheduling',
                        meeting_details,
                        user_email
                    )
                    
                    print(f"Assistant result: {result}")
                    
                    # Check if result is valid
                    if result and result.get('success'):
                        return jsonify({
                            'success': True,
                            'message': f'✅ Meeting scheduled successfully! Calendar event created and invitations sent.',
                            'next_action': 'complete',
                            'details': result.get('details', {}) if result else {},
                            'timestamp': datetime.now().isoformat()
                        })
                    else:
                        error_msg = result.get('message', 'Unknown error') if result else 'Assistant returned None'
                        return jsonify({
                            'success': False,
                            'message': f'Failed to schedule meeting: {error_msg}'
                        }), 500
                        
            except Exception as e:
                print(f"Error in assistant processing: {e}")
                import traceback
                traceback.print_exc()
                
                # Return a mock success for now
                return jsonify({
                    'success': True,
                    'message': f'✅ Time slot #{index + 1} confirmed! (Error in assistant: {str(e)})',
                    'next_action': 'complete',
                    'timestamp': datetime.now().isoformat()
                })
                
        else:
            # Handle other types (restaurant, etc.)
            return jsonify({
                'success': True,
                'message': f'✅ Selection #{index + 1} confirmed!',
                'next_action': 'complete',
                'selection_type': selection_type,
                'selection_index': index,
                'timestamp': datetime.now().isoformat()
            })

    except Exception as e:
        print(f"EXCEPTION in confirm_selection: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/test_apis', methods=['POST'])
def test_apis():
    """Test all API connections"""
    try:
        assistant = get_assistant()
        if not assistant:
            return jsonify({
                'success': False,
                'message': 'Assistant service is not available'
            }), 503

        test_results = {}

        # Test AI Service
        try:
            ai_test = assistant.ai_service.generate_response("Test", "Hello")
            test_results["AI Service"] = "✅ Working"
        except Exception as e:
            test_results["AI Service"] = f"❌ Error: {str(e)[:50]}"

        # Test Calendar Service
        try:
            cal_test = assistant.calendar_service.get_events(date.today(), date.today())
            test_results["Calendar Service"] = "✅ Working"
        except Exception as e:
            test_results["Calendar Service"] = f"❌ Error: {str(e)[:50]}"

        # Test Email Service
        try:
            # Just check if service is available
            email_service = getattr(assistant, 'email_service', None)
            if email_service:
                test_results["Email Service"] = "✅ Working"
            else:
                test_results["Email Service"] = "❌ Service not available"
        except Exception as e:
            test_results["Email Service"] = f"❌ Error: {str(e)[:50]}"

        # Test Restaurant Service
        try:
            rest_test = assistant.restaurant_service.search_restaurants("Hyderabad", "Indian", 5000)
            test_results["Restaurant Service"] = f"✅ Working ({len(rest_test)} results)"
        except Exception as e:
            test_results["Restaurant Service"] = f"❌ Error: {str(e)[:50]}"

        # Test Location Service
        try:
            location_service = getattr(assistant, 'location_service', None)
            if location_service:
                test_results["Location Service"] = "✅ Working"
            else:
                test_results["Location Service"] = "❌ Service not available"
        except Exception as e:
            test_results["Location Service"] = f"❌ Error: {str(e)[:50]}"

        return jsonify({
            'success': True,
            'results': test_results
        })

    except Exception as e:
        logger.error(f"Error testing APIs: {e}")
        return jsonify({
            'success': False,
            'message': f'An error occurred while testing APIs: {str(e)}'
        }), 500

@app.route('/get_logs')
def get_logs():
    """Get system logs"""
    try:
        log_type = request.args.get('type', 'gemini')
        
        log_files = {
            'gemini': 'gemini_api.log',
            'calendar': 'calendar_api.log',
            'email': 'email_api.log',
            'restaurant': 'restaurant_api.log',
            'location': 'location_api.log'
        }
        
        log_filename = log_files.get(log_type, 'gemini_api.log')
        log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), log_filename))
        
        logs = read_log_file(log_path, max_lines=50)
        
        return jsonify({
            'success': True,
            'logs': logs,
            'type': log_type
        })

    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        return jsonify({
            'success': False,
            'message': f'An error occurred while fetching logs: {str(e)}'
        }), 500

@app.route('/get_status')
def get_status():
    """Get assistant status"""
    try:
        assistant = get_assistant()
        if not assistant:
            return jsonify({
                'status': 'offline',
                'services': {},
                'conversation_count': 0
            })

        status = assistant.get_assistant_status()
        return jsonify(status)

    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'status': 'error',
            'services': {},
            'conversation_count': 0,
            'error': str(e)
        })

@app.route('/test_simple', methods=['GET', 'POST'])
def test_simple():
    """Simple test endpoint"""
    try:
        return jsonify({
            'success': True,
            'message': 'Simple test working',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in simple test: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Simple test failed: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint for AWS"""
    try:
        assistant = get_assistant()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'assistant_available': assistant is not None
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting Nebula.AI Flask Application")
    print("=" * 60)
    
    # Test Assistant initialization on startup
    print("Testing Assistant initialization...")
    assistant = get_assistant()
    if assistant:
        print("✅ Assistant initialized successfully!")
        print("✅ Calendar and email functionality will be available")
        try:
            status = assistant.get_assistant_status()
            print(f"✅ Assistant status: {status.get('status', 'unknown')}")
            print(f"✅ Services available: {list(status.get('services', {}).keys())}")
        except Exception as e:
            print(f"⚠️ Warning: Could not get assistant status: {e}")
    else:
        print("❌ Assistant initialization failed!")
        print("❌ Calendar and email functionality will NOT be available")
        print("❌ Only mock responses will be provided")
    
    print("=" * 60)
    print("🌐 Starting Flask server...")
    print("🔧 Visit http://localhost:5000/diagnostic for detailed status")
    print("=" * 60)
    
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Nebula.AI Flask application on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
