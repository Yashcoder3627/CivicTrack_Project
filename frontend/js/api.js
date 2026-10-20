// =====================================================================
// api.js: yahan sirf backend se baat karne ka code hai.
// Har page isi file ke API.xxx() functions ko call karta hai.
// =====================================================================

// Backend ka address. Deploy karne ke baad ise live URL se badal dena.
const API_BASE = (location.hostname === "localhost" || location.hostname === "127.0.0.1")
  ? "http://127.0.0.1:8000"
  : "https://civictrack-99b8.onrender.com";

// ---------- Login ki jaankari browser mein save rakhna ----------
const Auth = {
  get token() { return localStorage.getItem("token"); },
  get role() { return localStorage.getItem("role"); },
  get name() { return localStorage.getItem("name"); },
  save(d) {
    localStorage.setItem("token", d.access_token);
    localStorage.setItem("role", d.role);
    localStorage.setItem("name", d.name || "");
  },
  clear() { ["token", "role", "name"].forEach(k => localStorage.removeItem(k)); }
};

// Login ke baad kaun sa role kaun se page par jaayega
const HOME = { citizen: "citizen.html", admin: "admin.html", officer: "officer.html" };

// Page ki suraksha (sirf dikhane ke liye; asli suraksha backend mein hoti hai).
function requireRole(...roles) {
  if (!Auth.token) { location.href = "index.html"; return false; }
  if (!roles.includes(Auth.role)) { location.href = HOME[Auth.role] || "index.html"; return false; }
  return true;
}

// ---------- Backend ko request bhejne wala helper ----------
function errorText(data) {
  if (!data) return "";
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail)) return data.detail.map(d => d.msg).join(", ");
  return "";
}

async function request(path, { method = "GET", body } = {}) {
  const isForm = body instanceof FormData;
  const headers = isForm ? {} : { "Content-Type": "application/json" };   // FormData mein browser khud type lagata hai
  if (Auth.token) headers.Authorization = "Bearer " + Auth.token;   // JWT token yahan jaata hai

  let res;
  try {
    res = await fetch(API_BASE + path, {
      method, headers, body: body ? (isForm ? body : JSON.stringify(body)) : undefined
    });
  } catch (e) {
    throw new Error("Backend se connect nahi ho paya. Kya uvicorn chal raha hai? Kya main.py mein CORS lagaya hai?");
  }
  const data = await res.json().catch(() => null);

  if (res.status === 401 && Auth.token) {          // token galat ya expire
    Auth.clear();
    location.href = "index.html";
    throw new Error("Dobara login karo.");
  }
  if (!res.ok) throw new Error(errorText(data) || "Error " + res.status);
  return data;
}

// =====================================================================
// BACKEND KE ENDPOINTS: frontend inhi 8 ko use karta hai.
// Ek endpoint bana lo, phir uska page chalake dekho.
// =====================================================================
const API = {
  // Step A: POST /auth/signup   body: {full_name, email, password}
  signup: (full_name, email, password) =>
    request("/auth/signup", { method: "POST", body: { full_name, email, password } }),

  // Step B: POST /auth/login    body: {email, password}
  //         wapas chahiye: {access_token, role, name}
  login: (email, password) =>
    request("/auth/login", { method: "POST", body: { email, password } }),

  // Step C: GET /complaints
  //         citizen ko sirf apni complaints, admin ko sabki. (token se pata chalta hai)
  complaints: () => request("/complaints"),

  // Step D: POST /complaints    body: {title, category, description, location}
    createComplaint: (formData) => request("/complaints", { method: "POST", body: formData }),

  // Step E: PATCH /complaints/{id}/status   body: {status}
  //         admin: koi bhi complaint. officer: sirf apne ko assign hui.
  updateStatus: (id, status) =>
    request(`/complaints/${id}/status`, { method: "PATCH", body: { status } }),

  // Step F: GET /officers     (sirf admin)  -> [{id, full_name, email, role}]
  officers: () => request("/officers"),

  // Step G: POST /officers    (sirf admin)  body: {full_name, email, password}
  createOfficer: (full_name, email, password) =>
    request("/officers", { method: "POST", body: { full_name, email, password } }),

  // Step H: PATCH /complaints/{id}/assign   (sirf admin)  body: {officer_id}
  assign: (id, officer_id) =>
    request(`/complaints/${id}/assign`, { method: "PATCH", body: { officer_id: Number(officer_id) } })
};

// ---------- Chhote helpers ----------
// Backend list ya {items: [...]} dono mein bheje, chalega.
function asList(data) { return Array.isArray(data) ? data : (data && data.items) || []; }

function photoUrl(name) { return name ? API_BASE + "/uploads/" + encodeURIComponent(name) : ""; }

function esc(v) {
  return String(v ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

const STATUS_CLASS = { "Pending": "pending", "In Progress": "progress", "Resolved": "resolved" };
function badge(status) {
  return `<span class="badge ${STATUS_CLASS[status] || "pending"}">${esc(status)}</span>`;
}

function fmtDate(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return isNaN(d) ? "" : d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

function showMsg(el, text, type) {
  el.textContent = text || "";
  el.className = "msg" + (text ? " " + type : "");
}

// Upar wali bar (brand + naam + role + sign out)
function renderTopbar() {
  document.getElementById("topbar").innerHTML = `
    <div class="topbar">
      <div class="brand"><div class="logo"><i></i></div>CivicTrack</div>
      <div class="topbar-right">
        <span>${esc(Auth.name)}</span>
        <span class="pill ${esc(Auth.role)}">${esc(Auth.role)}</span>
        <button class="signout" id="signout">Sign out</button>
      </div>
    </div>`;
  document.getElementById("signout").onclick = () => { Auth.clear(); location.href = "index.html"; };
}
