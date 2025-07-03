import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";
import { authTables } from "@convex-dev/auth/server";

export default defineSchema({
  // Include Convex Auth tables
  ...authTables,

  // User profiles table (extends auth)
  users: defineTable({
    name: v.optional(v.string()),
    email: v.string(),
    image: v.optional(v.string()),
    emailVerified: v.optional(v.number()),
    created_at: v.number(),
    last_active: v.number(),
    subscription_status: v.optional(v.union(v.literal("free"), v.literal("pro"), v.literal("enterprise"))),
    analysis_count: v.optional(v.number()),
  })
    .index("by_email", ["email"]),

  // User sessions table (legacy - keeping for compatibility)
  sessions: defineTable({
    session_id: v.string(),
    email: v.string(),
    created_at: v.number(), // timestamp
    last_active: v.number(), // timestamp
    user_id: v.optional(v.id("users")), // Link to authenticated user
  })
    .index("by_session_id", ["session_id"])
    .index("by_email", ["email"])
    .index("by_user_id", ["user_id"]),

  // Brand analysis results table
  brand_analyses: defineTable({
    session_id: v.string(),
    user_id: v.optional(v.id("users")), // Link to authenticated user
    brand_name: v.string(),
    brand_website: v.optional(v.string()),
    brand_country: v.optional(v.string()),
    brand_description: v.optional(v.string()),
    brand_industry: v.optional(v.string()),
    competitors: v.optional(v.array(v.string())),
    analysis_timestamp: v.number(),
    status: v.union(v.literal("pending"), v.literal("completed"), v.literal("failed")),
    result_data: v.optional(v.any()), // Store the complete analysis result
    sources: v.optional(v.array(v.any())), // Store source data
  })
    .index("by_session_id", ["session_id"])
    .index("by_user_id", ["user_id"])
    .index("by_status", ["status"])
    .index("by_timestamp", ["analysis_timestamp"]),

  // GEO analysis data table
  geo_analyses: defineTable({
    session_id: v.string(),
    user_id: v.optional(v.id("users")), // Link to authenticated user
    brand_name: v.string(),
    search_queries: v.array(v.string()),
    competitors: v.optional(v.array(v.string())),
    llm_models: v.optional(v.array(v.string())),
    optimization_suggestions: v.optional(v.string()),
    progress_status: v.number(), // 0-100
    analysis_result: v.optional(v.any()), // Store the complete GEO analysis
    completed_at: v.optional(v.number()),
    status: v.union(v.literal("pending"), v.literal("in_progress"), v.literal("completed"), v.literal("failed")),
    sources: v.optional(v.array(v.any())), // Store source data
  })
    .index("by_session_id", ["session_id"])
    .index("by_user_id", ["user_id"])
    .index("by_status", ["status"])
    .index("by_progress", ["progress_status"]),

  // Report history table
  reports: defineTable({
    session_id: v.string(),
    user_id: v.optional(v.id("users")), // Link to authenticated user
    report_type: v.union(v.literal("brand_analysis"), v.literal("geo_analysis"), v.literal("combined")),
    report_data: v.any(), // Complete report data
    email_sent: v.boolean(),
    recipient_email: v.string(),
    generated_at: v.number(),
    brand_name: v.optional(v.string()),
  })
    .index("by_session_id", ["session_id"])
    .index("by_user_id", ["user_id"])
    .index("by_email", ["recipient_email"])
    .index("by_type", ["report_type"])
    .index("by_timestamp", ["generated_at"]),
});