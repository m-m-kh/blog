'use client';

import { useEffect, useState, useMemo } from "react";
import Post from "@/components/Post";

const SORTS = {
  NEWEST: "newest",
  OLDEST: "oldest",
  MOST_LIKED: "most_liked",
  LEAST_LIKED: "least_liked",
};

export default function BlogsPage() {
  const [posts, setPosts] = useState([]);
  const [sortBy, setSortBy] = useState(SORTS.NEWEST);

  useEffect(() => {
    async function fetchPosts() {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/posts/`
      );
      const data = await res.json();
      setPosts(data.results || []);
    }

    fetchPosts();
  }, []);

  // 🔹 SORT LOGIC (no mutation)
  const sortedPosts = useMemo(() => {
    const copy = [...posts];

    switch (sortBy) {
      case SORTS.NEWEST:
        return copy.sort(
          (a, b) => new Date(b.created_at) - new Date(a.created_at)
        );

      case SORTS.OLDEST:
        return copy.sort(
          (a, b) => new Date(a.created_at) - new Date(b.created_at)
        );

      case SORTS.MOST_LIKED:
        return copy.sort(
          (a, b) => (b.likes || 0) - (a.likes || 0)
        );

      case SORTS.LEAST_LIKED:
        return copy.sort(
          (a, b) => (a.likes || 0) - (b.likes || 0)
        );

      default:
        return copy;
    }
  }, [posts, sortBy]);

  return (
    <div className="min-h-screen bg-black text-white px-6 py-10 max-w-6xl mx-auto">
      <h1 className="text-4xl font-bold mb-8 text-center">Blogs</h1>

      {/* 🔘 SORT BUTTONS — SAME STYLING */}
      <div className="flex flex-wrap justify-center gap-4 mb-10">
        {Object.values(SORTS).map((type) => (
          <button
            key={type}
            onClick={() => setSortBy(type)}
            className={`px-4 py-2 border rounded transition ${
              sortBy === type
                ? "border-sky-400 text-sky-400"
                : "border-zinc-700 text-zinc-400 hover:border-zinc-400"
            }`}
          >
            {type.replace("_", " ").toUpperCase()}
          </button>
        ))}
      </div>

      {/* 🧱 POSTS GRID */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {sortedPosts.map((post) => (
          <Post key={post.slug} {...post} />
        ))}

        {sortedPosts.length === 0 && (
          <p className="text-zinc-400 col-span-full text-center">
            No blogs yet
          </p>
        )}
      </div>
    </div>
  );
}
