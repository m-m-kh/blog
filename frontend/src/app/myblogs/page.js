'use client'

import { useEffect, useState } from 'react'
import Post from '@/components/Post'
import AuthModal from '@/components/AuthModal'

const API = process.env.NEXT_PUBLIC_API_BASE_URL

function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
}

export default function MyBlogsPage() {
  const [blogs, setBlogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAuth, setShowAuth] = useState(false)
  const [user, setUser] = useState(null)

  const isAuthenticated = !!user?.message?.username
  const username = user?.message?.username

  // ✅ Fetch user info
  useEffect(() => {
    fetch(`${API}/api/account/me/`, { credentials: 'include' })
      .then(res => (res.ok ? res.json() : null))
      .then(setUser)
      .catch(() => setUser(null))
  }, [])

  // ✅ Fetch user's blogs after user is loaded
  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false)
      return
    }

    async function fetchBlogs() {
      try {
        const res = await fetch(`${API}/api/posts/me/`, {
          credentials: 'include',
        })
        if (!res.ok) throw new Error('Failed to fetch')
        const data = await res.json()
        const blogList = Array.isArray(data) ? data : data.results || []

        // Add author username to each blog
        const withAuthor = blogList.map(blog => ({
          ...blog,
          author: { username }, // All posts belong to this user
        }))

        setBlogs(withAuthor)
      } catch (err) {
        console.error(err)
        setBlogs([])
      } finally {
        setLoading(false)
      }
    }

    fetchBlogs()
  }, [isAuthenticated, username])

  // ✅ Delete a blog
  async function handleDelete(slug) {
    if (!confirm('Are you sure you want to delete this blog?')) return
    try {
      const res = await fetch(`${API}/api/posts/${slug}/`, {
        method: 'DELETE',
        credentials: 'include',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
      })
      if (res.status === 204) {
        setBlogs(prev => prev.filter(b => b.slug !== slug))
      }
    } catch (err) {
      console.error(err)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-zinc-400">
        Loading...
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center text-zinc-400">
        You must be logged in to see your blogs.
      </div>
    )
  }

  return (
    <>
      <div className="min-h-screen bg-gradient-to-b from-zinc-900 to-black text-white px-6 py-10 max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-center">My Blogs</h1>

        {blogs.length === 0 ? (
          <p className="text-zinc-400 text-center">
            You haven't created any blogs yet.
          </p>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {blogs.map(blog => (
              <div key={blog.slug} className="relative">
                <Post {...blog} />

                <button
                  onClick={() => handleDelete(blog.slug)}
                  className="absolute top-2 right-2 px-3 py-1 text-xs rounded-lg bg-red-600 hover:bg-red-500 transition"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  )
}
