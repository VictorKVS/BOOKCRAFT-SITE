import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import WorkspacePage from "../components/WorkspacePage.jsx";

const index = [
  ["/create","Create Hub","создание модули инструменты"],
  ["/mailing","Рассылка","newsletter письма кампании"],
  ["/podcast","Подкаст","audio tts сценарий"],
  ["/video-avatar","Видео-Аватар","voice avatar external api"],
  ["/images","Изображения","comfyui image generation"],
  ["/books","Книги","главы сюжет персонажи"],
  ["/scripts","Сценарии клипов","storyboard сцены кадры"],
  ["/analytics","Аналитика","trend metrics recommendation"],
];

export default function SearchPage() {
  const [q, setQ] = useState("");

  const results = useMemo(() => {
    const needle = q.trim().toLowerCase();
    if (!needle) return index;
    return index.filter(([,title,keywords]) => `${title} ${keywords}`.toLowerCase().includes(needle));
  }, [q]);

  return (
    <WorkspacePage
      eyebrow="✦ SEARCH"
      title="Поиск"
      description="На этапе каркаса поиск работает по разделам продукта. Поиск по знаниям подключим позже."
      status="LOCAL INDEX"
    >
      <label className="field">
        <span>Найти раздел</span>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Например: подкаст, книги, аналитика..." autoFocus />
      </label>

      <div className="searchResults">
        {results.map(([to,title]) => (
          <Link key={to} to={to} className="searchResult spectralSurface">
            <b>{title}</b><span>{to}</span><i>→</i>
          </Link>
        ))}
        {!results.length && <div className="resultPlaceholder">Ничего не найдено</div>}
      </div>
    </WorkspacePage>
  );
}
