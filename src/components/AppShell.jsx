import { NavLink, Outlet } from "react-router-dom";
import { useState } from "react";
import SpectralAction from "./SpectralAction.jsx";

const nav = [
  ["/features", "Возможности"],
  ["/examples", "Примеры"],
  ["/pricing", "Тарифы"],
  ["/blog", "Блог"],
  ["/studio", "О студии"],
];

export default function AppShell() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="app">
      <header className="topbar">
        <NavLink to="/" className="brand" aria-label="BOOK-CRAFT — главная">
          <span className="brandMark">✦</span>
          <span className="brandText">
            <strong>BOOK-CRAFT</strong>
            <small>NARRATIVE AI STUDIO</small>
          </span>
        </NavLink>

        <nav className="topnav" aria-label="Основная навигация">
          {nav.map(([to, label]) => (
            <NavLink key={to} to={to} className={({isActive}) => isActive ? "active" : ""}>
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="headerRight">
          <NavLink className="searchButton" to="/search" aria-label="Поиск">⌕</NavLink>

          <SpectralAction to="/analytics" variant="analytics" className="analyticsButton">
            <span className="analyticsGlyph">◈</span>
            <span>Аналитика</span>
            <small>DEMO</small>
          </SpectralAction>

          <NavLink className="loginLink" to="/login">Войти</NavLink>

          <SpectralAction to="/create" variant="light" className="startButton">
            Начать бесплатно →
          </SpectralAction>

          <button
            className="mobileMenuButton"
            type="button"
            aria-label="Открыть меню"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((v) => !v)}
          >
            ☰
          </button>
        </div>
      </header>

      {menuOpen && (
        <nav className="mobileMenu" aria-label="Мобильное меню">
          {nav.map(([to, label]) => (
            <NavLink key={to} to={to} onClick={() => setMenuOpen(false)}>{label}</NavLink>
          ))}
          <NavLink to="/analytics" onClick={() => setMenuOpen(false)}>◈ Аналитика</NavLink>
          <NavLink to="/login" onClick={() => setMenuOpen(false)}>Войти</NavLink>
          <NavLink to="/create" onClick={() => setMenuOpen(false)}>Начать бесплатно →</NavLink>
        </nav>
      )}

      <main className="pageWrap">
        <Outlet />
      </main>
    </div>
  );
}
