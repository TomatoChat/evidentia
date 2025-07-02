# Evidentia Database Migration to Convex

This document outlines the complete migration of Evidentia from in-memory session storage to a Convex-powered database system.

## Overview

Evidentia has been successfully migrated from an in-memory session management system to a robust Convex database solution that provides:
- Real-time data synchronization
- TypeScript type safety
- Automatic scaling
- ACID transactions
- Schema validation

## Database Schema

### Tables

#### 1. Sessions (`sessions`)
Stores user session information for brand research workflows.

```typescript
{
  session_id: string,        // Unique session identifier
  email: string,             // User's email address
  created_at: number,        // Creation timestamp
  last_active: number,       // Last activity timestamp
}
```

**Indexes:**
- `by_session_id` - Primary lookup by session ID
- `by_email` - Find sessions by email address

#### 2. Brand Analyses (`brand_analyses`)
Stores complete brand analysis results and metadata.

```typescript
{
  session_id: string,              // Reference to user session
  brand_name: string,              // Analyzed brand name
  brand_website?: string,          // Brand website URL
  brand_country?: string,          // Target country for analysis
  brand_description?: string,      // AI-generated brand description
  brand_industry?: string,         // Identified industry
  competitors?: string[],          // List of discovered competitors
  analysis_timestamp: number,     // When analysis was completed
  status: "pending" | "completed" | "failed",
  result_data?: any,              // Complete analysis result object
}
```

**Indexes:**
- `by_session_id` - Find analyses by session
- `by_status` - Query by completion status
- `by_timestamp` - Sort by analysis time

#### 3. GEO Analyses (`geo_analyses`)
Stores Geographic Engine Optimization analysis data.

```typescript
{
  session_id: string,                    // Reference to user session
  brand_name: string,                    // Brand being analyzed
  search_queries: string[],              // List of test search queries
  competitors?: string[],                // Competitor brands
  llm_models?: string[],                 // LLM models used for analysis
  optimization_suggestions?: string,     // AI-generated optimization advice
  progress_status: number,               // Progress percentage (0-100)
  analysis_result?: any,                 // Complete GEO analysis data
  completed_at?: number,                 // Completion timestamp
  status: "pending" | "in_progress" | "completed" | "failed",
}
```

**Indexes:**
- `by_session_id` - Find analyses by session
- `by_status` - Query by completion status
- `by_progress` - Find analyses by progress level

#### 4. Reports (`reports`)
Stores generated reports and email delivery status.

```typescript
{
  session_id: string,                           // Reference to user session
  report_type: "brand_analysis" | "geo_analysis" | "combined",
  report_data: any,                             // Complete report data
  email_sent: boolean,                          // Email delivery status
  recipient_email: string,                      // Report recipient
  generated_at: number,                         // Report generation time
  brand_name?: string,                          // Associated brand name
}
```

**Indexes:**
- `by_session_id` - Find reports by session
- `by_email` - Find reports by recipient
- `by_type` - Query by report type
- `by_timestamp` - Sort by generation time

## Migration Changes

### Backend Changes

#### 1. New Files Added
- `backend/libs/convex_client.py` - Python wrapper for Convex operations
- `convex/schema.ts` - Database schema definition
- `convex/sessions.ts` - Session management functions
- `convex/brandAnalysis.ts` - Brand analysis data functions
- `convex/geoAnalysis.ts` - GEO analysis data functions
- `convex/reports.ts` - Report management functions

#### 2. Modified Files
- `backend/server.py` - Updated to use Convex for data persistence
- `backend/requirements.txt` - Added Convex Python client
- `.env.template` - Added CONVEX_URL configuration

#### 3. Backend Integration Points

**Session Management:**
- `collect_email` endpoint now creates sessions in Convex
- Fallback to in-memory storage if Convex unavailable
- Session cleanup after report delivery

**Brand Analysis:**
- `stream_brand_info` endpoint saves results to Convex
- Analysis results stored with complete metadata
- Progress tracking and status updates

**Report Generation:**
- `send_report` endpoint saves report history
- Email delivery status tracking
- Session cleanup after successful delivery

### Frontend Changes

#### 1. New Files Added
- `frontend/lib/convex.ts` - Convex client configuration
- `frontend/providers/ConvexProvider.tsx` - React context provider

#### 2. Modified Files
- `frontend/app/layout.tsx` - Added ConvexProvider wrapper
- `frontend/package.json` - Added Convex React client

#### 3. Frontend Integration
- ConvexProvider wraps the entire application
- Real-time data synchronization capabilities
- Environment-based configuration

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Convex Database
CONVEX_URL="https://your-convex-deployment.convex.cloud"

# Frontend (for Next.js)
NEXT_PUBLIC_CONVEX_URL="https://your-convex-deployment.convex.cloud"
```

### Convex Setup

1. **Install Convex CLI:**
   ```bash
   npm install -g convex
   ```

2. **Project Configuration:**
   - `convex.json` - Project configuration
   - Generated API files in `convex/_generated/`

3. **Deployment:**
   ```bash
   npx convex dev    # Development
   npx convex deploy # Production
   ```

## Benefits of Migration

### 1. Data Persistence
- User sessions survive server restarts
- Analysis results are permanently stored
- Report history is maintained

### 2. Real-time Capabilities
- Live progress updates during analysis
- Real-time collaboration potential
- Automatic UI updates when data changes

### 3. Scalability
- Automatic scaling with user growth
- No manual database management
- Built-in performance optimization

### 4. Data Integrity
- ACID transactions ensure consistency
- Schema validation prevents data corruption
- Type safety reduces runtime errors

### 5. Analytics & Insights
- Query historical analysis data
- Track user engagement patterns
- Monitor system performance metrics

## Backward Compatibility

The migration maintains full backward compatibility:
- Fallback to in-memory storage if Convex fails
- Existing API endpoints unchanged
- Frontend interface remains the same
- Error handling preserves user experience

## Future Enhancements

With Convex integration, future features become possible:
- User accounts and authentication
- Analysis history and comparisons
- Real-time collaborative analysis
- Advanced analytics and reporting
- Multi-user brand monitoring
- API rate limiting and usage tracking

## Files Cleaned Up

During migration, the following unnecessary files were removed:
- Python cache directories (`__pycache__`)
- Yarn error logs
- Temporary build artifacts

## Testing

To verify the migration:

1. **Environment Setup:**
   ```bash
   # Set CONVEX_URL in your .env file
   # Run: npx convex dev
   ```

2. **Backend Testing:**
   ```bash
   cd backend
   python server.py
   # Check console for "✅ Convex client initialized successfully"
   ```

3. **Feature Testing:**
   - Email collection creates sessions in Convex
   - Brand analysis saves results with metadata
   - Reports are stored with delivery status
   - Session cleanup works properly

4. **Fallback Testing:**
   - Remove CONVEX_URL temporarily
   - Verify fallback to in-memory storage
   - Restore CONVEX_URL and test normal operation

This migration positions Evidentia for future growth while maintaining current functionality and user experience.