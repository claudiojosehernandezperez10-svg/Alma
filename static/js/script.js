// ============================================================================
// ALMA — script.js
// Menú móvil, resaltado de sección activa al hacer scroll, y envío del
// formulario de inscripción por AJAX hacia /inscripcion (definido en app.py).
// ============================================================================

document.addEventListener("DOMContentLoaded", () => {
  setupMobileMenu();
  setupScrollSpy();
  setupEnrollForm();
});

function setupMobileMenu() {
  const toggle = document.getElementById("sidebarToggle");
  const sidebar = document.getElementById("sidebar");
  if (!toggle || !sidebar) return;

  toggle.addEventListener("click", () => {
    sidebar.classList.toggle("open");
  });

  document.querySelectorAll(".nav-link").forEach((link) => {
    link.addEventListener("click", () => sidebar.classList.remove("open"));
  });
}

function setupScrollSpy() {
  const sections = document.querySelectorAll(".section, .site-footer");
  const links = document.querySelectorAll(".nav-link");
  if (!sections.length || !links.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute("id");
          links.forEach((link) => {
            link.classList.toggle("active", link.dataset.section === id);
          });
        }
      });
    },
    { rootMargin: "-40% 0px -50% 0px", threshold: 0 }
  );

  sections.forEach((section) => observer.observe(section));
}

function setupEnrollForm() {
  const form = document.getElementById("enrollForm");
  const feedback = document.getElementById("formFeedback");
  if (!form) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearErrors(form);
    feedback.textContent = "";
    feedback.className = "form-feedback";

    const submitButton = form.querySelector("button[type=submit]");
    submitButton.disabled = true;
    submitButton.textContent = "Enviando...";

    try {
      const formData = new FormData(form);
      const response = await fetch("/inscripcion", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      if (data.ok) {
        feedback.textContent = data.mensaje;
        feedback.className = "form-feedback success";
        form.reset();
      } else if (data.errores) {
        showErrors(data.errores);
        feedback.textContent = "Por favor revisa los campos marcados.";
        feedback.className = "form-feedback error";
      } else {
        feedback.textContent = data.mensaje || "Ocurrió un error. Intenta de nuevo.";
        feedback.className = "form-feedback error";
      }
    } catch (err) {
      feedback.textContent = "No pudimos conectar con el servidor. Intenta de nuevo.";
      feedback.className = "form-feedback error";
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Quiero ser parte de ALMA";
    }
  });
}

function clearErrors(form) {
  form.querySelectorAll(".field-error").forEach((el) => (el.textContent = ""));
}

function showErrors(errores) {
  Object.entries(errores).forEach(([campo, mensaje]) => {
    const el = document.querySelector(`[data-error-for="${campo}"]`);
    if (el) el.textContent = mensaje;
  });
}
