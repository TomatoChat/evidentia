import { convexAuth } from "@convex-dev/auth/server";
import GitHub from "@auth/core/providers/github";
import Google from "@auth/core/providers/google";
import Resend from "@auth/core/providers/resend";

export const { auth, signIn, signOut, store } = convexAuth({
  providers: [
    GitHub({
      clientId: process.env.AUTH_GITHUB_ID,
      clientSecret: process.env.AUTH_GITHUB_SECRET,
    }),
    Google({
      clientId: process.env.AUTH_GOOGLE_ID,
      clientSecret: process.env.AUTH_GOOGLE_SECRET,
    }),
    Resend({
      apiKey: process.env.AUTH_RESEND_KEY,
      from: process.env.AUTH_EMAIL_FROM || "noreply@evidentia.ai",
    }),
  ],
  callbacks: {
    async createOrUpdateUser(ctx, args) {
      // Check if user exists
      const existingUser = await ctx.db
        .query("users")
        .withIndex("by_email", (q) => q.eq("email", args.profile.email!))
        .first();

      const now = Date.now();
      
      if (existingUser) {
        // Update existing user
        await ctx.db.patch(existingUser._id, {
          last_active: now,
          name: args.profile.name || existingUser.name,
          image: args.profile.image || existingUser.image,
        });
        return existingUser._id;
      }

      // Create new user
      return await ctx.db.insert("users", {
        email: args.profile.email!,
        name: args.profile.name,
        image: args.profile.image,
        created_at: now,
        last_active: now,
        subscription_status: "free",
        analysis_count: 0,
      });
    },
  },
});