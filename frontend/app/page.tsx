import Link from "next/link";

const FEATURES = [
  {
    icon: "📋",
    title: "오늘의 브리핑",
    desc: "관심기업의 최신 뉴스와 채용 공고를 매일 아침 한 곳에서 확인하세요.",
  },
  {
    icon: "⭐",
    title: "관심기업 등록",
    desc: "대기업·중견기업·공기업 중 최대 5개 기업을 골라 팔로우하세요.",
  },
  {
    icon: "🎯",
    title: "준비 카드",
    desc: "인재상·채용 동향·자소서·면접 포인트를 기업별로 정리해 드립니다.",
  },
];

export default function HomePage() {
  return (
    <div className="space-y-8">
      {/* 히어로 */}
      <section className="rounded-xl bg-white border border-gray-200 px-6 py-10 text-center">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-xs font-medium text-blue-700 mb-4">
          Phase 0 · Mock Data
        </div>
        <h1 className="text-2xl font-bold text-gray-900 leading-tight">
          취업 준비, 매일 아침
          <br />
          <span className="text-blue-600">관심기업 브리핑</span>으로 시작하세요
        </h1>
        <p className="mt-3 text-sm text-gray-500 max-w-sm mx-auto leading-relaxed">
          뉴스·채용 공고·기업 준비 카드를 한 화면에서.
          <br />
          취업 준비생을 위한 맞춤형 정보 서비스입니다.
        </p>

        <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            href="/briefings/today"
            className="w-full sm:w-auto px-5 py-2.5 rounded-lg bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 transition-colors text-center"
          >
            오늘의 브리핑 보기
          </Link>
          <Link
            href="/subscriptions"
            className="w-full sm:w-auto px-5 py-2.5 rounded-lg bg-white border border-gray-200 text-gray-700 text-sm font-semibold hover:border-gray-400 transition-colors text-center"
          >
            관심기업 관리
          </Link>
        </div>
      </section>

      {/* 핵심 가치 */}
      <section>
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
          핵심 기능
        </h2>
        <div className="space-y-3">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="flex items-start gap-4 rounded-lg bg-white border border-gray-200 px-4 py-4"
            >
              <span className="text-2xl flex-shrink-0">{f.icon}</span>
              <div>
                <p className="text-sm font-semibold text-gray-900">{f.title}</p>
                <p className="mt-0.5 text-sm text-gray-500 leading-relaxed">{f.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 안내 */}
      <div className="rounded-lg bg-amber-50 border border-amber-200 px-4 py-3">
        <p className="text-xs text-amber-700 leading-relaxed">
          <strong>Phase 0 데모</strong> · 현재는 mock 데이터로 동작합니다. 
          실제 뉴스·채용 수집 기능은 Phase 1에서 연결됩니다.
        </p>
      </div>
    </div>
  );
}
