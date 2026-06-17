export async function fetchFullFlow(query: string, signal?: AbortSignal) {
  const res = await fetch("/full-flow", {
    method: "POST",
    body: JSON.stringify({ query }),
    headers: { "Content-Type": "application/json" },
    signal
  })

  if (!res.ok) {
    throw new Error(`Failed to fetch full flow: ${res.statusText}`)
  }

  return res.json()
}
