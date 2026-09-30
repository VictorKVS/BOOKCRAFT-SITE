import { useEffect, useMemo, useState } from "react";

function getEnabledItems(config) {
  if (!config?.enabled || !Array.isArray(config.items)) {
    return [];
  }

  return config.items.filter(
    (item) => item?.enabled !== false && item?.asset
  );
}

function getNextIndex(current, length, mode) {
  if (length <= 1) return 0;

  if (mode === "random") {
    let next = current;

    while (next === current) {
      next = Math.floor(Math.random() * length);
    }

    return next;
  }

  return (current + 1) % length;
}

export function useRotatingAsset(config) {
  const items = useMemo(() => getEnabledItems(config), [config]);

  const requestedStartIndex = Number.isInteger(config?.startIndex)
    ? config.startIndex
    : 0;

  const safeStartIndex =
    items.length > 0
      ? Math.min(Math.max(requestedStartIndex, 0), items.length - 1)
      : 0;

  const [index, setIndex] = useState(safeStartIndex);

  useEffect(() => {
    setIndex((current) =>
      items.length === 0 ? 0 : Math.min(current, items.length - 1)
    );
  }, [items.length]);

  useEffect(() => {
    if (items.length <= 1) return undefined;

    const mediaQuery = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    );

    if (mediaQuery.matches) return undefined;

    const intervalMs = Math.max(
      Number(config?.intervalMs) || 8000,
      1000
    );

    const timer = window.setInterval(() => {
      setIndex((current) =>
        getNextIndex(current, items.length, config?.mode)
      );
    }, intervalMs);

    return () => window.clearInterval(timer);
  }, [items.length, config?.intervalMs, config?.mode]);

  useEffect(() => {
    if (items.length <= 1) return;

    const nextIndex = getNextIndex(
      index,
      items.length,
      config?.mode === "random" ? "sequence" : config?.mode
    );

    const next = items[nextIndex];

    if (!next?.asset) return;

    const image = new Image();
    image.src = next.asset;
  }, [index, items, config?.mode]);

  return {
    item: items[index] ?? null,
    index,
    count: items.length,
  };
}

export default useRotatingAsset;