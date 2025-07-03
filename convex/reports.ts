import { mutation, query } from "./_generated/server";
import { getAuthUserId } from "@convex-dev/auth/server";
import { v } from "convex/values";

// Save report history
export const saveReport = mutation({
  args: {
    session_id: v.string(),
    report_type: v.union(v.literal("brand_analysis"), v.literal("geo_analysis"), v.literal("combined")),
    report_data: v.any(),
    email_sent: v.boolean(),
    recipient_email: v.string(),
    brand_name: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    
    // Log authentication status for debugging
    console.log(`Saving report - User ID: ${userId ? userId : 'ANONYMOUS'}, Session: ${args.session_id}, Type: ${args.report_type}`);
    
    try {
      const newId = await ctx.db.insert("reports", {
        session_id: args.session_id,
        user_id: userId || undefined, // undefined for anonymous users
        report_type: args.report_type,
        report_data: args.report_data,
        email_sent: args.email_sent,
        recipient_email: args.recipient_email,
        generated_at: Date.now(),
        brand_name: args.brand_name,
      });
      
      console.log(`✅ Created report for ${userId ? 'authenticated' : 'anonymous'} user - ID: ${newId}`);
      return newId;
    } catch (error) {
      console.error('❌ Failed to save report:', error);
      throw new Error(`Failed to save report: ${error}`);
    }
  },
});

// Get reports by session_id
export const getReportsBySession = query({
  args: { session_id: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("reports")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .collect();
  },
});

// Get reports by email
export const getReportsByEmail = query({
  args: { email: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("reports")
      .withIndex("by_email", (q) => q.eq("recipient_email", args.email))
      .collect();
  },
});

// Get reports by type
export const getReportsByType = query({
  args: { report_type: v.union(v.literal("brand_analysis"), v.literal("geo_analysis"), v.literal("combined")) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("reports")
      .withIndex("by_type", (q) => q.eq("report_type", args.report_type))
      .collect();
  },
});

// Update report email status
export const updateReportEmailStatus = mutation({
  args: {
    report_id: v.id("reports"),
    email_sent: v.boolean(),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.report_id, {
      email_sent: args.email_sent,
    });
    
    return args.report_id;
  },
});

// Get recent reports (last 30 days)
export const getRecentReports = query({
  args: {
    days: v.optional(v.number()), // defaults to 30 days
  },
  handler: async (ctx, args) => {
    const daysBack = args.days || 30;
    const thirtyDaysAgo = Date.now() - (daysBack * 24 * 60 * 60 * 1000);
    
    return await ctx.db
      .query("reports")
      .withIndex("by_timestamp", (q) => q.gte("generated_at", thirtyDaysAgo))
      .collect();
  },
});