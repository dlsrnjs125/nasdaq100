import type { DataSource, NewsArticle } from "@/lib/types";

type Props = {
  articles: NewsArticle[];
  source: DataSource;
  loading: boolean;
};

export function NewsList({ articles, source, loading }: Props) {
  return (
    <section className="rounded-lg border border-slate-800 bg-slate-800 p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-slate-100">관련 뉴스</h2>
          <p className="text-xs text-slate-500">최대 3건 표시</p>
        </div>
        <span className="rounded bg-slate-900 px-2 py-1 text-xs text-slate-400">source: {source}</span>
      </div>
      {loading ? (
        <p className="text-sm text-slate-400">뉴스 로딩 중</p>
      ) : articles.length === 0 ? (
        <p className="text-sm text-slate-400">표시할 뉴스가 없습니다.</p>
      ) : (
        <div className="space-y-3">
          {articles.map((article) => (
            <article key={article.id} className="border-b border-slate-700 pb-3 last:border-b-0 last:pb-0">
              <a
                href={article.url}
                target="_blank"
                rel="noreferrer"
                className="text-sm font-semibold text-slate-100 hover:text-blue-300"
              >
                {article.title}
              </a>
              <p className="mt-1 text-xs text-slate-500">
                {article.publisher} · {new Date(article.publishedAt).toLocaleDateString("ko-KR")}
              </p>
              {article.summary ? <p className="mt-2 text-sm text-slate-400">{article.summary}</p> : null}
            </article>
          ))}
          <a
            href={articles[0].url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex rounded-md border border-slate-700 px-3 py-2 text-xs font-semibold text-slate-300 hover:border-blue-500 hover:text-blue-300"
          >
            더보기
          </a>
        </div>
      )}
    </section>
  );
}
