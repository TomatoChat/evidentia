import { mutation, query } from "./_generated/server";
import { getAuthUserId } from "@convex-dev/auth/server";
import { v } from "convex/values";

// Get current authenticated user
export const getCurrentUser = query({
  args: {},
  handler: async (ctx) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) {
      return null;
    }
    
    return await ctx.db.get(userId);
  },
});

// Get user by ID
export const getUser = query({
  args: { userId: v.id("users") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.userId);
  },
});

// Update user profile
export const updateUserProfile = mutation({
  args: {
    name: v.optional(v.string()),
    subscription_status: v.optional(v.union(v.literal("free"), v.literal("pro"), v.literal("enterprise"))),
  },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) {
      throw new Error("Not authenticated");
    }

    await ctx.db.patch(userId, {
      ...args,
      last_active: Date.now(),
    });

    return await ctx.db.get(userId);
  },
});

// Increment analysis count for user
export const incrementAnalysisCount = mutation({
  args: {},
  handler: async (ctx) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) {
      throw new Error("Not authenticated");
    }

    const user = await ctx.db.get(userId);
    if (!user) {
      throw new Error("User not found");
    }

    await ctx.db.patch(userId, {
      analysis_count: (user.analysis_count || 0) + 1,
      last_active: Date.now(),
    });

    return user.analysis_count || 0 + 1;
  },
});

// Get user's analysis history
export const getUserAnalyses = query({
  args: {
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) {
      return [];
    }

    const limit = args.limit || 10;

    // Get brand analyses
    const brandAnalyses = await ctx.db
      .query("brand_analyses")
      .withIndex("by_user_id", (q) => q.eq("user_id", userId))
      .order("desc")
      .take(limit);

    // Get GEO analyses
    const geoAnalyses = await ctx.db
      .query("geo_analyses")
      .withIndex("by_user_id", (q) => q.eq("user_id", userId))
      .order("desc")
      .take(limit);

    // Combine and sort by timestamp
    const allAnalyses = [
      ...brandAnalyses.map(a => ({ ...a, type: "brand" as const })),
      ...geoAnalyses.map(a => ({ ...a, type: "geo" as const, analysis_timestamp: a.completed_at || 0 }))
    ].sort((a, b) => b.analysis_timestamp - a.analysis_timestamp);

    return allAnalyses.slice(0, limit);
  },
});

// Get user's reports
export const getUserReports = query({
  args: {
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) {
      return [];
    }

    const limit = args.limit || 10;

    return await ctx.db
      .query("reports")
      .withIndex("by_user_id", (q) => q.eq("user_id", userId))
      .order("desc")
      .take(limit);
  },
});

// Create or link session to authenticated user
export const linkSessionToUser = mutation({
  args: {
    session_id: v.string(),
    email: v.string(),
  },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) {
      throw new Error("Not authenticated");
    }

    const now = Date.now();
    
    // Check if session already exists
    const existingSession = await ctx.db
      .query("sessions")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .first();
    
    if (existingSession) {
      // Update existing session with user_id
      await ctx.db.patch(existingSession._id, {
        user_id: userId,
        email: args.email,
        last_active: now,
      });
      return existingSession._id;
    }
    
    // Create new session linked to user
    return await ctx.db.insert("sessions", {
      session_id: args.session_id,
      email: args.email,
      created_at: now,
      last_active: now,
      user_id: userId,
    });
  },
});