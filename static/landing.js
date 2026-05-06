// Landing page name capture.

(function () {
  const form = document.getElementById("name-form");
  const input = document.getElementById("trainee-name");

  if (!form || !input) return;

  const existingName = window.ProjectFreeParking.getName();
  if (existingName) {
    input.value = existingName;
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    const name = input.value.trim();
    if (!name) {
      input.focus();
      return;
    }
    window.ProjectFreeParking.setName(name);
    window.location.href = "/lobby";
  });

  input.focus();
})();
