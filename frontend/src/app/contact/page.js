import Link from "next/link";

export default function ContactPage() {
  return (
    <section className="min-h-screen flex items-center justify-center bg-black px-6">
      <div className="max-w-3xl text-center">
        {/* Heading */}
        <h1 className="text-4xl md:text-5xl font-bold mb-6 text-sky-400">
          Get In Touch
        </h1>

        {/* Description */}
        <p className="text-zinc-300 leading-relaxed mb-10">
          If you want to work with me, collaborate on a project, or just have a
          conversation about development, feel free to reach out.
          <br />
          <br />
          The best way to contact me is through my social media accounts.
          Send me a message and we can schedule a meeting or continue the
          discussion there.
        </p>

        {/* Social Links */}
        <div className="flex justify-center gap-6 text-2xl mb-12">
          <Link
            href="https://facebook.com/"
            target="_blank"
            className="text-zinc-400 hover:text-sky-400 transition"
          >
            <i className="fa-brands fa-facebook-f" />
          </Link>

          <Link
            href="https://twitter.com/"
            target="_blank"
            className="text-zinc-400 hover:text-sky-400 transition"
          >
            <i className="fa-brands fa-twitter" />
          </Link>

          <Link
            href="https://instagram.com/"
            target="_blank"
            className="text-zinc-400 hover:text-sky-400 transition"
          >
            <i className="fa-brands fa-instagram" />
          </Link>

          <Link
            href="https://linkedin.com/"
            target="_blank"
            className="text-zinc-400 hover:text-sky-400 transition"
          >
            <i className="fa-brands fa-linkedin-in" />
          </Link>
        </div>

        {/* Optional CTA */}
        <p className="text-sm text-zinc-500">
          I usually respond within 24–48 hours.
        </p>
      </div>
    </section>
  );
}
