import Link from "next/link";

export default function Post({
  title,
  author,
  tags_list,
  likes,
  created_at,
  slug,
}) {
  // ---------- Safe derived values ----------
  const tags = typeof tags_list === "string"
    ? tags_list.split(",").map(t => t.trim()).filter(Boolean)
    : [];

  const authorName =
    author?.username ||
    author?.email ||
    "Anonymous";

  const date = created_at
    ? new Date(created_at).toLocaleDateString()
    : null;

  const likeCount =
    typeof likes === "number" ? likes : 0;

  return (
    <article className="bg-zinc-900 border border-zinc-800 p-6 rounded-lg hover:border-sky-400 transition">

      {/* Tags */}
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {tags.map((tag) => (
            <span
              key={tag}
              className="text-xs uppercase tracking-wider text-sky-400 border border-sky-400/40 px-2 py-1 rounded"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Title */}
      <h3 className="text-xl font-semibold leading-snug mb-3 hover:text-sky-400 transition">
        {title || "Untitled Post"}
      </h3>

      {/* Meta */}
      {(authorName || date) && (
        <div className="text-sm text-zinc-400 mb-4">
          <span>{authorName}</span>
          {date && <> · <span>{date}</span></>}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between text-sm text-zinc-400">
        <span className="flex items-center gap-1">
          <i className="fa-regular fa-heart" />
          {likeCount}
        </span>

        <Link
          href={`/blogs/${slug}`}
          className="text-sky-400 hover:underline"
        >
          Continue Reading →
        </Link>
      </div>
    </article>
  );
}
