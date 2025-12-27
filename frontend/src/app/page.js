'use client';

import Link from "next/link";
import Image from "next/image";
import Post from "@/components/Post";
import { useEffect, useState } from "react";


export default function Home() {
  const [posts, setPosts] = useState([]);

   useEffect(() => {
    async function fetchPosts() {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/posts/`);
      const data = await res.json();

      setPosts(data.results || []);
    }

    fetchPosts();
  }, []);
  return (
    <div className="flex min-h-screen bg-black text-white">
      

      {/* Main Content */}
      <main className="flex-1">
        <section
          className="relative flex min-h-screen items-center justify-center bg-cover bg-center"
          style={{ backgroundImage: "url('/bg_1.jpg')" }}
        >
          {/* Overlay */}
          <div className="absolute inset-0 bg-black/60" />

          {/* Content */}
          <div className="relative z-10 max-w-2xl text-center px-6">
            {/* Author Image */}
            <div className="mx-auto mb-6 w-32 h-32 rounded-full overflow-hidden">
              <Image
                src="/author.jpg"
                alt="Author"
                width={128}
                height={128}
                priority
              />
            </div>

            <h2 className="text-sm tracking-widest text-sky-400 uppercase mb-2">
              Hello I’m
            </h2>

            <h1 className="text-4xl md:text-5xl font-bold mb-6">
              Mojtaba
            </h1>

            <p className="text-zinc-300 leading-relaxed mb-8">
              I am a Web Developer and Blogger. Far far away, behind the word mountains, far from
              the countries Vokalia and Consonantia, there live the blind texts.
            </p>
            <Link href="/about" className="inline-flex items-center gap-2 border border-sky-400 px-6 py-3 text-sky-400 hover:bg-sky-400 hover:text-black transition">
              More About Me →
            </Link>
          </div>
        </section>
        <div className="max-w-6xl mx-auto px-6 py-10">
        {/* Heading */}
        <div className="text-center max-w-2xl mx-auto mb-14">
          <h2 className="text-3xl font-bold mb-4">Blogs</h2>
          <p className="text-zinc-400">
            Thoughts, notes, and write-ups about technology, travel, and ideas.
          </p>
        </div>

        {/* Posts Grid */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 mb-14">
            {posts.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 5).map((post) => (
              <Post key={post.slug} {...post} />
            ))}

            {posts.length === 0 && (
              <p className="text-zinc-400 text-center col-span-full">
                No blogs yet
              </p>
            )}
          </div>

        {/* Show All Blogs */}
        <div className="text-center">
          <Link
            href="/blogs"
            className="inline-flex items-center gap-2 border border-sky-400 px-6 py-3 text-sky-400 hover:bg-sky-400 hover:text-black transition"
          >
            Show all blogs →
          </Link>
        </div>
      </div>
      </main>
    </div>
  );
}
