'use client'

import { use, useEffect, useState } from 'react'
import AuthModal from '@/components/AuthModal'

const API = process.env.NEXT_PUBLIC_API_BASE_URL

function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
}

// ---------------- helper for RTL ----------------
const isPersianOrArabic = text => /[\u0600-\u06FF]/.test(text)

function renderContentWithDir(html) {
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  return Array.from(doc.body.childNodes).map((node, idx) => {
    const text = node.textContent || ''
    const dir = isPersianOrArabic(text) ? 'rtl' : 'ltr'

    // keep all styling, only add dir
    if (node.nodeName === 'P')
      return <p key={idx} dir={dir} dangerouslySetInnerHTML={{ __html: node.innerHTML }} />
    if (node.nodeName === 'H2')
      return <h2 key={idx} dir={dir} dangerouslySetInnerHTML={{ __html: node.innerHTML }} />
    if (node.nodeName === 'H3')
      return <h3 key={idx} dir={dir} dangerouslySetInnerHTML={{ __html: node.innerHTML }} />
    if (node.nodeName === 'IMG')
      return (
        <img
          key={idx}
          src={node.getAttribute('src')}
          alt=""
          className="mx-auto my-6 rounded-xl max-w-[85%] shadow-md border border-zinc-700"
        />
      )

    return <div key={idx} dir={dir} dangerouslySetInnerHTML={{ __html: node.outerHTML }} />
  })
}

export default function BlogDetailPage({ params }) {
  const { slug } = use(params)

  const [post, setPost] = useState(null)
  const [comments, setComments] = useState([])
  const [commentText, setCommentText] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [editingText, setEditingText] = useState('')
  const [loading, setLoading] = useState(true)
  const [liking, setLiking] = useState(false)
  const [showAuth, setShowAuth] = useState(false)
  const [user, setUser] = useState(null)

  const username = user?.message?.username
  const isAuthenticated = !!username

  /* ---------------- user ---------------- */
  useEffect(() => {
    fetch(`${API}/api/account/me/`, { credentials: 'include' })
      .then(res => (res.ok ? res.json() : null))
      .then(setUser)
      .catch(() => setUser(null))
  }, [])

  /* ---------------- post + comments ---------------- */
  useEffect(() => {
    async function fetchData() {
      try {
        const postRes = await fetch(`${API}/api/posts/${slug}/`, {
          credentials: 'include',
        })
        if (!postRes.ok) throw new Error()
        setPost(await postRes.json())

        const commentRes = await fetch(`${API}/api/posts/${slug}/comment/`, {
          credentials: 'include',
        })
        if (commentRes.ok) {
          const data = await commentRes.json()
          setComments(data.results || [])
        }
      } catch {
        setPost(null)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [slug])

  /* ---------------- like ---------------- */
  async function handleLike() {
    if (!isAuthenticated) return setShowAuth(true)
    if (liking) return

    setLiking(true)
    try {
      await fetch(`${API}/api/posts/${slug}/toggle_like/`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
      })

      const refreshed = await fetch(`${API}/api/posts/${slug}/`, {
        credentials: 'include',
      })
      setPost(await refreshed.json())
    } finally {
      setLiking(false)
    }
  }

  /* ---------------- add comment ---------------- */
  async function handleCommentSubmit(e) {
    e.preventDefault()
    if (!isAuthenticated) return setShowAuth(true)
    if (!commentText.trim()) return

    const res = await fetch(`${API}/api/posts/${slug}/comment/`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({ content: commentText }),
    })

    if (!res.ok) return

    const newComment = await res.json()
    setComments(prev => [newComment, ...prev])
    setCommentText('')
  }

  /* ---------------- edit comment ---------------- */
  async function handleUpdate(id) {
    const res = await fetch(`${API}/api/posts/${slug}/comment/${id}/`, {
      method: 'PATCH',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({ content: editingText }),
    })

    if (!res.ok) return

    const updated = await res.json()
    setComments(prev => prev.map(c => (c.url === updated.url ? updated : c)))
    setEditingId(null)
  }

  /* ---------------- delete comment ---------------- */
  async function handleDelete(id) {
    if (!confirm('Delete this comment?')) return

    const res = await fetch(`${API}/api/posts/${slug}/comment/${id}/`, {
      method: 'DELETE',
      credentials: 'include',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
    })

    if (res.status === 204) {
      setComments(prev => prev.filter(c => !c.url.endsWith(`/${id}/`)))
    }
  }

  /* ---------------- UI ---------------- */
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-zinc-400">
        Loading...
      </div>
    )
  }

  if (!post) {
    return (
      <div className="min-h-screen flex items-center justify-center text-red-400">
        Post not found
      </div>
    )
  }

  // ✅ normalize tags (string OR array)
  const tags =
    Array.isArray(post.tags_list)
      ? post.tags_list
      : typeof post.tags_list === 'string' && post.tags_list.trim()
      ? post.tags_list.split(',').map(t => t.trim())
      : []

  return (
    <>
      <div className="min-h-screen bg-gradient-to-b from-zinc-900 to-black text-white">
        <div className="max-w-3xl mx-auto px-6 py-16">

          {/* TITLE */}
          <h1 className="text-4xl font-bold mb-2">{post.title}</h1>

          <div className="text-sm text-zinc-400 mb-4">
            {post.author.username} •{' '}
            {new Date(post.created_at).toLocaleDateString()}
          </div>

          {/* TAGS */}
          {tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-10">
              {tags.map(tag => (
                <span
                  key={tag}
                  className="px-3 py-1 text-sm rounded-full
                             bg-zinc-800 text-zinc-300
                             border border-zinc-700"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}

          {/* BLOG CONTENT */}
          <div
            className="[&_p]:mb-4 [&_p]:text-zinc-300 [&_p]:leading-relaxed
                        [&_img]:mx-auto [&_img]:my-6 [&_img]:rounded-xl [&_img]:max-w-[85%]
                        [&_img]:shadow-md [&_img]:border [&_img]:border-zinc-700
                        [&_h2]:text-2xl [&_h2]:font-bold [&_h2]:mt-10 [&_h2]:mb-4
                        [&_h3]:text-xl [&_h3]:font-semibold [&_h3]:mt-8 [&_h3]:mb-3"
          >
            {renderContentWithDir(post.content)}
          </div>

          {/* LIKE BUTTON */}
          <div className="my-10">
            <button
              onClick={handleLike}
              className={`flex items-center gap-2 px-6 py-2 rounded-full
                ${
                  post.you_liked
                    ? 'bg-pink-600 hover:bg-pink-500'
                    : 'bg-zinc-800 hover:bg-zinc-700'
                }`}
            >
              ❤️ {post.likes}
            </button>
          </div>

          {/* COMMENTS */}
          <section className="mt-16 space-y-6">
            <h2 className="text-2xl font-semibold mb-6">
              Comments ({comments.length})
            </h2>

            <div className="space-y-4">
              {comments.map(c => {
                const isOwner = c.author?.username === username
                const id = c.url.split('/').filter(Boolean).pop()

                return (
                  <div
                    key={c.url}
                    className="bg-zinc-800/60 p-4 rounded-xl border border-zinc-700"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        {c.author?.profile_pic && (
                          <img
                            src={c.author.profile_pic}
                            className="w-8 h-8 rounded-full object-cover"
                          />
                        )}
                        <span className="text-sm text-zinc-400">
                          {c.author?.username || 'Anonymous'}
                        </span>
                      </div>

                      {isOwner && (
                        <div className="flex items-center gap-3 text-sm">
                          <button
                            onClick={() => {
                              setEditingId(id)
                              setEditingText(c.content)
                            }}
                            className="text-sky-400 hover:text-sky-300"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDelete(id)}
                            className="text-red-400 hover:text-red-300"
                          >
                            Delete
                          </button>
                        </div>
                      )}
                    </div>

                    {editingId === id ? (
                      <>
                        <textarea
                          value={editingText}
                          onChange={e => setEditingText(e.target.value)}
                          className="w-full min-h-[100px] resize-none rounded-xl
                            bg-zinc-900 border border-zinc-700
                            p-4 text-white mb-3"
                        />
                        <div className="flex gap-4">
                          <button
                            onClick={() => handleUpdate(id)}
                            className="text-sky-400 hover:underline"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => setEditingId(null)}
                            className="text-zinc-400 hover:underline"
                          >
                            Cancel
                          </button>
                        </div>
                      </>
                    ) : (
                      <p className="text-zinc-200 leading-relaxed">{c.content}</p>
                    )}
                  </div>
                )
              })}

              {comments.length === 0 && (
                <p className="text-zinc-500">No comments yet.</p>
              )}
            </div>

            {/* ADD COMMENT */}
            <form onSubmit={handleCommentSubmit} className="space-y-4">
              <textarea
                value={commentText}
                onChange={e => setCommentText(e.target.value)}
                placeholder="Write a comment..."
                className="w-full min-h-[120px] resize-none rounded-xl
                  bg-zinc-900 border border-zinc-700
                  p-4 text-white placeholder-zinc-500
                  focus:outline-none focus:ring-2 focus:ring-zinc-500"
              />

              <button
                type="submit"
                className="px-6 py-2 rounded-lg bg-white text-black
                  font-medium hover:bg-zinc-200 transition"
              >
                Submit Comment
              </button>
            </form>
          </section>
        </div>
      </div>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  )
}
