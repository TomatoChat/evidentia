import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Save GEO analysis results
export const saveGeoAnalysis = mutation({
  args: {
    session_id: v.string(),
    brand_name: v.string(),
    search_queries: v.array(v.string()),
    competitors: v.optional(v.array(v.string())),
    llm_models: v.optional(v.array(v.string())),
    optimization_suggestions: v.optional(v.string()),
    progress_status: v.number(),
    analysis_result: v.optional(v.any()),
    status: v.union(v.literal("pending"), v.literal("in_progress"), v.literal("completed"), v.literal("failed")),
  },
  handler: async (ctx, args) => {
    // Check if GEO analysis already exists for this session
    const existingAnalysis = await ctx.db
      .query("geo_analyses")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .first();
    
    const analysisData = {
      session_id: args.session_id,
      brand_name: args.brand_name,
      search_queries: args.search_queries,
      competitors: args.competitors,
      llm_models: args.llm_models,
      optimization_suggestions: args.optimization_suggestions,
      progress_status: args.progress_status,
      analysis_result: args.analysis_result,
      status: args.status,
      completed_at: args.status === "completed" ? Date.now() : undefined,
    };
    
    if (existingAnalysis) {
      // Update existing analysis
      await ctx.db.patch(existingAnalysis._id, analysisData);
      return existingAnalysis._id;
    }
    
    // Create new analysis
    return await ctx.db.insert("geo_analyses", analysisData);
  },
});

// Get GEO analysis by session_id
export const getGeoAnalysis = query({
  args: { session_id: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("geo_analyses")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .first();
  },
});

// Update GEO analysis progress
export const updateGeoAnalysisProgress = mutation({
  args: {
    session_id: v.string(),
    progress_status: v.number(),
    status: v.optional(v.union(v.literal("pending"), v.literal("in_progress"), v.literal("completed"), v.literal("failed"))),
    analysis_result: v.optional(v.any()),
    optimization_suggestions: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const analysis = await ctx.db
      .query("geo_analyses")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .first();
    
    if (!analysis) {
      throw new Error("GEO analysis not found");
    }
    
    const updateData: any = {
      progress_status: args.progress_status,
    };
    
    if (args.status !== undefined) {
      updateData.status = args.status;
      if (args.status === "completed") {
        updateData.completed_at = Date.now();
      }
    }
    
    if (args.analysis_result !== undefined) {
      updateData.analysis_result = args.analysis_result;
    }
    
    if (args.optimization_suggestions !== undefined) {
      updateData.optimization_suggestions = args.optimization_suggestions;
    }
    
    await ctx.db.patch(analysis._id, updateData);
    return analysis._id;
  },
});

// Get all GEO analyses by status
export const getGeoAnalysesByStatus = query({
  args: { status: v.union(v.literal("pending"), v.literal("in_progress"), v.literal("completed"), v.literal("failed")) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("geo_analyses")
      .withIndex("by_status", (q) => q.eq("status", args.status))
      .collect();
  },
});

// Get GEO analyses by progress range
export const getGeoAnalysesByProgress = query({
  args: {
    min_progress: v.number(),
    max_progress: v.number(),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("geo_analyses")
      .withIndex("by_progress", (q) => 
        q.gte("progress_status", args.min_progress).lte("progress_status", args.max_progress)
      )
      .collect();
  },
});