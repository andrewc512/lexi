"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabaseClient";

export default function AuthCallback() {
  const router = useRouter();

  useEffect(() => {
    const finishLogin = async () => {
      // This reads the access_token from the URL hash
      // and saves the session into Supabase
      const { data, error } = await supabase.auth.getSession();

      if (error) {
        console.error(error);
        router.push("/login?error=oauth");
        return;
      }

      // User is now logged in 🎉
      router.push("/dashboard");
    };

    finishLogin();
  }, [router]);

  return (
    <div className="h-screen flex items-center justify-center">
      Signing you in…
    </div>
  );
}
