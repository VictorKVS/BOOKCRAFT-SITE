import WorkspacePage from "./WorkspacePage.jsx";

export default function PlaceholderPage({ eyebrow, title, description, children }) {
  return (
    <WorkspacePage eyebrow={eyebrow} title={title} description={description}>
      <div className="placeholderModule">
        {children ?? (
          <>
            <b>КАРКАС ГОТОВ</b>
            <span>Сюда подключим реальное содержимое следующим этапом.</span>
          </>
        )}
      </div>
    </WorkspacePage>
  );
}
