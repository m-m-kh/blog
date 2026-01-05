"use client";

import dynamic from "next/dynamic";
import "react-quill/dist/quill.snow.css";

// IMPORTANT: load without SSR
const ReactQuill = dynamic(() => import("react-quill"), {
  ssr: false,
});

export default function QuillEditor({ value, onChange }) {
  return (
    <ReactQuill
      theme="snow"
      value={value}
      onChange={onChange}
      placeholder="Write your blog here..."
    />
  );
}
