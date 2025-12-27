"use client";

import { useEffect, useState } from "react";
import Post from "@/components/Post";

const API = process.env.NEXT_PUBLIC_API_BASE_URL;

export default function LikedBlogsPage() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchLikedPosts() {
      try {
        const res = await fetch(`${API}/api/posts/me/likes/`, {
          credentials: "include",
        });

        if (!res.ok) throw new Error("Failed to fetch likes");

        const likedPosts = await res.json();
        const list = Array.isArray(likedPosts)
          ? likedPosts
          : likedPosts.results || [];

        // 🔥 fetch full post details to get author
        const enriched = await Promise.all(
          list.map(async (p) => {
            const detailRes = await fetch(
              `${API}/api/posts/${p.slug}/`
            );
            if (!detailRes.ok) return p;
            return await detailRes.json();
          })
        );

        setPosts(enriched);
      } catch (err) {
        console.error(err);
        setPosts([]);
      } finally {
        setLoading(false);
      }
    }

    fetchLikedPosts();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-zinc-400">
        Loading...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white px-6 py-16">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold mb-10">Liked Blogs</h1>

        {posts.length === 0 ? (
          <p className="text-zinc-500">You haven’t liked any posts yet.</p>
        ) : (
          <div className="grid gap-8">
            {posts.map((post) => (
              <Post
                key={post.slug}
                title={post.title}
                author={post.author}     // ✅ now exists
                tags_list={post.tags_list}
                likes={post.likes}
                created_at={post.created_at}
                slug={post.slug}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
