export async function askEduBot(message) {
  const res = await fetch("https://chat-bot-1-22ke.onrender.com/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });
  return res.json();
}