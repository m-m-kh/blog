"use client";

import { useEffect, useState } from "react";
import AuthModal from "./AuthModal";
import UserMenu from "./UserMenu";
import Link from "next/link";

const API_BASE = "http://localhost:8000";

export default function Sidebar() {
  const [open, setOpen] = useState(false);
  const [showAuth, setShowAuth] = useState(false);

  const [user, setUser] = useState(null);
  const isAuthenticated = !!user;

  // 🔑 fetch logged-in user
  useEffect(() => {
    fetch(`${API_BASE}/api/account/me/`, {
      credentials: "include",
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setUser(data))
      .catch(() => setUser(null));
  }, []);

  return (
    <>
      {/* Mobile Toggle */}
      <button
        className="fixed top-6 left-6 z-50 md:hidden text-2xl text-white"
        onClick={() => setOpen(!open)}
      >
        <i className={`fa-solid ${open ? "fa-xmark" : "fa-bars"}`} />
      </button>

      <aside
        className={`
          bg-zinc-900 py-10 px-6 text-center w-72
          transform transition-transform duration-300
          fixed inset-y-0 left-0 z-40
          ${open ? "translate-x-0" : "-translate-x-full"}
          md:sticky md:top-0 md:h-screen md:translate-x-0
          md:flex md:flex-col md:justify-between
        `}
      >
        {/* Logo */}
        <Link href="/" className="text-3xl font-bold tracking-wide">
          MojiDev<span className="text-sky-400">.</span>
        </Link>

        {/* Nav */}
        <nav className="mt-12">
          <ul className="space-y-4 text-lg">
            <li>
              <Link
                href="/"
                className="text-sky-400 font-semibold"
              >
                Home
              </Link>
            </li>

            <li>
              <Link
                href="/blogs"
                className="hover:text-sky-400 transition"
              >
                Blogs
              </Link>
            </li>

            <li>
              <Link
                href="/about"
                className="hover:text-sky-400 transition"
              >
                About
              </Link>
            </li>

            <li>
              <Link
                href="/contact"
                className="hover:text-sky-400 transition"
              >
                Contact
              </Link>
            </li>
          </ul>
        </nav>

        {/* Auth Section */}
        <div className="mt-10">
          {!isAuthenticated ? (
            <button
              onClick={() => setShowAuth(true)}
              className="w-full py-2 rounded-lg bg-sky-500 text-black font-medium hover:bg-sky-400 transition"
            >
              Login / Sign up
            </button>
          ) : (
            <UserMenu user={user} onLogout={() => setUser(null)} />
          )}
        </div>

        <div className="text-sm text-zinc-400 mt-10">
          © 2026 All rights reserved
        </div>
      </aside>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  );
}
