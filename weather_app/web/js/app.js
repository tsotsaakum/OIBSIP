const $ = (id) => document.getElementById(id);

let unit = "C";
let lastBundle = null;

const cToF = (c) => c * 9 / 5 + 32;
const deg = (c) => `${Math.round(unit === "F" ? cToF(c) : c)}°`;
const wind = (mps) => (unit === "F" ? `${Math.round(mps * 2.23694)} mph` : `${mps.toFixed(1)} m/s`);
const uvWord = (i) => (i < 3 ? "low" : i < 6 ? "moderate" : i < 8 ? "high" : "very high");
const iconUrl = (code) => `https://openweathermap.org/img/wn/${code}@2x.png`;

function clock(epoch, offset) {
  if (!epoch) return "—";
  return new Date((epoch + (offset || 0)) * 1000).toLocaleTimeString([], {
    hour: "numeric",
    minute: "2-digit",
    timeZone: "UTC",
  });
}

function hourLabel(epoch, offset, index) {
  if (index === 0) return "Now";
  return new Date((epoch + (offset || 0)) * 1000).toLocaleTimeString([], {
    hour: "numeric",
    hour12: true,
    timeZone: "UTC",
  });
}

function skyPhase(c) {
  const now = Date.now() / 1000;
  const rise = Number(c.sunrise_epoch) || 0;
  const set = Number(c.sunset_epoch) || 0;
  if (!rise || !set) return "day";
  if (now < rise || now >= set) return "night";
  if (now < rise + 3 * 3600) return "morning";
  if (now >= set - 1.5 * 3600) return "dusk";
  return "day";
}

function applyLight(c) {
  const phase = skyPhase(c);
  document.documentElement.dataset.phase = phase;
  const labels = {
    morning: "Morning light — after sunrise",
    day: "Daylight",
    dusk: "Evening light — toward sunset",
    night: "Night — after sunset",
  };
  document.body.dataset.light = labels[phase];
}

function lineFor(c) {
  const rise = clock(c.sunrise_epoch, c.timezone_offset);
  const set = clock(c.sunset_epoch, c.timezone_offset);
  return `Lentswe says: ${c.description.toLowerCase()} in ${c.place.split(",")[0]}, ${deg(c.temp_c)}. Sunrise ${rise}. Sunset ${set}. Humidity ${c.humidity}%, pressure ${c.pressure_hpa} hPa. UV is ${uvWord(c.uv_index)}.`;
}

async function detectCity() {
  try {
    const res = await fetch("weather.php?ip=1");
    const data = await res.json();
    if (data.ok && data.city && !$("q").value) $("q").value = data.city;
  } catch (_) { /* optional */ }
  if ($("q").value.trim()) search($("q").value);
}

async function search(query) {
  const q = (query || $("q").value || "").trim();
  if (!q) {
    $("error").hidden = false;
    $("error").textContent = "Enter a city name or ZIP code.";
    return;
  }
  $("error").hidden = true;
  $("status").hidden = false;
  $("status").textContent = "Fetching…";
  try {
    const res = await fetch(`weather.php?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || "Request failed");
    lastBundle = data;
    paint();
    $("status").hidden = !data.demo;
    $("status").textContent = data.demo ? "Demo data — add an API key to .env for live weather." : "";
  } catch (err) {
    $("error").hidden = false;
    $("error").textContent = err.message;
    $("status").hidden = true;
  }
}

function paint() {
  if (!lastBundle) return;
  const c = lastBundle.current;
  $("place").textContent = c.place;
  $("temp").textContent = deg(c.temp_c);
  $("cond").textContent = c.description;
  $("meta").textContent = `High ${deg(c.max_c)} · Low ${deg(c.min_c)}`;
  $("said").textContent = lineFor(c);
  $("heroIcon").hidden = false;
  $("heroIcon").src = iconUrl(c.icon);
  $("heroIcon").alt = "";

  $("tFeel").textContent = deg(c.feels_like_c);
  $("tHum").textContent = `${c.humidity}%`;
  $("tWind").textContent = wind(c.wind_mps);
  $("tPres").textContent = `${c.pressure_hpa} hPa`;
  $("tUv").textContent = `${Math.round(c.uv_index)} (${uvWord(c.uv_index)})`;
  $("tRise").textContent = clock(c.sunrise_epoch, c.timezone_offset);
  $("tSet").textContent = clock(c.sunset_epoch, c.timezone_offset);
  applyLight(c);

  $("hours").innerHTML = (lastBundle.hourly || []).map((h, i) => `
    <article>
      <div class="when">${hourLabel(h.epoch, c.timezone_offset, i)}</div>
      <img src="${iconUrl(h.icon)}" alt="" />
      <div class="t">${deg(h.temp_c)}</div>
      <div class="p">${Math.round((h.pop || 0) * 100)}% rain</div>
    </article>
  `).join("");

  $("days").innerHTML = (lastBundle.daily || []).map((d) => `
    <div class="day">
      <span>${d.date_label}</span>
      <span>${d.description}</span>
      <span class="hi">${deg(d.max_c)}</span>
      <span>${deg(d.min_c)}</span>
    </div>
  `).join("");
}

function speak() {
  if (!lastBundle || !window.speechSynthesis) return;
  const u = new SpeechSynthesisUtterance(lineFor(lastBundle.current));
  speechSynthesis.cancel();
  speechSynthesis.speak(u);
}

function listen() {
  const Rec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Rec) {
    $("error").hidden = false;
    $("error").textContent = "Voice search needs Chrome or Edge.";
    return;
  }
  const rec = new Rec();
  rec.lang = "en-ZA";
  rec.onresult = (e) => {
    $("q").value = e.results[0][0].transcript;
    search();
  };
  rec.start();
}

$("searchForm").addEventListener("submit", (e) => {
  e.preventDefault();
  search();
});
$("unitBtn").addEventListener("click", () => {
  unit = unit === "C" ? "F" : "C";
  $("unitBtn").textContent = `°${unit}`;
  paint();
});
$("speakWeather").addEventListener("click", speak);
$("voiceSearch").addEventListener("click", listen);

detectCity();
