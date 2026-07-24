import type { DataSource, NewsArticle } from "@/lib/types";

type Props = {
  articles: NewsArticle[];
  source: DataSource;
  loading: boolean;
};

export function NewsList({ articles, source, loading }: Props) {
  return (
    <section className="rounded-[28px] border border-[#bfc9c3]/30 bg-white p-6 shadow-sm transition duration-300 hover:-translate-y-0.5 hover:shadow-md md:p-8">
      <div className="mb-8 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#dde1d5] text-[#003527]">
            <span className="material-symbols-outlined">newspaper</span>
          </div>
          <h3 className="text-2xl font-semibold text-[#003527]">관련 뉴스</h3>
        </div>
        <span className="rounded-lg bg-[#eff4ff] px-2 py-1 text-xs font-bold text-[#404944]">source: {source}</span>
      </div>
      {loading ? (
        <p className="text-sm font-semibold text-[#404944]">뉴스 로딩 중</p>
      ) : articles.length === 0 ? (
        <p className="text-sm font-semibold text-[#404944]">표시할 뉴스가 없습니다.</p>
      ) : (
        <div>
          {articles.map((article) => (
            <article
              key={article.id}
              className="group flex cursor-pointer items-center justify-between rounded-2xl border-b border-[#bfc9c3]/20 p-5 transition-colors last:border-0 hover:bg-[#eff4ff]"
            >
              <div>
                <a
                  href={article.url}
                  target="_blank"
                  rel="noreferrer"
                  className="mb-1 block text-sm font-semibold text-[#121c2a] transition-colors group-hover:text-[#003527]"
                >
                  {article.title}
                </a>
                <p className="flex items-center gap-2 text-xs font-bold text-[#404944]">
                  <span>{article.publisher}</span>
                  <span className="h-1 w-1 rounded-full bg-[#bfc9c3]" />
                  <span>{new Date(article.publishedAt).toLocaleDateString("ko-KR").replace(/\\. /g, ".")}</span>
                </p>
              </div>
              <span className="material-symbols-outlined text-[#bfc9c3] transition-colors group-hover:text-[#003527]">
                chevron_right
              </span>
            </article>
          ))}
          <a
            href={articles[0].url}
            target="_blank"
            rel="noreferrer"
            className="mt-6 flex w-full items-center justify-center gap-2 py-3 text-sm font-semibold text-[#404944] transition-colors hover:text-[#003527]"
          >
            더보기 <span className="material-symbols-outlined text-sm">expand_more</span>
          </a>
        </div>
      )}
    </section>
  );
}
