export async function fetchNavigator(query: string, signal?: AbortSignal) {
  const res = await fetch("/navigator", {
    method: "POST",
    body: JSON.stringify({ query }),
    headers: { "Content-Type": "application/json" },
    signal
  })

  if (!res.ok) {
    throw new Error(`Failed to fetch navigator data: ${res.statusText}`)
  }

  return res.json()
}
