"""
Convex client wrapper for Evidentia backend
"""
import os
from convex import ConvexClient
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime

class ConvexClientWrapper:
    def __init__(self):
        """Initialize Convex client with deployment URL from environment"""
        convex_url = os.getenv('CONVEX_URL')
        if not convex_url:
            raise ValueError("CONVEX_URL environment variable is required")
        
        self.client = ConvexClient(convex_url)
    
    # Session management
    def create_session(self, email: str) -> str:
        """Create a new session and return session_id"""
        session_id = str(uuid.uuid4())
        self.client.mutation("sessions:createSession", {
            "session_id": session_id,
            "email": email
        })
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by session_id"""
        return self.client.query("sessions:getSession", {
            "session_id": session_id
        })
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        return self.client.mutation("sessions:deleteSession", {
            "session_id": session_id
        })
    
    def update_session_activity(self, session_id: str):
        """Update session last_active timestamp"""
        return self.client.mutation("sessions:updateSessionActivity", {
            "session_id": session_id
        })
    
    # Brand Analysis
    def save_brand_analysis(self, 
                          session_id: str,
                          brand_name: str,
                          brand_website: Optional[str] = None,
                          brand_country: Optional[str] = None,
                          brand_description: Optional[str] = None,
                          brand_industry: Optional[str] = None,
                          competitors: Optional[List[str]] = None,
                          status: str = "pending",
                          result_data: Optional[Any] = None) -> str:
        """Save brand analysis results"""
        return self.client.mutation("brandAnalysis:saveBrandAnalysis", {
            "session_id": session_id,
            "brand_name": brand_name,
            "brand_website": brand_website,
            "brand_country": brand_country,
            "brand_description": brand_description,
            "brand_industry": brand_industry,
            "competitors": competitors,
            "status": status,
            "result_data": result_data
        })
    
    def get_brand_analysis(self, session_id: str) -> Optional[Dict]:
        """Get brand analysis by session_id"""
        return self.client.query("brandAnalysis:getBrandAnalysis", {
            "session_id": session_id
        })
    
    def update_brand_analysis_status(self, 
                                   session_id: str, 
                                   status: str, 
                                   result_data: Optional[Any] = None):
        """Update brand analysis status"""
        return self.client.mutation("brandAnalysis:updateBrandAnalysisStatus", {
            "session_id": session_id,
            "status": status,
            "result_data": result_data
        })
    
    # GEO Analysis
    def save_geo_analysis(self,
                         session_id: str,
                         brand_name: str,
                         search_queries: List[str],
                         competitors: Optional[List[str]] = None,
                         llm_models: Optional[List[str]] = None,
                         optimization_suggestions: Optional[str] = None,
                         progress_status: int = 0,
                         analysis_result: Optional[Any] = None,
                         status: str = "pending") -> str:
        """Save GEO analysis results"""
        return self.client.mutation("geoAnalysis:saveGeoAnalysis", {
            "session_id": session_id,
            "brand_name": brand_name,
            "search_queries": search_queries,
            "competitors": competitors,
            "llm_models": llm_models,
            "optimization_suggestions": optimization_suggestions,
            "progress_status": progress_status,
            "analysis_result": analysis_result,
            "status": status
        })
    
    def get_geo_analysis(self, session_id: str) -> Optional[Dict]:
        """Get GEO analysis by session_id"""
        return self.client.query("geoAnalysis:getGeoAnalysis", {
            "session_id": session_id
        })
    
    def update_geo_analysis_progress(self,
                                   session_id: str,
                                   progress_status: int,
                                   status: Optional[str] = None,
                                   analysis_result: Optional[Any] = None,
                                   optimization_suggestions: Optional[str] = None):
        """Update GEO analysis progress"""
        return self.client.mutation("geoAnalysis:updateGeoAnalysisProgress", {
            "session_id": session_id,
            "progress_status": progress_status,
            "status": status,
            "analysis_result": analysis_result,
            "optimization_suggestions": optimization_suggestions
        })
    
    # Reports
    def save_report(self,
                   session_id: str,
                   report_type: str,
                   report_data: Any,
                   email_sent: bool,
                   recipient_email: str,
                   brand_name: Optional[str] = None) -> str:
        """Save report history"""
        return self.client.mutation("reports:saveReport", {
            "session_id": session_id,
            "report_type": report_type,
            "report_data": report_data,
            "email_sent": email_sent,
            "recipient_email": recipient_email,
            "brand_name": brand_name
        })
    
    def get_reports_by_session(self, session_id: str) -> List[Dict]:
        """Get reports by session_id"""
        return self.client.query("reports:getReportsBySession", {
            "session_id": session_id
        })
    
    def update_report_email_status(self, report_id: str, email_sent: bool):
        """Update report email status"""
        return self.client.mutation("reports:updateReportEmailStatus", {
            "report_id": report_id,
            "email_sent": email_sent
        })

# Global instance to be used throughout the application
convex_client = None

def get_convex_client() -> ConvexClientWrapper:
    """Get singleton Convex client instance"""
    global convex_client
    if convex_client is None:
        convex_client = ConvexClientWrapper()
    return convex_client