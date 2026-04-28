"""
Test script for email functionality
Run this to verify email sending works
"""
import sys
sys.path.append('.')

from src.email_service import send_login_email, send_scholarship_results_email

# Test login email
print("Testing login email...")
result = send_login_email("Test User", "anuranjsmanoj61@gmail.com")
print(f"Login email sent: {result}")

# Test scholarship results email
print("\nTesting scholarship results email...")
sample_matches = [
    {
        "title": "Merit Scholarship for Engineering Students",
        "score": 95,
        "description_snippet": "This scholarship is for engineering students with excellent academic records",
        "url": "https://example.com/scholarship1"
    },
    {
        "title": "Need-Based Financial Aid",
        "score": 88,
        "description_snippet": "Financial assistance for students from low-income families",
        "url": "https://example.com/scholarship2"
    }
]
result = send_scholarship_results_email("Test User", "anuranjsmanoj61@gmail.com", sample_matches)
print(f"Scholarship results email sent: {result}")

print("\nCheck your inbox at anuranjsmanoj61@gmail.com!")
