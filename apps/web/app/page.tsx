import Link from "next/link";

const SAMPLE_TOPICS = [
  "杭州西湖",
  "Paris architecture",
  "量子计算机",
  "人体免疫系统",
];

export default function HomePage() {
  return (
    <main className="ofb-shell relative min-h-dvh overflow-hidden text-[var(--color-ink)]">
      <div className="ofb-noise" />
      <section className="relative z-10 mx-auto grid min-h-dvh w-full max-w-7xl items-center gap-10 px-5 py-10 lg:grid-cols-[0.92fr_1.08fr] lg:px-8">
        <div className="max-w-2xl">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-black/45">
            Open Flipbook
          </p>
          <h1 className="mt-5 text-5xl font-semibold tracking-tight text-balance sm:text-6xl lg:text-7xl">
            Explore anything as a generated visual browser.
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-black/58">
            Type a topic, get a Flipbook-style page, then click any region to
            zoom into the next generated page. The backend is wired for
            DeepSeek, Qwen-VL, and SiliconFlow.
          </p>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Link
              href="/play"
              className="inline-flex items-center justify-center rounded-full bg-black px-6 py-3 text-sm font-semibold text-white shadow-[0_18px_50px_rgba(0,0,0,0.22)] transition hover:scale-[1.02] active:scale-[0.98]"
            >
              Start generating
            </Link>
            <a
              href="https://flipbook.page/"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center justify-center rounded-full border border-black/10 bg-white/62 px-6 py-3 text-sm font-semibold text-black/72 shadow-sm backdrop-blur-xl transition hover:bg-white"
            >
              Official reference
            </a>
          </div>

          <div className="mt-8 flex flex-wrap gap-2">
            {SAMPLE_TOPICS.map((topic) => (
              <Link
                key={topic}
                href={`/play?q=${encodeURIComponent(topic)}`}
                className="rounded-full border border-black/10 bg-white/52 px-3.5 py-2 text-sm font-medium text-black/62 backdrop-blur-xl transition hover:bg-white hover:text-black"
              >
                {topic}
              </Link>
            ))}
          </div>
        </div>

        <div className="relative">
          <div className="absolute -inset-8 rounded-[44px] bg-white/40 blur-3xl" />
          <div className="relative overflow-hidden rounded-[34px] border border-black/10 bg-white/70 p-2 shadow-[0_40px_120px_rgba(15,23,42,0.20)] backdrop-blur-2xl">
            <div className="flex items-center gap-2 border-b border-black/8 px-4 py-3">
              <span className="h-3 w-3 rounded-full bg-[#ff5f57]" />
              <span className="h-3 w-3 rounded-full bg-[#ffbd2e]" />
              <span className="h-3 w-3 rounded-full bg-[#28c840]" />
              <span className="ml-3 truncate rounded-full bg-black/[0.045] px-4 py-1.5 text-xs font-medium text-black/45">
                flipbook://visual-browser/paris
              </span>
            </div>
            <video
              src="/demo.mp4"
              poster="/demo-poster.jpg"
              className="aspect-video w-full rounded-[26px] object-cover"
              autoPlay
              muted
              loop
              playsInline
            />
          </div>
        </div>
      </section>
    </main>
  );
}
