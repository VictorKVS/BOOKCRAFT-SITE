const FATHER_URL =
  import.meta.env.VITE_FATHER_URL ??
  "http://127.0.0.1:8010";

async function request(path, options = {}) {
  const response = await fetch(
    `${FATHER_URL}${path}`,
    options,
  );

  if (!response.ok) {
    let detail = "";

    try {
      const data = await response.json();
      detail = data?.detail ?? "";
    } catch {
      detail = await response.text();
    }

    throw new Error(
      detail ||
      `FATHER request failed: ${response.status}`,
    );
  }

  return response.json();
}

export async function getFatherHealth() {
  return request("/api/father/health");
}

export async function fatherChat(message) {
  return request(
    "/api/father/chat",
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json; charset=utf-8",
      },
      body: JSON.stringify({
        agent: "alina",
        message,
      }),
    },
  );
}

export async function fatherAnalyzeImage(
  file,
  prompt,
) {
  const form = new FormData();

  form.append(
    "image",
    file,
    file.name || "image.png",
  );

  form.append(
    "prompt",
    prompt ||
      "Проанализируй изображение подробно. Не придумывай невидимые детали.",
  );

  return request(
    "/api/father/analyze-image",
    {
      method: "POST",
      body: form,
    },
  );
}

export { FATHER_URL };

export async function getFatherRuntimeInfo() {
  return request("/api/father/runtime-info");
}

export async function fatherSpeak(text) {
  return request("/api/father/speak", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });
}

export async function fatherChatStream(
  message,
  {
    provider = "auto",
    profile = "fast",
    onToken,
    onMeta,
    onFallback,
  } = {},
) {
  const response = await fetch(
    `${FATHER_URL}/api/father/chat-stream`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        agent: "alina",
        message,
        provider,
        profile,
      }),
    },
  );

  if (!response.ok) {
    const text = await response.text();

    throw new Error(
      `FATHER ${response.status}: ${text}`
    );
  }

  if (!response.body) {
    throw new Error(
      "Streaming response body is unavailable."
    );
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");

  let buffer = "";
  let answer = "";
  let finalMeta = null;

  while (true) {
    const { value, done } =
      await reader.read();

    if (done) break;

    buffer += decoder.decode(
      value,
      { stream: true },
    );

    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      const trimmed = line.trim();

      if (!trimmed) continue;

      let event;

      try {
        event = JSON.parse(trimmed);
      } catch {
        continue;
      }

      if (event.type === "meta") {
        onMeta?.(event);
        continue;
      }

      if (event.type === "fallback") {
        onFallback?.(event);
        continue;
      }

      if (event.type === "token") {
        answer += event.content || "";
        onToken?.(
          event.content || "",
          answer,
        );
        continue;
      }

      if (event.type === "done") {
        finalMeta = event;
        onMeta?.(event);
        continue;
      }

      if (event.type === "error") {
        throw new Error(
          event.message || "Streaming error"
        );
      }
    }
  }

  return {
    answer,
    ...(finalMeta || {}),
  };
}
