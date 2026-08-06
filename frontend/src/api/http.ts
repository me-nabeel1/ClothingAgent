export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly code?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function requestJson<T>(
  url: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  const body = await response.json().catch(() => null) as
    | { error?: { code?: string; message?: string }; detail?: unknown }
    | T
    | null;

  if (!response.ok) {
    const envelope = body as { error?: { code?: string; message?: string }; detail?: unknown } | null;
    const detail = typeof envelope?.detail === "string"
      ? envelope.detail
      : envelope?.error?.message;
    throw new ApiError(
      detail ?? `Request failed with status ${response.status}.`,
      response.status,
      envelope?.error?.code,
    );
  }

  return body as T;
}
