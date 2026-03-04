// main.js – shared utilities for Face Attendance System

// CSRF token helper for AJAX POST requests
function getCsrfToken() {
  const el = document.querySelector("[name=csrfmiddlewaretoken]");
  if (el) return el.value;
  const cookie = document.cookie
    .split(";")
    .find((c) => c.trim().startsWith("csrftoken="));
  return cookie ? cookie.split("=")[1] : "";
}

// Generic POST helper
async function postJSON(url, data = {}) {
  const resp = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
    body: JSON.stringify(data),
  });
  return resp.json();
}

// Auto-hide flash messages after 4 seconds
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".alert").forEach((el) => {
    setTimeout(() => {
      el.style.transition = "opacity 0.6s";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 700);
    }, 4000);
  });
});
