// scripts.js - comportamiento mínimo
document.addEventListener('DOMContentLoaded', function(){
  // ejemplo: imprimir en consola que el script está cargado
  console.log('Scripts cargados - Eventos Deportivos');
});

function eliminar(){
  var x = confirm("¿Eliminar jugador?")
  if (x)
    return true
  else
    return false
}