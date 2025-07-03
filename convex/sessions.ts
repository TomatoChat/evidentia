import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Create a new user session
export const createSession = mutation({
  args: {
    session_id: v.string(),
    email: v.string(),
  },
  handler: async (ctx, args) => {
    const now = Date.now();
    
    // Check if session already exists
    const existingSession = await ctx.db
      .query("sessions")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .first();
    
    if (existingSession) {
      // Update existing session
      await ctx.db.patch(existingSession._id, {
        email: args.email,
        last_active: now,
      });
      return existingSession._id;
    }
    
    // Create new session
    return await ctx.db.insert("sessions", {
      session_id: args.session_id,
      email: args.email,
      created_at: now,
      last_active: now,
    });
  },
});

// Get session by session_id
export const getSession = query({
  args: { session_id: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("sessions")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .first();
  },
});

// Update session last_active timestamp
export const updateSessionActivity = mutation({
  args: { session_id: v.string() },
  handler: async (ctx, args) => {
    const session = await ctx.db
      .query("sessions")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .first();
    
    if (!session) {
      throw new Error("Session not found");
    }
    
    await ctx.db.patch(session._id, {
      last_active: Date.now(),
    });
    
    return session._id;
  },
});

// Delete a session (cleanup)
export const deleteSession = mutation({
  args: { session_id: v.string() },
  handler: async (ctx, args) => {
    const session = await ctx.db
      .query("sessions")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .first();
    
    if (session) {
      await ctx.db.delete(session._id);
    }
    
    return true;
  },
});

// Get comprehensive session data with all associated records
export const getSessionData = query({
  args: { session_id: v.string() },
  handler: async (ctx, args) => {
    // Get session info
    const session = await ctx.db
      .query("sessions")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .first();
    
    // Get brand analyses
    const brandAnalyses = await ctx.db
      .query("brand_analyses")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .collect();
    
    // Get GEO analyses
    const geoAnalyses = await ctx.db
      .query("geo_analyses")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .collect();
    
    // Get reports
    const reports = await ctx.db
      .query("reports")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .collect();
    
    return {
      session,
      brandAnalyses,
      geoAnalyses,
      reports,
      totalRecords: brandAnalyses.length + geoAnalyses.length + reports.length,
      hasData: brandAnalyses.length > 0 || geoAnalyses.length > 0 || reports.length > 0,
    };
  },
});