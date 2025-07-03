import smtplib
import ssl
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import json
from datetime import datetime
from typing import Dict, Any, Optional
from .pdf_generator import generate_pdf_report, create_pdf_filename


def send_report_email(
    recipient_email: str,
    brand_name: str,
    analysis_result: Dict[Any, Any],
    sender_email: Optional[str] = None,
    sender_password: Optional[str] = None,
    smtp_server: Optional[str] = None,
    smtp_port: int = 587
) -> bool:
    """
    Send the analysis report via email to the user.
    
    Args:
        recipient_email (str): Email address to send the report to
        brand_name (str): Name of the analyzed brand
        analysis_result (dict): The complete analysis result
        sender_email (str, optional): SMTP email address. Defaults to env var SMTP_EMAIL
        sender_password (str, optional): SMTP password. Defaults to env var SMTP_PASSWORD
        smtp_server (str, optional): SMTP server. Defaults to env var SMTP_SERVER
        smtp_port (int): SMTP port. Defaults to 587
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    
    # Get SMTP credentials from environment variables or parameters
    sender_email = sender_email or os.getenv("SMTP_EMAIL")
    sender_password = sender_password or os.getenv("SMTP_PASSWORD")
    smtp_server = smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
    
    if not sender_email or not sender_password:
        print("ERROR: SMTP credentials not provided. Set SMTP_EMAIL and SMTP_PASSWORD environment variables.")
        return False
    
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = f"Your AI Search Analysis Report for {brand_name}"
        message["From"] = sender_email
        message["To"] = recipient_email
        
        # Create HTML email content
        html_content = generate_report_html(brand_name, analysis_result)
        
        # Create plain text version
        text_content = generate_report_text(brand_name, analysis_result)
        
        # Add parts to message
        text_part = MIMEText(text_content, "plain")
        html_part = MIMEText(html_content, "html")
        
        message.attach(text_part)
        message.attach(html_part)
        
        # Add PDF attachment
        pdf_content = generate_pdf_report(brand_name, analysis_result)
        pdf_filename = create_pdf_filename(brand_name)
        pdf_attachment = MIMEApplication(pdf_content, _subtype='pdf')
        pdf_attachment.add_header(
            'Content-Disposition', 
            'attachment', 
            filename=pdf_filename
        )
        message.attach(pdf_attachment)
        
        # Create secure connection and send email
        context = ssl.create_default_context()
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        
        print(f"✅ Report successfully sent to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return False


def generate_report_html(brand_name: str, analysis_result: Dict[Any, Any]) -> str:
    """Generate HTML email content for the report."""
    
    queries_count = len(analysis_result.get('queries', []))
    competitors_count = len(analysis_result.get('analysis', {}).get('competitors_analyzed', []))
    suggestions_count = len(analysis_result.get('analysis', {}).get('optimization_suggestions', []))
    
    # Get first 5 suggestions for preview
    suggestions = analysis_result.get('analysis', {}).get('optimization_suggestions', [])[:5]
    suggestions_html = ""
    for i, suggestion in enumerate(suggestions, 1):
        suggestions_html += f"<li style='margin: 8px 0; color: #374151;'>{suggestion}</li>"
    
    # Add additional suggestions note if there are more than 5
    additional_html = ""
    if suggestions_count > 5:
        additional_html = f"<p style='color: #6b7280; font-style: italic; margin-top: 15px;'>+ {suggestions_count - 5} more recommendations in the full report</p>"
    
    # Format datetime outside f-string
    report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Search Report for {brand_name}</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    
    <div style="background: linear-gradient(135deg, #0CF2A0, #00D4AA); padding: 30px; border-radius: 12px; text-align: center; margin-bottom: 30px;">
        <h1 style="color: black; margin: 0; font-size: 28px; font-weight: bold;">🎯 AI Search Analysis Report</h1>
        <p style="color: black; margin: 10px 0 0 0; font-size: 18px; opacity: 0.8;">for {brand_name}</p>
    </div>
    
    <div style="background: #f9fafb; padding: 25px; border-radius: 8px; margin-bottom: 25px;">
        <h2 style="color: #111827; margin-top: 0;">📊 Executive Summary</h2>
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 20px 0;">
            <div style="text-align: center; padding: 15px; background: white; border-radius: 8px; border: 1px solid #e5e7eb;">
                <div style="font-size: 24px; font-weight: bold; color: #0CF2A0;">{queries_count}</div>
                <div style="font-size: 12px; color: #6b7280; margin-top: 5px;">Queries Tested</div>
            </div>
            <div style="text-align: center; padding: 15px; background: white; border-radius: 8px; border: 1px solid #e5e7eb;">
                <div style="font-size: 24px; font-weight: bold; color: #0CF2A0;">{competitors_count}</div>
                <div style="font-size: 12px; color: #6b7280; margin-top: 5px;">Competitors Analyzed</div>
            </div>
            <div style="text-align: center; padding: 15px; background: white; border-radius: 8px; border: 1px solid #e5e7eb;">
                <div style="font-size: 24px; font-weight: bold; color: #0CF2A0;">{suggestions_count}</div>
                <div style="font-size: 12px; color: #6b7280; margin-top: 5px;">Recommendations</div>
            </div>
        </div>
    </div>
    
    <div style="background: white; padding: 25px; border-radius: 8px; border: 1px solid #e5e7eb; margin-bottom: 25px;">
        <h2 style="color: #111827; margin-top: 0;">🚀 Key Recommendations</h2>
        <ol style="padding-left: 20px; margin: 15px 0;">
            {suggestions_html}
        </ol>
        {additional_html}
    </div>
    
    <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
        <h3 style="color: #111827; margin-top: 0;">📎 Attachments</h3>
        <p style="margin: 10px 0; color: #374151;">• Professional PDF report with complete analysis</p>
        <p style="margin: 10px 0; color: #374151;">• Query-by-query breakdown and insights</p>
        <p style="margin: 10px 0; color: #374151;">• Competitor comparison data</p>
        <p style="margin: 10px 0; color: #374151;">• Executive summary and recommendations</p>
    </div>
    
    <div style="background: #111827; color: white; padding: 20px; border-radius: 8px; text-align: center;">
        <h3 style="margin-top: 0; color: #0CF2A0;">Generated by Evidentia</h3>
        <p style="margin: 10px 0; opacity: 0.8;">AI-powered brand analysis for the generative search era</p>
        <p style="margin: 10px 0; font-size: 12px; opacity: 0.6;">Report generated on {report_date}</p>
    </div>
    
</body>
</html>"""
    
    return html


def generate_report_text(brand_name: str, analysis_result: Dict[Any, Any]) -> str:
    """Generate plain text email content for the report."""
    
    queries_count = len(analysis_result.get('queries', []))
    competitors_count = len(analysis_result.get('analysis', {}).get('competitors_analyzed', []))
    suggestions_count = len(analysis_result.get('analysis', {}).get('optimization_suggestions', []))
    
    # Get first 5 suggestions for preview
    suggestions = analysis_result.get('analysis', {}).get('optimization_suggestions', [])[:5]
    suggestions_text = ""
    for i, suggestion in enumerate(suggestions, 1):
        suggestions_text += f"{i}. {suggestion}\n"
    
    # Add additional suggestions note if there are more than 5
    additional_note = ""
    if suggestions_count > 5:
        additional_note = f"+ {suggestions_count - 5} more recommendations in the full report\n"
    
    # Format datetime outside f-string
    report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    text = f"""🎯 AI SEARCH ANALYSIS REPORT FOR {brand_name.upper()}

📊 EXECUTIVE SUMMARY
===================
• Queries Tested: {queries_count}
• Competitors Analyzed: {competitors_count}  
• Recommendations: {suggestions_count}

🚀 KEY RECOMMENDATIONS
=====================
{suggestions_text}{additional_note}

📎 ATTACHMENTS
=============
• Professional PDF report with complete analysis
• Query-by-query breakdown and insights  
• Competitor comparison data
• Executive summary and recommendations

---
Generated by Evidentia - AI-powered brand analysis
Report generated on {report_date}"""
    
    return text