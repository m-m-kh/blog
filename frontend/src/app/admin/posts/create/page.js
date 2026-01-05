'use client'

import { useEffect, useRef, useState } from 'react'
import { EditorContent, useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import Placeholder from '@tiptap/extension-placeholder'
import { useRouter } from 'next/navigation'
import AuthModal from '@/components/AuthModal'

const API = process.env.NEXT_PUBLIC_API_BASE_URL

function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
}

export default function CreatePostPage() {
  const router = useRouter()
  const fileInputRef = useRef(null)

  const [title, setTitle] = useState('')
  const [tags, setTags] = useState('')
  const [publishing, setPublishing] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [user, setUser] = useState(null)
  const [showAuth, setShowAuth] = useState(false)

  const isAuthenticated = !!user?.message?.username

  /* ---------------- editor ---------------- */
  const editor = useEditor({
    immediatelyRender: false,
    extensions: [
      StarterKit,
      Image,
      Placeholder.configure({
        placeholder: 'Start writing your post...',
      }),
    ],
    content: '',
  })

  /* ---------------- auth ---------------- */
  useEffect(() => {
    fetch(`${API}/api/account/me/`, { credentials: 'include' })
      .then(res => (res.ok ? res.json() : null))
      .then(setUser)
      .catch(() => setUser(null))
  }, [])

  /* ---------------- image upload ---------------- */
  async function handleImageUpload(file) {
    if (!file || !editor) return
    if (!isAuthenticated) return setShowAuth(true)

    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch(`${API}/api/post_media/`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        body: formData,
      })

      if (!res.ok) throw new Error()
      const media = await res.json()

      editor.chain().focus().setImage({ src: media.file }).run()
    } finally {
      setUploading(false)
    }
  }

  /* ---------------- submit ---------------- */
  async function handleSubmit() {
    if (!editor) return
    if (!isAuthenticated) return setShowAuth(true)

    const content = editor.getHTML().trim()
    if (!title.trim() || content === '<p></p>') {
      alert('Title and content are required')
      return
    }

    setPublishing(true)
    try {
      const res = await fetch(`${API}/api/posts/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
          title,
          content,
          tags_list: tags.split(',').map(t => t.trim()).filter(Boolean),
          status: true,
        }),
      })

      if (!res.ok) throw new Error()
      const post = await res.json()
      router.push(`/blogs/${post.slug}`)
    } finally {
      setPublishing(false)
    }
  }

  return (
    <>
      <div className="min-h-screen bg-gradient-to-b from-zinc-900 to-black text-white">
        <div className="max-w-3xl mx-auto px-6 py-16">
          <h1 className="text-3xl font-bold mb-10">Create New Post</h1>

          <div className="space-y-6">
            <input
              value={title}
              onChange={e => setTitle(e.target.value)}
              placeholder="Post title"
              className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3
                         text-lg focus:outline-none focus:ring-2 focus:ring-zinc-500"
            />

            <input
              value={tags}
              onChange={e => setTags(e.target.value)}
              placeholder="Tags (comma separated)"
              className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3
                         focus:outline-none focus:ring-2 focus:ring-zinc-500"
            />

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => {
                  if (!isAuthenticated) return setShowAuth(true)
                  fileInputRef.current?.click()
                }}
                className="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 transition"
                disabled={!editor}
              >
                🖼 Upload Image
              </button>

              {uploading && (
                <span className="text-sm text-zinc-400 self-center">
                  Uploading image...
                </span>
              )}
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              hidden
              onChange={e => handleImageUpload(e.target.files?.[0])}
            />

            <div className="border border-zinc-700 rounded-xl bg-zinc-900
                            focus-within:ring-2 focus-within:ring-zinc-500 transition">
              <EditorContent
                editor={editor}
                className="prose prose-invert max-w-none
                  min-h-[300px] p-6 text-zinc-100 caret-white
                  [&_.ProseMirror]:outline-none
                  [&_.ProseMirror]:min-h-[300px]
                  [&_.ProseMirror_img]:mx-auto
                  [&_.ProseMirror_img]:max-w-[85%]
                  [&_.ProseMirror_img]:rounded-xl
                  [&_.ProseMirror_img]:my-8"
              />
            </div>

            <button
              onClick={handleSubmit}
              disabled={publishing || !editor}
              className="px-6 py-3 rounded-lg bg-white text-black font-semibold
                         hover:bg-zinc-200 transition disabled:opacity-50"
            >
              {publishing ? 'Publishing...' : 'Publish'}
            </button>
          </div>
        </div>
      </div>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  )
}
