export async function fetchCoach(question: string, student_answer: string, signal?: AbortSignal) {
  const res = await fetch("/api/coach", {
    method: "POST",
    body: JSON.stringify({ 
      question, 
      student_answer 
    }),
    headers: { "Content-Type": "application/json" },
    signal
  })

  if (!res.ok) {
    throw new Error(`Failed to fetch coach feedback: ${res.statusText}`)
  }

  return res.json()
}
