// static/js/main.js
const dropzone = document.getElementById("dropzone");
const fileinput = document.getElementById("fileinput");
const uploadBtn = document.getElementById("uploadBtn");
const preview = document.getElementById("preview");
const targetInput = document.getElementById("target_dir");
const dirList = document.getElementById("dirList");
const refreshDirs = document.getElementById("refreshDirs");
const organizeBtn = document.getElementById("organizeBtn");
const dryRun = document.getElementById("dryRun");
const out = document.getElementById("out");

let filesToUpload = [];

function renderPreview(){
  preview.innerHTML = "";
  filesToUpload.forEach(f=>{
    const chip = document.createElement("div");
    chip.className = "chip";
    chip.textContent = `${f.name}`;
    preview.appendChild(chip);
  });
}

dropzone.addEventListener("click", ()=> fileinput.click());
dropzone.addEventListener("dragover", e => { e.preventDefault(); dropzone.style.borderColor="#6ee7b7"; });
dropzone.addEventListener("dragleave", e => { dropzone.style.borderColor=""; });
dropzone.addEventListener("drop", e => {
  e.preventDefault();
  dropzone.style.borderColor="";
  const dt = e.dataTransfer;
  for(const f of dt.files) filesToUpload.push(f);
  renderPreview();
});

fileinput.addEventListener("change", ()=> {
  for(const f of fileinput.files) filesToUpload.push(f);
  renderPreview();
});

uploadBtn.addEventListener("click", async ()=>{
  if(filesToUpload.length===0){ alert("Choose files first"); return; }
  const form = new FormData();
  filesToUpload.forEach(f => form.append("files[]", f));
  const target = targetInput.value.trim();
  if(target) form.append("target_dir", target);
  uploadBtn.disabled = true;
  uploadBtn.textContent = "Uploading...";
  try{
    const res = await fetch("/api/upload", { method:"POST", body: form });
    const j = await res.json();
    if(!res.ok){ alert(j.error || "Upload failed"); }
    else {
      filesToUpload = [];
      renderPreview();
      await refreshDirectoryList();
      showOutput("Upload saved: " + JSON.stringify(j.saved, null, 2));
    }
  }catch(e){
    alert("Upload error");
  }finally{
    uploadBtn.disabled = false;
    uploadBtn.textContent = "Upload";
  }
});

async function refreshDirectoryList(){
  const res = await fetch("/api/list_dirs");
  const j = await res.json();
  dirList.innerHTML = "";
  j.dirs.forEach(d=>{
    const el = document.createElement("div");
    el.className = "dir-item";
    el.textContent = d;
    el.addEventListener("click", ()=> {
      document.querySelectorAll(".dir-item").forEach(x=>x.classList.remove("selected"));
      el.classList.add("selected");
      targetInput.value = d;
    });
    dirList.appendChild(el);
  });
}

refreshDirs.addEventListener("click", refreshDirectoryList);
window.addEventListener("load", refreshDirectoryList);

organizeBtn.addEventListener("click", async ()=>{
  const selected = document.querySelector(".dir-item.selected");
  const source = selected ? selected.textContent : "";
  const payload = { source, dry: dryRun.checked };
  organizeBtn.disabled = true;
  organizeBtn.textContent = "Organizing...";
  try{
    const res = await fetch("/api/organize", {
      method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(payload)
    });
    const j = await res.json();
    showOutput(JSON.stringify(j, null, 2));
    await refreshDirectoryList();
  }catch(e){
    showOutput("Error organizing");
  }finally{
    organizeBtn.disabled = false;
    organizeBtn.textContent = "Organize Selected";
  }
});

function showOutput(text){
  out.hidden = false;
  out.textContent = text;
}