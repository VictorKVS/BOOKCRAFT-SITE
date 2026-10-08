const DEFAULT_FATHER_URL =
  "http://127.0.0.1:8010";

export const FATHER_URL =
  import.meta.env.VITE_FATHER_URL ??
  DEFAULT_FATHER_URL;

function createTraceId() {
  if (
    globalThis.crypto &&
    typeof globalThis.crypto.randomUUID === "function"
  ) {
    return globalThis.crypto.randomUUID();
  }

  return [
    Date.now().toString(16),
    Math.random()
      .toString(16)
      .slice(2),
  ].join("-");
}

async function readError(response) {
  try {
    const data = await response.json();

    if (typeof data?.detail === "string") {
      return data.detail;
    }

    return JSON.stringify(data);
  } catch {
    return (
      `${response.status} `
      + response.statusText
    );
  }
}

export async function fatherGenerateImage(
  prompt,
  width = 768,
  height = 768
) {
  const traceId = createTraceId();

  console.info(
    `[FATHER TRACE ${traceId}]`,
    "image.request",
    {
      width,
      height,
      promptChars: prompt.length,
    }
  );

  const response = await fetch(
    `${FATHER_URL}/api/father/image`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json; charset=utf-8",

        "X-Trace-ID":
          traceId,
      },

      body: JSON.stringify({
        prompt,
        width,
        height,
      }),
    }
  );

  if (!response.ok) {
    const message =
      await readError(response);

    console.error(
      `[FATHER TRACE ${traceId}]`,
      "image.error",
      message
    );

    throw new Error(
      `[TRACE ${traceId}] ${message}`
    );
  }

  const data =
    await response.json();

  const finalTraceId =
    data.trace_id ||
    traceId;

  console.info(
    `[FATHER TRACE ${finalTraceId}]`,
    "image.completed",
    {
      provider: data.provider,
      checkpoint: data.checkpoint,
      promptId: data.prompt_id,
      url: data.url,
    }
  );

  return {
    ...data,
    trace_id: finalTraceId,
  };
}
