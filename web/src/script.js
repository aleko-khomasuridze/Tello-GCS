const videoEl = document.getElementById("video");

const connPill = document.getElementById("connPill");
const fpsPill = document.getElementById("fpsPill");

const btnConnect = document.getElementById("btnConnect");
const btnDisconnect = document.getElementById("btnDisconnect");
const btnTakeoff = document.getElementById("btnTakeoff");
const btnLand = document.getElementById("btnLand");
const btnEmergency = document.getElementById("btnEmergency");

const rcRoll = document.getElementById("rcRoll");
const rcPitch = document.getElementById("rcPitch");
const rcThrottle = document.getElementById("rcThrottle");
const rcYaw = document.getElementById("rcYaw");
const btnSendRC = document.getElementById("btnSendRC");
const btnCenterRC = document.getElementById("btnCenterRC");

const tBattery = document.getElementById("tBattery");
const tHeight = document.getElementById("tHeight");
const tTime = document.getElementById("tTime");
const tWifi = document.getElementById("tWifi");
const tSx = document.getElementById("tSx");
const tSy = document.getElementById("tSy");
const tSz = document.getElementById("tSz");
const tTemp = document.getElementById("tTemp");

// FPS counter
let lastFrameTs = performance.now();
let fps = 0;
let fpsSmooth = 0;

function setConnected(isConn){
  connPill.textContent = isConn ? "CONNECTED" : "DISCONNECTED";
  connPill.classList.toggle("ok", isConn);
  connPill.classList.toggle("bad", !isConn);
}

btnConnect.onclick = async () => {
  const res = await eel.ui_connect()();
  if(!res.ok) alert(res.error || "Connect failed");
};

btnDisconnect.onclick = async () => {
  await eel.ui_disconnect()();
  setConnected(false);
};

btnTakeoff.onclick = async () => {
  const res = await eel.ui_takeoff()();
  if(!res.ok) alert(res.error || "Takeoff failed");
};

btnLand.onclick = async () => {
  const res = await eel.ui_land()();
  if(!res.ok) alert(res.error || "Land failed");
};

btnEmergency.onclick = async () => {
  const res = await eel.ui_emergency()();
  if(!res.ok) alert(res.error || "Emergency failed");
};

btnSendRC.onclick = async () => {
  await sendRC();
};

btnCenterRC.onclick = () => {
  rcRoll.value = 0; rcPitch.value = 0; rcThrottle.value = 0; rcYaw.value = 0;
};

async function sendRC(){
  const lr = parseInt(rcRoll.value, 10);
  const fb = parseInt(rcPitch.value, 10);
  const ud = parseInt(rcThrottle.value, 10);
  const yw = parseInt(rcYaw.value, 10);
  await eel.ui_rc(lr, fb, ud, yw)();
}

// Keyboard control (hold keys -> updates sliders -> send RC)
const keys = new Set();
const STEP = 40; // feel free to tune: 20-60 is typical

function clamp(v){ return Math.max(-100, Math.min(100, v)); }

function tickKeys(){
  let lr = 0, fb = 0, ud = 0, yw = 0;

  if(keys.has("a")) lr -= STEP;
  if(keys.has("d")) lr += STEP;

  if(keys.has("w")) fb += STEP;
  if(keys.has("s")) fb -= STEP;

  if(keys.has("r")) ud += STEP;
  if(keys.has("f")) ud -= STEP;

  if(keys.has("q")) yw -= STEP;
  if(keys.has("e")) yw += STEP;

  // Arrow keys alternate scheme
  if(keys.has("ArrowLeft"))  yw -= STEP;
  if(keys.has("ArrowRight")) yw += STEP;
  if(keys.has("ArrowUp"))    ud += STEP;
  if(keys.has("ArrowDown"))  ud -= STEP;

  // Update sliders (visual feedback)
  rcRoll.value = clamp(lr);
  rcPitch.value = clamp(fb);
  rcThrottle.value = clamp(ud);
  rcYaw.value = clamp(yw);

  // Send continuously while keys are held
  if(keys.size > 0){
    sendRC();
  }

  requestAnimationFrame(tickKeys);
}

window.addEventListener("keydown", (e) => {
  // prevent scrolling with arrows/space
  if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"," "].includes(e.key)) e.preventDefault();
  keys.add(e.key.toLowerCase());
});

window.addEventListener("keyup", (e) => {
  keys.delete(e.key.toLowerCase());
  // When released, center controls and send neutral
  if(keys.size === 0){
    rcRoll.value = 0; rcPitch.value = 0; rcThrottle.value = 0; rcYaw.value = 0;
    sendRC();
  }
});

requestAnimationFrame(tickKeys);

// ----------------------
// Eel callbacks (Python -> UI)
// ----------------------
eel.expose(updateFrame);
function updateFrame(dataUrl){
  videoEl.src = dataUrl;

  const now = performance.now();
  const dt = now - lastFrameTs;
  lastFrameTs = now;
  fps = 1000 / Math.max(dt, 1);
  fpsSmooth = fpsSmooth * 0.9 + fps * 0.1;
  fpsPill.textContent = `FPS: ${fpsSmooth.toFixed(0)}`;
}

eel.expose(updateTelemetry);
function updateTelemetry(t){
  setConnected(!!t.connected);

  tBattery.textContent = (t.battery ?? "--") + (t.battery != null ? "%" : "");
  tHeight.textContent = (t.height_cm ?? "--") + (t.height_cm != null ? " cm" : "");
  tTime.textContent = (t.flight_time_s ?? "--") + (t.flight_time_s != null ? " s" : "");
  tWifi.textContent = (t.wifi_strength ?? "--");

  tSx.textContent = (t.speed_x ?? "--");
  tSy.textContent = (t.speed_y ?? "--");
  tSz.textContent = (t.speed_z ?? "--");

  const tl = t.temp_low;
  const th = t.temp_high;
  tTemp.textContent = (tl != null && th != null) ? `${tl}..${th}°C` : "--";
}


eel.expose(updateJoystick);
function updateJoystick(s){
  const nameEl = document.getElementById("jsName");
  const stateEl = document.getElementById("jsState");
  if(!nameEl || !stateEl) return;
  nameEl.textContent = s.name ?? "No device";
  stateEl.textContent = s.state ?? "--";
}
