import { Link } from "react-router-dom";
import WorkspacePage from "../components/WorkspacePage.jsx";

const posts = [
  {date:"28.09.2026", tag:"BUILD LOG", title:"Как мы собираем BOOK-CRAFT: от каркаса к визуальному проходу", text:"Почему сначала фиксируем геометрию, маршруты и состояния, а уже потом добавляем арт."},
  {date:"28.09.2026", tag:"AI CONTENT", title:"Одна идея — несколько форматов", text:"Как один замысел превращается в рассылку, подкаст, видео и визуальный контент."},
  {date:"28.09.2026", tag:"ARCHITECTURE", title:"Почему интерфейс не запекается в картинки", text:"UI остаётся React-компонентами, а визуальные ассеты подключаются как сменные слои."},
];

export default function BlogPage() {
  return (
    <WorkspacePage
      eyebrow="✦ CONTENT"
      title="Блог"
      description="Редакционный раздел BOOK-CRAFT: заметки о продукте, AI-контенте, архитектуре и ходе разработки."
      status="EDITORIAL DEMO"
    >
      <div className="blogLeadCard">
        <small>EDITOR'S NOTE</small>
        <h2>Строим AI-студию как продукт, а не как набор разрозненных генераторов.</h2>
        <p>Все текущие материалы — демонстрационный контент для проверки структуры раздела.</p>
      </div>

      <div className="blogGrid">
        {posts.map((post) => (
          <article key={post.title} className="blogCard">
            <div><small>{post.tag}</small><span>{post.date}</span></div>
            <h3>{post.title}</h3>
            <p>{post.text}</p>
            <Link to="/create">Перейти в продукт →</Link>
          </article>
        ))}
      </div>
    </WorkspacePage>
  );
}
