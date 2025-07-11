from flask import Flask, render_template, request, session as flask_session, redirect, url_for, jsonify
from flask_cors import CORS
import os
import requests
from collections import defaultdict
from form_fetcher import fetch_form_data_sync
from logger_setup import logger
import schedule
import time
import threading
from datetime import datetime
from submit_proof import run_batch_requests_for_user


app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'

# Per-user session store
user_sessions = defaultdict(requests.Session)





# Schedule it daily at 06:50:50



user_headers = defaultdict(dict)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    return 'OK', 200
    """Health check endpoint"""
    deployment_info = {
        'status': 'healthy',
        'service': 'KPCL OTP Automation',
        'version': '1.0.0',
        'environment': os.environ.get('AWS_LAMBDA_FUNCTION_NAME', 'local'),
        'deployment': 'AWS Lambda' if os.environ.get('AWS_LAMBDA_FUNCTION_NAME') else 'Local',
        'region': os.environ.get('AWS_REGION', 'N/A'),
        'features': [
            'Dynamic form fetching',
            'User-specific overrides', 
            'Scheduled execution at 6:59:59 AM',
            'Multi-user support',
            'GitHub Pages integration',
            'AWS Lambda deployment'
        ],
        'schedule': {
            'login_window': '6:45-6:55 AM IST',
            'execution_time': '6:59:59.99 AM IST',
            'timezone': 'Asia/Kolkata'
        }
    }
    
    # Add Lambda-specific info if running on AWS
    if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        deployment_info.update({
            'lambda_function': os.environ.get('AWS_LAMBDA_FUNCTION_NAME'),
            'lambda_version': os.environ.get('AWS_LAMBDA_FUNCTION_VERSION'),
            'lambda_memory': os.environ.get('AWS_LAMBDA_FUNCTION_MEMORY_SIZE'),
            'request_id': getattr(flask_session, 'request_id', None)
        })
    
    return jsonify(deployment_info)

@app.route('/generate-otp', methods=['POST'])
def generate_otp():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')  # Receive password but not using it for OTP generation
    if not username:
        return jsonify({'success': False, 'error': 'Username required'}), 400

    session = user_sessions[username]
    session.cookies.set('PHPSESSID', str(int(time.time()))+'s')  # Set a dummy session ID or manage it dynamically
    try:
        # First visit the signin page to establish session
        session.get('https://kpcl-ams.com/signin_page.php', timeout=10)
        
        # Send OTP request
        otp_url = 'https://kpcl-ams.com/send_otp.php'
        payload = {'user_id': username}
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://kpcl-ams.com/signin_page.php',
            'Origin': 'https://kpcl-ams.com',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01'
        }
        otp_resp = session.post(otp_url, data=payload, headers=headers, timeout=10)

        if otp_resp.ok and 'success' in otp_resp.text.lower():
            print("📅 Scheduler running. Waiting for 06:50:50 every day...")


            return jsonify({'success': True, 'message': 'OTP sent to your registered mobile number'})
        return jsonify({'success': False, 'error': 'Failed to send OTP. Please check your username.'}), 400
    except Exception as e:
        logger.error(f"Error in generate_otp: {str(e)}")
        return jsonify({'success': False, 'error': f'Network error: {str(e)}'}), 500

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    logger.info("Received OTP verification request")
    data = request.get_json()
    username = data.get('username')
    otp = data.get('otp')
    password = data.get('password')
    if not all([username, otp, password]):
        return jsonify({'success': False, 'error': 'Missing credentials'}), 400

    session = user_sessions[username]
    try:
        verify_resp = session.post('https://kpcl-ams.com/verify_otp.php', data={'otp': otp, 'username': username}, timeout=10)

        if 'OTP Verified' in verify_resp.text or 'success' in verify_resp.text.lower():
            signin_payload = {
                'username': username,
                'password': password,
                'otp_code': otp,
                'submit': 'Sign In'
            }
            logger.info(f"Signing in user {username} with OTP {otp}")
            signin_resp = session.post('https://kpcl-ams.com/signin_page.php', data=signin_payload, timeout=10)
            if 'dashboard' in signin_resp.text.lower() or 'logout' in signin_resp.text.lower():
                logger.info(f"Login successful for user {username} with otp {otp}")

                run_batch_requests_for_user(session)
                return jsonify({'success': True, 'message': 'Login successful'})
                
            logger.error(f"Login failed for user {username} after OTP verification")
            return jsonify({'success': False, 'error': 'Login failed after OTP verification'}), 401
        return jsonify({'success': False, 'error': 'Invalid or expired OTP'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/submit-gatepass', methods=['POST'])
def submit_gatepass():
    data = request.get_json() if request.is_json else request.form.to_dict()
    username = data.get('username')
    if not username:
        return jsonify({'success': False, 'error': 'Username required'}), 400

    session = user_sessions[username]
    try:
        gatepass_url = 'https://kpcl-ams.com/user/proof_uploade_code.php'
        
        # Only set the Referer header as default, everything else fetched dynamically
        headers = {
            'Referer': 'https://kpcl-ams.com/user/gatepass.php'
        }
        
        # Get current session cookies
        session_cookies = dict(session.cookies)
        
        # Prepare user overrides from form data (excluding username)
        user_overrides = {k: v for k, v in data.items() if k != 'username'}
        
        # Fetch form data dynamically from the website and merge with user input
        form_data = fetch_form_data_sync(session_cookies, user_overrides)
        
        if not form_data:
            return jsonify({'success': False, 'error': 'Failed to fetch form data from website'}), 500
        
        resp = session.post(gatepass_url, data=form_data, headers=headers, timeout=15)
        return jsonify({'success': True, 'status_code': resp.status_code, 'response': resp.text})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/gatepass')
def gatepass():
    return render_template('gatepass.html')

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)
