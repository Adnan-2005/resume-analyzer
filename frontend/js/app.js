/* ---------- Config ----------
   Served by FastAPI on :8000 -> same origin, so API base is "/api".
   Opened from elsewhere (e.g. Live Server on :5500) -> call the backend directly. */
const API = location.port === "8000" ? "/api" : "http://localhost:8000/api";

const $ = id => document.getElementById(id);
const messagesEl = $("messages"), chatEl = $("chat"), input = $("input"), sendBtn = $("send");
let sessionId = null;
let history = [];      // [{role, content}]
let busy = false;

/* ---------- UI helpers ---------- */
function scrollDown(){ chatEl.scrollTop = chatEl.scrollHeight; }

function addMessage(role, html, opts = {}){
  $("welcome")?.remove();
  const div = document.createElement("div");
  div.className = `msg ${role}` + (opts.error ? " error" : "");
  div.innerHTML = `<div class="avatar">AI</div><div class="bubble"></div>`;
  const bubble = div.querySelector(".bubble");
  if (opts.markdown) bubble.innerHTML = DOMPurify.sanitize(marked.parse(html));
  else if (opts.raw) bubble.innerHTML = html;
  else bubble.textContent = html;
  messagesEl.appendChild(div);
  scrollDown();
  return div;
}

function showTyping(){
  return addMessage("bot", `<div class="typing"><i></i><i></i><i></i></div>`, {raw:true});
}

function setInputState(){
  const ready = !!sessionId && !busy && input.value.trim().length > 0;
  sendBtn.disabled = !ready;
  input.placeholder = sessionId ? "Ask about your resume…" : "Upload a resume to begin…";
}

function esc(s){ return String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c])); }

function showResumeCard(r, filename){
  const skills = (r.skills || []).slice(0, 8).join(", ") || "—";
  $("resumeInfo").innerHTML = `
    <div class="row"><span>File:</span> ${esc(filename)}</div>
    <div class="row"><span>Name:</span> ${esc(r.name || "—")}</div>
    <div class="row"><span>Experience:</span> ${r.total_experience_years ?? "—"} yrs</div>
    <div class="row"><span>Skills:</span> ${esc(skills)}</div>
    <div class="row"><span>Projects:</span> ${(r.projects || []).length}</div>`;
  $("resumeCard").style.display = "block";
}

function networkError(err){
  return err.message === "Failed to fetch"
    ? "Can't reach the backend. Is it running on port 8000?" : err.message;
}

/* ---------- Upload (frontend -> backend /api/upload) ---------- */
async function uploadResume(file){
  if (!file) return;
  if (!file.name.toLowerCase().endsWith(".pdf")){
    addMessage("bot", "Please upload a PDF file.", {error:true}); return;
  }
  addMessage("user", `<span class="file-chip">📄 ${esc(file.name)}</span>`, {raw:true});
  const typing = showTyping();
  busy = true; setInputState();

  const form = new FormData();
  form.append("file", file);            // field name must match FastAPI param: `file`

  try{
    const res = await fetch(`${API}/upload`, { method:"POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Upload failed");

    sessionId = data.session_id;        // remember this; /chat needs it
    history = [];
    typing.remove();
    showResumeCard(data.resume, data.filename);
    $("title").textContent = data.filename;

    const r = data.resume;
    const msg = addMessage("bot",
      `Got it! I've read **${esc(r.name || "your resume")}** — ${(r.skills||[]).length} skills, ` +
      `${(r.experiences||[]).length} experience entries and ${(r.projects||[]).length} projects found.\n\nWhat would you like to do?`,
      {markdown:true});
    const chips = document.createElement("div");
    chips.className = "chips";
    ["Analyze my resume in detail", "What are my biggest weaknesses?", "How ATS-friendly is it?",
     "Suggest better bullet points for my projects", "What roles am I best suited for?"]
      .forEach(t => {
        const b = document.createElement("button");
        b.className = "chip"; b.textContent = t;
        b.onclick = () => { chips.remove(); sendMessage(t); };
        chips.appendChild(b);
      });
    msg.querySelector(".bubble").appendChild(chips);
  }catch(err){
    typing.remove();
    addMessage("bot", networkError(err), {error:true});
  }finally{
    busy = false; setInputState();
  }
}

/* ---------- Chat (frontend -> backend /api/chat) ---------- */
async function sendMessage(text){
  text = (text ?? input.value).trim();
  if (!text || !sessionId || busy) return;

  input.value = ""; autoGrow();
  addMessage("user", text);
  const typing = showTyping();
  busy = true; setInputState();

  try{
    const res = await fetch(`${API}/chat`, {
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        question: text,
        mode: $("mode").value,
        history: history
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Request failed");

    typing.remove();
    addMessage("bot", data.answer, {markdown:true});
    history.push({role:"user", content:text}, {role:"assistant", content:data.answer});
  }catch(err){
    typing.remove();
    addMessage("bot", networkError(err), {error:true});
  }finally{
    busy = false; setInputState(); input.focus();
  }
}

/* ---------- Events ---------- */
function autoGrow(){ input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 180) + "px"; setInputState(); }
input.addEventListener("input", autoGrow);
input.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey){ e.preventDefault(); sendMessage(); } });
sendBtn.onclick = () => sendMessage();

$("attach").onclick = () => $("file").click();
$("file").onchange = e => { uploadResume(e.target.files[0]); e.target.value = ""; };

const drop = $("drop");
drop.onclick = () => $("file").click();
["dragover","dragenter"].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add("over"); }));
["dragleave","drop"].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove("over"); }));
drop.addEventListener("drop", e => uploadResume(e.dataTransfer.files[0]));

$("newChat").onclick = () => location.reload();
setInputState();
