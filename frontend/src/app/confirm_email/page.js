"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

export default function ConfirmEmailPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const user_id = searchParams.get("uid");

  const [status, setStatus] = useState("loading");

  useEffect(() => {
    if (!token || !user_id) {
      setStatus("invalid");
      return;
    }

    fetch("http://localhost:8000/api/account/email_confirmation/", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, user_id }),
    })
      .then((res) => {
        if (res.ok) setStatus("success");
        else setStatus("error");
      })
      .catch(() => setStatus("error"));
  }, [token, user_id]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-950 px-4">
      <div className="w-full max-w-md rounded-2xl border border-zinc-800 bg-zinc-900 p-6 shadow-xl text-center">
        {status === "loading" && (
          <>
            <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-zinc-700 border-t-sky-500" />
            <h1 className="text-lg font-semibold text-white">
              Confirming your email…
            </h1>
            <p className="mt-2 text-sm text-zinc-400">
              Please wait a moment.
            </p>
          </>
        )}

        {status === "success" && (
          <>
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-500/10 text-green-500 text-2xl">
              ✓
            </div>
            <h1 className="text-xl font-semibold text-white">
              Email confirmed 🎉
            </h1>
            <p className="mt-2 text-sm text-zinc-400">
              Your account is now active. You can safely log in.
            </p>

            <a
              href="/"
              className="mt-6 inline-block rounded-lg bg-sky-500 px-5 py-2 text-sm font-medium text-black hover:bg-sky-400 transition"
            >
              Go to home
            </a>
          </>
        )}

        {status === "invalid" && (
          <>
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-yellow-500/10 text-yellow-500 text-2xl">
              !
            </div>
            <h1 className="text-xl font-semibold text-white">
              Invalid confirmation link
            </h1>
            <p className="mt-2 text-sm text-zinc-400">
              This link is incomplete or malformed.
            </p>
          </>
        )}

        {status === "error" && (
          <>
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-500/10 text-red-500 text-2xl">
              ✕
            </div>
            <h1 className="text-xl font-semibold text-white">
              Confirmation failed
            </h1>
            <p className="mt-2 text-sm text-zinc-400">
              The link may be expired or already used.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
