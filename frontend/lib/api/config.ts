// API 설정
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000",
  USE_MOCK: process.env.NEXT_PUBLIC_USE_MOCK === "true",
} as const;

// Health check (개발용)
export async function checkApiHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_CONFIG.BASE_URL}/health`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    const json = await res.json();
    return json.success === true && json.data?.status === "ok";
  } catch {
    return false;
  }
}
