import Image from "next/image";
import Link from "next/link";


export default function AboutPage() {
    return(
        <section className="bg-black py-24">
                <div className="max-w-4xl mx-auto px-6">
                    {/* Header */}
                    <div className="text-center mb-16">
                    <div className="mx-auto mb-6 w-32 h-32 rounded-full overflow-hidden">
                        <Image
                        src="/author.jpg"
                        alt="Mojtaba"
                        width={128}
                        height={128}
                        priority
                        />
                    </div>

                    <h2 className="text-sm tracking-widest text-sky-400 uppercase mb-2">
                        About Me
                    </h2>

                    <h1 className="text-4xl font-bold mb-6">
                        Mojtaba
                    </h1>
                    </div>

                    {/* Content */}
                    <div className="space-y-6 text-zinc-300 leading-relaxed text-lg">
                    <p>
                        I’m a web developer and blogger with a strong interest in building
                        clean, structured, and maintainable systems. I enjoy working on projects
                        that have a clear purpose and tangible results.
                    </p>

                    <p>
                        My background in trading and data analysis shaped the way I think about
                        problem-solving — I prefer logical workflows, measurable outcomes, and
                        well-defined constraints over vague or overly creative approaches.
                    </p>

                    <p>
                        Most of my work focuses on backend logic, automation, and data-driven
                        features, but I also care deeply about clean UI and user experience when
                        it serves a functional goal.
                    </p>

                    <p>
                        Outside of coding, I enjoy writing, breaking down complex ideas, and
                        building tools that make everyday tasks more efficient.
                    </p>
                    </div>

                    {/* CTA */}
                    <div className="mt-16 text-center">
                    <Link
                        href="/contact"
                        className="inline-flex items-center gap-2 border border-sky-400 px-8 py-3 text-sky-400 hover:bg-sky-400 hover:text-black transition"
                    >
                        Get in touch →
                    </Link>
                    </div>
                </div>
        </section>

    )
}