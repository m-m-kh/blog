"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function UserMenu({ user, onLogout }) {
  console.log("UserMenu received user:", user); // <-- Add this

  const [open, setOpen] = useState(false);
  const router = useRouter();

  const username = user?.message.first_name || "User";
  const initial = username[0].toUpperCase();

  function goToLiked() {
    setOpen(false);
    router.push("/liked");
  }

  async function handleLogout() {
    await fetch("http://localhost:8000/api/account/logout/", {
      method: "POST",
      credentials: "include",
      headers: {
        "X-CSRFToken": getCSRF(),
      },
    });

    onLogout();
  }

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 transition"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-sky-500 flex items-center justify-center text-black font-bold">
            {initial}
          </div>
          <span className="font-medium">{username}</span>
        </div>
        <span className="text-sm opacity-70">▾</span>
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-full rounded-lg bg-zinc-800 shadow-lg overflow-hidden">
          <button
            onClick={goToLiked}
            className="w-full px-4 py-2 text-left hover:bg-zinc-700"
          >
            Liked blogs
          </button>

          <button
            onClick={handleLogout}
            className="w-full px-4 py-2 text-left text-red-400 hover:bg-zinc-700"
          >
            Logout
          </button>
        </div>
      )}
    </div>
  );
}

function getCSRF() {
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1];
}
