// Nivel seleccionado actualmente
let nivelActual = "alto";

// Cargar configuración guardada
chrome.storage.local.get([
  "proteccion_activa", "bloqueo_auto", "mostrar_advertencias",
  "guardar_historial", "nivel_sensibilidad"
], function(data) {
  document.getElementById("toggle-protection").checked = data.proteccion_activa !== false;
  document.getElementById("toggle-block").checked = data.bloqueo_auto !== false;
  document.getElementById("toggle-notif").checked = data.mostrar_advertencias !== false;
  document.getElementById("toggle-history").checked = data.guardar_historial !== false;

  nivelActual = data.nivel_sensibilidad || "alto";
  actualizarBotonesSensibilidad(nivelActual);
});

// Función para actualizar botones de sensibilidad
function actualizarBotonesSensibilidad(nivel) {
  document.getElementById("sens-bajo").classList.remove("active");
  document.getElementById("sens-medio").classList.remove("active");
  document.getElementById("sens-alto").classList.remove("active");
  document.getElementById("sens-" + nivel).classList.add("active");
}

// Eventos de botones de sensibilidad
document.getElementById("sens-bajo").addEventListener("click", function() {
  nivelActual = "bajo";
  actualizarBotonesSensibilidad("bajo");
});

document.getElementById("sens-medio").addEventListener("click", function() {
  nivelActual = "medio";
  actualizarBotonesSensibilidad("medio");
});

document.getElementById("sens-alto").addEventListener("click", function() {
  nivelActual = "alto";
  actualizarBotonesSensibilidad("alto");
});

// Guardar configuración
document.getElementById("btn-save").addEventListener("click", function() {
  chrome.storage.local.set({
    proteccion_activa: document.getElementById("toggle-protection").checked,
    bloqueo_auto: document.getElementById("toggle-block").checked,
    mostrar_advertencias: document.getElementById("toggle-notif").checked,
    guardar_historial: document.getElementById("toggle-history").checked,
    nivel_sensibilidad: nivelActual,
  }, function() {
    var msg = document.getElementById("success-msg");
    msg.style.display = "block";
    setTimeout(function() { msg.style.display = "none"; }, 3000);
  });
});