document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("icao");
  if (input) {
    input.addEventListener("input", () => {
      input.value = input.value.toUpperCase().replace(/[^A-Z]/g, "");
    });
  }
});
