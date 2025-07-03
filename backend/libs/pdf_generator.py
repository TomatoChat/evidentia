import io
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


def generate_pdf_report(brand_name: str, analysis_result: Dict[Any, Any]) -> bytes:
    """
    Generate a professional PDF report from analysis results.
    
    Args:
        brand_name (str): Name of the analyzed brand
        analysis_result (dict): The complete analysis result
    
    Returns:
        bytes: PDF file content as bytes
    """
    
    # Create a BytesIO buffer to store the PDF
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=HexColor('#111827'),
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        textColor=HexColor('#0CF2A0'),
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=15,
        spaceBefore=20,
        textColor=HexColor('#111827'),
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    # Build the story (content)
    story = []
    
    # Title page
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("🎯 AI Search Analysis Report", title_style))
    story.append(Paragraph(f"for {brand_name}", subtitle_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Report date
    report_date = datetime.now().strftime("%B %d, %Y")
    story.append(Paragraph(f"Generated on {report_date}", normal_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Executive Summary
    story.append(Paragraph("📊 Executive Summary", heading_style))
    
    # Summary stats
    queries_count = len(analysis_result.get('queries', []))
    competitors_count = len(analysis_result.get('analysis', {}).get('competitors_analyzed', []))
    suggestions_count = len(analysis_result.get('analysis', {}).get('optimization_suggestions', []))
    
    # Summary table
    summary_data = [
        ['Metric', 'Count'],
        ['Queries Tested', str(queries_count)],
        ['Competitors Analyzed', str(competitors_count)],
        ['Recommendations Generated', str(suggestions_count)]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0CF2A0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f9fafb')),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#e5e7eb'))
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Key Recommendations
    story.append(Paragraph("🚀 Key Recommendations", heading_style))
    
    suggestions = analysis_result.get('analysis', {}).get('optimization_suggestions', [])
    if suggestions:
        for i, suggestion in enumerate(suggestions[:10], 1):  # Limit to top 10
            story.append(Paragraph(f"{i}. {suggestion}", normal_style))
        
        if len(suggestions) > 10:
            story.append(Paragraph(f"<i>+ {len(suggestions) - 10} additional recommendations available in detailed analysis</i>", normal_style))
    else:
        story.append(Paragraph("No specific recommendations available in the analysis data.", normal_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Queries Analysis
    if queries_count > 0:
        story.append(Paragraph("🔍 Query Analysis", heading_style))
        
        queries = analysis_result.get('queries', [])
        for i, query in enumerate(queries[:5], 1):  # Show first 5 queries
            if isinstance(query, str):
                story.append(Paragraph(f"<b>Query {i}:</b> {query}", normal_style))
            elif isinstance(query, dict):
                query_text = query.get('query', query.get('text', 'Unknown query'))
                story.append(Paragraph(f"<b>Query {i}:</b> {query_text}", normal_style))
        
        if queries_count > 5:
            story.append(Paragraph(f"<i>+ {queries_count - 5} additional queries analyzed</i>", normal_style))
        
        story.append(Spacer(1, 0.3*inch))
    
    # Competitors Analysis
    competitors = analysis_result.get('analysis', {}).get('competitors_analyzed', [])
    if competitors:
        story.append(Paragraph("🏢 Competitor Analysis", heading_style))
        
        for competitor in competitors[:5]:  # Show first 5 competitors
            if isinstance(competitor, str):
                story.append(Paragraph(f"• {competitor}", normal_style))
            elif isinstance(competitor, dict):
                comp_name = competitor.get('name', competitor.get('brand', 'Unknown competitor'))
                story.append(Paragraph(f"• {comp_name}", normal_style))
        
        if len(competitors) > 5:
            story.append(Paragraph(f"<i>+ {len(competitors) - 5} additional competitors analyzed</i>", normal_style))
        
        story.append(Spacer(1, 0.3*inch))
    
    # Analysis Details
    analysis_data = analysis_result.get('analysis', {})
    if analysis_data:
        story.append(Paragraph("📈 Detailed Analysis", heading_style))
        
        # Brand visibility
        if 'brand_visibility' in analysis_data:
            visibility = analysis_data['brand_visibility']
            story.append(Paragraph(f"<b>Brand Visibility:</b> {visibility}", normal_style))
        
        # Performance metrics
        if 'performance_metrics' in analysis_data:
            metrics = analysis_data['performance_metrics']
            if isinstance(metrics, dict):
                for metric, value in metrics.items():
                    story.append(Paragraph(f"<b>{metric.replace('_', ' ').title()}:</b> {value}", normal_style))
        
        story.append(Spacer(1, 0.3*inch))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e5e7eb')))
    story.append(Spacer(1, 0.2*inch))
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=HexColor('#6b7280')
    )
    
    story.append(Paragraph("Generated by <b>Evidentia</b> - AI-powered brand analysis for the generative search era", footer_style))
    story.append(Paragraph(f"Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", footer_style))
    
    # Build the PDF
    doc.build(story)
    
    # Get the PDF content
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content


def create_pdf_filename(brand_name: str) -> str:
    """
    Create a clean filename for the PDF report.
    
    Args:
        brand_name (str): Name of the brand
    
    Returns:
        str: Clean filename for the PDF
    """
    clean_name = brand_name.lower().replace(" ", "_").replace("-", "_")
    # Remove any non-alphanumeric characters except underscores
    clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
    return f"{clean_name}_ai_search_report.pdf" 