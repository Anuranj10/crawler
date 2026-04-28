import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict

# Gmail Configuration
GMAIL_USER = "anuranjsmanoj61@gmail.com"
GMAIL_APP_PASSWORD = "wase atwf pifa opkf"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send email using Gmail SMTP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = GMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def send_login_email(user_name: str, user_email: str):
    """Send welcome email on login"""
    subject = "Welcome Back to EduroApp!"
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #4CAF50;">Welcome Back, {user_name}!</h2>
            <p>You have successfully logged into EduroApp.</p>
            <p>Login Time: {get_current_time()}</p>
            <p>Start exploring scholarships tailored for you!</p>
            <hr>
            <p style="color: #666; font-size: 12px;">This is an automated message from EduroApp Scholarship Platform.</p>
        </body>
    </html>
    """
    return send_email(user_email, subject, html_content)

def send_scholarship_results_email(user_name: str, user_email: str, matches: List[Dict]):
    """Send scholarship results via email"""
    subject = f"Your Scholarship Matches - {len(matches)} Found!"
    
    # Build scholarship list HTML
    scholarships_html = ""
    for idx, match in enumerate(matches, 1):
        score = min(int(match.get('score', 0)), 100)
        title = match.get('title', 'N/A')
        description = match.get('description_snippet', 'No description available')[:200]
        url = match.get('url', '#')
        
        scholarships_html += f"""
        <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
            <h3 style="color: #2196F3; margin: 0;">
                <span style="background: #4CAF50; color: white; padding: 3px 8px; border-radius: 3px; font-size: 14px;">
                    {score}% Match
                </span>
                {title}
            </h3>
            <p style="color: #555; margin: 10px 0;">{description}...</p>
            <a href="{url}" style="color: #2196F3; text-decoration: none;">View Details & Apply →</a>
        </div>
        """
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px;">
                <h2 style="color: #4CAF50;">Hello {user_name}!</h2>
                <p>We found <strong>{len(matches)} scholarship(s)</strong> matching your profile!</p>
                <p style="color: #666;">Generated on: {get_current_time()}</p>
                <hr style="border: 1px solid #eee;">
                {scholarships_html}
                <hr style="border: 1px solid #eee; margin-top: 20px;">
                <p style="color: #666; font-size: 12px;">
                    This email was sent from EduroApp Scholarship Recommendation Platform.<br>
                    Keep exploring and apply to scholarships that match your profile!
                </p>
            </div>
        </body>
    </html>
    """
    return send_email(user_email, subject, html_content)

def get_current_time():
    """Get current formatted time"""
    from datetime import datetime
    return datetime.now().strftime("%B %d, %Y at %I:%M %p")
