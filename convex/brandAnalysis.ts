import { mutation, query } from "./_generated/server";
import { getAuthUserId } from "@convex-dev/auth/server";
import { v } from "convex/values";

// Save brand analysis results
export const saveBrandAnalysis = mutation({
  args: {
    session_id: v.string(),
    brand_name: v.string(),
    brand_website: v.optional(v.string()),
    brand_country: v.optional(v.string()),
    brand_description: v.optional(v.string()),
    brand_industry: v.optional(v.string()),
    competitors: v.optional(v.array(v.string())),
    status: v.union(v.literal("pending"), v.literal("completed"), v.literal("failed")),
    result_data: v.optional(v.any()),
    sources: v.optional(v.array(v.any())),
  },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    
    // Log authentication status for debugging
    console.log(`Saving brand analysis - User ID: ${userId ? userId : 'ANONYMOUS'}, Session: ${args.session_id}`);
    
    // Check if analysis already exists for this session
    const existingAnalysis = await ctx.db
      .query("brand_analyses")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .first();
    
    const analysisData = {
      session_id: args.session_id,
      user_id: userId || undefined, // undefined for anonymous users
      brand_name: args.brand_name,
      brand_website: args.brand_website,
      brand_country: args.brand_country,
      brand_description: args.brand_description,
      brand_industry: args.brand_industry,
      competitors: args.competitors,
      analysis_timestamp: Date.now(),
      status: args.status,
      result_data: args.result_data,
      sources: args.sources,
    };
    
    try {
      if (existingAnalysis) {
        // Update existing analysis
        await ctx.db.patch(existingAnalysis._id, analysisData);
        console.log(`✅ Updated brand analysis for ${userId ? 'authenticated' : 'anonymous'} user - ID: ${existingAnalysis._id}`);
        return existingAnalysis._id;
      }
      
      // Create new analysis
      const newId = await ctx.db.insert("brand_analyses", analysisData);
      console.log(`✅ Created brand analysis for ${userId ? 'authenticated' : 'anonymous'} user - ID: ${newId}`);
      return newId;
    } catch (error) {
      console.error('❌ Failed to save brand analysis:', error);
      throw new Error(`Failed to save brand analysis: ${error}`);
    }
  },
});

// Get brand analysis by session_id
export const getBrandAnalysis = query({
  args: { session_id: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("brand_analyses")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .first();
  },
});

// Update brand analysis status
export const updateBrandAnalysisStatus = mutation({
  args: {
    session_id: v.string(),
    status: v.union(v.literal("pending"), v.literal("completed"), v.literal("failed")),
    result_data: v.optional(v.any()),
  },
  handler: async (ctx, args) => {
    const analysis = await ctx.db
      .query("brand_analyses")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .first();
    
    if (!analysis) {
      throw new Error("Brand analysis not found");
    }
    
    const updateData: any = {
      status: args.status,
      analysis_timestamp: Date.now(),
    };
    
    if (args.result_data !== undefined) {
      updateData.result_data = args.result_data;
    }
    
    await ctx.db.patch(analysis._id, updateData);
    return analysis._id;
  },
});

// Get all brand analyses by status
export const getBrandAnalysesByStatus = query({
  args: { status: v.union(v.literal("pending"), v.literal("completed"), v.literal("failed")) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("brand_analyses")
      .withIndex("by_status", (q) => q.eq("status", args.status))
      .collect();
  },
});

// Get user's brand analyses (authenticated)
export const getUserBrandAnalyses = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) {
      return [];
    }

    const limit = args.limit || 10;
    
    return await ctx.db
      .query("brand_analyses")
      .withIndex("by_user_id", (q) => q.eq("user_id", userId))
      .order("desc")
      .take(limit);
  },
});

// Get brand analysis for authenticated user by session
export const getUserBrandAnalysisBySession = query({
  args: { session_id: v.string() },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    
    const analysis = await ctx.db
      .query("brand_analyses")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .first();
    
    // If user is authenticated and owns the analysis, return it
    if (userId && analysis?.user_id === userId) {
      return analysis;
    }
    
    // If not authenticated or doesn't own it, still return for session-based access
    return analysis;
  },
});