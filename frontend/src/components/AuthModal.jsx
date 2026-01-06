"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_BASE_URL

export default function AuthModal({ onClose }) {
  const [mode, setMode] = useState("login"); // "login" or "signup"
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    username: "",
    first_name: "",
    last_name: "",
    email: "",
    password1: "",
    password2: "",
    password: "", // for login
    email_or_username: "", // for login
  });

  // Helper to fetch CSRF cookie
  async function getCSRF() {
    await fetch(`${API}/api/account/get_csrf/`, {
      credentials: "include",
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);

    try {
      // Always fetch CSRF before POST
      await getCSRF();

      let url = "";
      let body = {};

      if (mode === "login") {
        url = `${API}/api/account/login/`;
        body = {
          email_or_username: form.email_or_username,
          password: form.password,
        };
      } else {
        url = `${API}/api/account/signup/`;
        body = {
          username: form.username,
          first_name: form.first_name,
          last_name: form.last_name,
          email: form.email,
          password1: form.password1,
          password2: form.password2,
        };
      }

      // Send POST request
      const csrftoken = document.cookie
        .split("; ")
        .find((row) => row.startsWith("csrftoken="))
        ?.split("=")[1];

      const res = await fetch(url, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify(body),
      });

      const data = await res.json();

      if (res.ok && data.success) {
        alert(data.message || "Success!");
        onClose();
        location.reload();
      } else {
        alert(data.message || JSON.stringify(data));
      }
    } catch (err) {
      console.error(err);
      alert("Network or server error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center">
      <div className="bg-zinc-900 p-6 rounded-xl w-full max-w-sm relative">
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-zinc-400 hover:text-white"
        >
          ✕
        </button>

        <h2 className="text-xl font-semibold mb-4">
          {mode === "login" ? "Login" : "Sign up"}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === "signup" && (
            <>
              <input
                type="text"
                placeholder="Username"
                value={form.username}
                onChange={(e) =>
                  setForm({ ...form, username: e.target.value })
                }
                className="w-full p-2 rounded bg-zinc-800 border border-zinc-700"
                required
              />
              <input
                type="text"
                placeholder="First name"
                value={form.first_name}
                onChange={(e) =>
                  setForm({ ...form, first_name: e.target.value })
                }
                className="w-full p-2 rounded bg-zinc-800 border border-zinc-700"
                required
              />
              <input
                type="text"
                placeholder="Last name"
                value={form.last_name}
                onChange={(e) =>
                  setForm({ ...form, last_name: e.target.value })
                }
                className="w-full p-2 rounded bg-zinc-800 border border-zinc-700"
                required
              />
              <input
                type="email"
                placeholder="Email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="w-full p-2 rounded bg-zinc-800 border border-zinc-700"
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={form.password1}
                onChange={(e) =>
                  setForm({ ...form, password1: e.target.value })
                }
                className="w-full p-2 rounded bg-zinc-800 border border-zinc-700"
                required
              />
              <input
                type="password"
                placeholder="Confirm Password"
                value={form.password2}
                onChange={(e) =>
                  setForm({ ...form, password2: e.target.value })
                }
                className="w-full p-2 rounded bg-zinc-800 border border-zinc-700"
                required
              />
            </>
          )}

          {mode === "login" && (
            <>
              <input
                type="text"
                placeholder="Email or Username"
                value={form.email_or_username}
                onChange={(e) =>
                  setForm({ ...form, email_or_username: e.target.value })
                }
                className="w-full p-2 rounded bg-zinc-800 border border-zinc-700"
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={form.password}
                onChange={(e) =>
                  setForm({ ...form, password: e.target.value })
                }
                className="w-full p-2 rounded bg-zinc-800 border border-zinc-700"
                required
              />
            </>
          )}

          <button
            type="submit"
            className="w-full py-2 rounded bg-sky-500 text-black font-medium disabled:opacity-50"
            disabled={loading}
          >
            {loading
              ? mode === "login"
                ? "Logging in..."
                : "Signing up..."
              : mode === "login"
              ? "Login"
              : "Create account"}
          </button>
        </form>

        <p className="text-sm text-zinc-400 mt-4">
          {mode === "login" ? (
            <>
              Don’t have an account?{" "}
              <button
                type="button"
                onClick={() => setMode("signup")}
                className="text-sky-400 hover:underline"
              >
                Sign up
              </button>
            </>
          ) : (
            <>
              Already have an account?{" "}
              <button
                type="button"
                onClick={() => setMode("login")}
                className="text-sky-400 hover:underline"
              >
                Login
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  );
}
