import { createClient } from "@supabase/supabase-js";

/**
 * This client runs in the browser.
 * For hackathon simplicity, we use the public anon key client-side for auth.
 * RLS in Supabase protects your data.
 */
export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);
