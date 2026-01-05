'use client'

import { useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import AuthModal from '@/components/AuthModal'
import 'quill/dist/quill.snow.css'

const API = process.env.NEXT_PUBLIC_API_BASE_URL

function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
}

// Regex to detect Persian/Arabic characters
const isPersianOrArabic = text => /[\u0600-\u06FF]/.test(text)

export default function CreatePostPage() {
  const router = useRouter()
  const editorRef = useRef(null)
  const quillRef = useRef(null)
  const fileInputRef = useRef(null)

  const [title, setTitle] = useState('')
  const [tags, setTags] = useState('')
  const [publishing, setPublishing] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [user, setUser] = useState(null)
  const [showAuth, setShowAuth] = useState(false)

  const isAuthenticated = !!user?.message?.username

  /* ---------------- init quill (CLIENT ONLY) ---------------- */
  useEffect(() => {
    if (!editorRef.current || quillRef.current) return

    let mounted = true

    ;(async () => {
      const Quill = (await import('quill')).default
      if (!mounted) return

      quillRef.current = new Quill(editorRef.current, {
        theme: 'snow',
        placeholder: 'Start writing your post...',
        modules: {
          toolbar: [
            ['bold', 'italic', 'underline'],
            [{ header: [2, 3, false] }],
            [{ list: 'ordered' }, { list: 'bullet' }],
            ['image'],
            ['clean'],
          ],
        },
      })

      quillRef.current.root.style.unicodeBidi = 'plaintext'

      // Image upload handler
      quillRef.current.getModule('toolbar').addHandler('image', () => {
        fileInputRef.current?.click()
      })

      // Dynamically set RTL/LTR per line
      quillRef.current.on('text-change', () => {
        const selection = quillRef.current.getSelection()
        if (!selection) return

        const [line, offset] = quillRef.current.getLine(selection.index)
        if (!line || !line.domNode) return

        const text = line.domNode.innerText || ''
        if (text.trim().length === 0) {
          line.domNode.dir = 'ltr'
          line.domNode.style.textAlign = 'left'
          return
        }

        if (isPersianOrArabic(text)) {
          line.domNode.dir = 'rtl'
          line.domNode.style.textAlign = 'right'
        } else {
          line.domNode.dir = 'ltr'
          line.domNode.style.textAlign = 'left'
        }
      })
    })()

    return () => {
      mounted = false
    }
  }, [])

  /* ---------------- auth ---------------- */
  useEffect(() => {
    fetch(`${API}/api/account/me/`, { credentials: 'include' })
      .then(res => (res.ok ? res.json() : null))
      .then(setUser)
      .catch(() => setUser(null))
  }, [])

  /* ---------------- image upload ---------------- */
  async function handleImageUpload(file) {
    if (!file || !quillRef.current) return

    if (!isAuthenticated) {
      setShowAuth(true)
      return
    }

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
      const range = quillRef.current.getSelection(true)
      quillRef.current.insertEmbed(range.index, 'image', media.file)
      quillRef.current.setSelection(range.index + 1)
    } finally {
      setUploading(false)
    }
  }

  /* ---------------- submit ---------------- */
  async function handleSubmit() {
    if (!quillRef.current) {
      alert("Editor not ready yet. Please wait a moment.")
      return
    }

    if (!isAuthenticated) {
      setShowAuth(true)
      return
    }

    const content = quillRef.current.root.innerHTML.trim()
    if (!title.trim() || content === '<p><br></p>') {
      alert('Title and content are required')
      return
    }

    setPublishing(true)
    try {
      const csrfToken = getCookie('csrftoken')
      if (!csrfToken) {
        alert("CSRF token missing. Please reload the page.")
        return
      }

      const res = await fetch(`${API}/api/posts/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
          title,
          content,
          tags_list: tags
            .split(',')
            .map(t => t.trim())
            .filter(Boolean),
          status: true,
        }),
      })

      if (!res.ok) {
        const errorText = await res.text()
        throw new Error(`Server responded with ${res.status}: ${errorText}`)
      }

      const post = await res.json()
      router.push(`/blogs/${post.slug}`)
    } catch (err) {
      console.error("Error publishing post:", err)
      alert("Something went wrong while publishing. Check console for details.")
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

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              hidden
              onChange={e => handleImageUpload(e.target.files?.[0])}
            />

            {/* Scrollable editor */}
            <div className="rounded-xl overflow-hidden border border-zinc-700 bg-white text-black">
              <div
                ref={editorRef}
                className="
                  min-h-[300px] max-h-[450px] overflow-y-auto
                  [&_.ql-editor]:p-4
                  [&_.ql-editor_img]:mx-auto
                  [&_.ql-editor_img]:my-6
                  [&_.ql-editor_img]:rounded-xl
                  [&_.ql-editor_img]:max-w-[85%]
                  [&_.ql-editor_img]:shadow-md
                  [&_.ql-editor_img]:border
                  [&_.ql-editor_img]:border-zinc-300
                "
              />
            </div>

            {uploading && (
              <p className="text-sm text-zinc-400">Uploading image...</p>
            )}

            <button
              onClick={handleSubmit}
              disabled={publishing}
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
