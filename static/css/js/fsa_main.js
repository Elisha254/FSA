// static/js/fsa_main.js

// ── GLOBAL STATE ────────────────────────────────────────────────────────────
let deleteTarget = null;
let supervisorsCache = {};

// ── MODAL FUNCTIONS ─────────────────────────────────────────────────────────
let addModalMode = "attachee";

function closeModal(id) {
  document.getElementById(id).classList.remove("open");
}

function openAddModal(mode = "attachee") {
  addModalMode = mode;

  // Reset form
  document.getElementById("f-name").value = "";
  document.getElementById("f-id").value = "";
  document.getElementById("f-contact").value = "";
  document.getElementById("f-email").value = "";
  document.getElementById("f-emergency").value = "";
  document.getElementById("f-course").value = "";
  document.getElementById("f-year").value = "";
  document.getElementById("f-dept").value = "";
  document.getElementById("f-supervisor").innerHTML =
    '<option value="">Select supervisor…</option>';
  document.getElementById("f-sup-contact").value = "";
  document.getElementById("f-start").value = "";
  document.getElementById("f-end").value = "";
  document.getElementById("f-status").value = "active";
  document.getElementById("f-notes").value = "";

  toggleAddModalFields();
  document.getElementById("add-modal").classList.add("open");
}

function toggleAddModalFields() {
  const showAttacheeFields = addModalMode === "attachee";
  document.querySelectorAll(".add-mode-attachee").forEach((el) => {
    el.style.display = showAttacheeFields ? "" : "none";
  });

  const title = document.getElementById("add-modal-title");
  const submit = document.getElementById("add-modal-submit");
  if (title) {
    title.textContent = showAttacheeFields
      ? "Add New Attachee"
      : "Add New Intern";
  }
  if (submit) {
    submit.innerHTML = showAttacheeFields ? "➕ Add Attachee" : "➕ Add Intern";
  }
}

function submitAddModal() {
  submitAddStudent();
}

function submitAddStudent() {
  const name = document.getElementById("f-name").value.trim();
  const sid = document.getElementById("f-id").value.trim();
  const dept = document.getElementById("f-dept").value;
  const start = document.getElementById("f-start").value;
  const end = document.getElementById("f-end").value;

  const requiredFields = ["Name", "Department", "Start Date", "End Date"];
  if (!name || !dept || !start || !end) {
    showAlert(`⚠️ ${requiredFields.join(", ")} are required.`, "error");
    return;
  }

  let studentId = sid;
  if (addModalMode === "attachee") {
    if (!studentId) {
      showAlert(
        "⚠️ Name, Student ID, Department, Start Date, and End Date are required.",
        "error",
      );
      return;
    }
  }

  if (addModalMode === "intern" && !studentId) {
    studentId = `INTERN-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
  }

  const formData = new FormData();
  formData.append("mode", addModalMode);
  formData.append("name", name);
  formData.append("student_id", studentId);
  formData.append("contact", document.getElementById("f-contact").value);
  formData.append("email", document.getElementById("f-email").value);
  formData.append(
    "emergency_contact",
    document.getElementById("f-emergency").value,
  );
  formData.append("course", document.getElementById("f-course").value);
  formData.append(
    "year_of_study",
    addModalMode === "attachee" ? document.getElementById("f-year").value : "",
  );
  formData.append("department", dept);
  formData.append("supervisor", document.getElementById("f-supervisor").value);
  formData.append("start_date", start);
  formData.append("end_date", end);
  formData.append("status", document.getElementById("f-status").value);
  formData.append("notes", document.getElementById("f-notes").value);

  fetch("/students/api/add/", {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRFToken(),
    },
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Clear form
        [
          "f-name",
          "f-id",
          "f-contact",
          "f-email",
          "f-emergency",
          "f-course",
          "f-year",
          "f-sup-contact",
          "f-start",
          "f-end",
          "f-notes",
        ].forEach((id) => {
          document.getElementById(id).value = "";
        });
        document.getElementById("f-dept").value = "";
        document.getElementById("f-supervisor").innerHTML =
          '<option value="">Select supervisor…</option>';
        document.getElementById("f-status").value = "active";
        closeModal("add-modal");
        showAlert(`✅ ${data.message}`, "success");
        setTimeout(() => window.location.reload(), 800);
      } else {
        showAlert(`⚠️ ${data.message}`, "error");
      }
    })
    .catch((error) => {
      showAlert("⚠️ Network error. Please try again.", "error");
    });
}

// Load supervisors for Add modal
function loadSupervisorsForAdd() {
  const deptId = document.getElementById("f-dept").value;
  const supervisorSelect = document.getElementById("f-supervisor");
  const contactInput = document.getElementById("f-sup-contact");

  supervisorSelect.innerHTML = '<option value="">Select supervisor…</option>';
  contactInput.value = "";

  if (!deptId) return;

  fetch(`/departments/api/supervisors/?department=${deptId}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success && data.supervisors) {
        data.supervisors.forEach((sup) => {
          const option = document.createElement("option");
          option.value = sup.id;
          option.textContent = sup.name;
          option.dataset.phone = sup.phone || "";
          supervisorSelect.appendChild(option);
        });
      }
    })
    .catch((error) => console.error("Error loading supervisors:", error));
}

// Load supervisors for Edit modal
function loadSupervisorsForEdit() {
  const deptId = document.getElementById("e-dept").value;
  const supervisorSelect = document.getElementById("e-supervisor");
  const contactInput = document.getElementById("e-sup-contact");

  supervisorSelect.innerHTML = '<option value="">Select supervisor…</option>';
  contactInput.value = "";

  if (!deptId) return;

  fetch(`/departments/api/supervisors/?department=${deptId}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success && data.supervisors) {
        data.supervisors.forEach((sup) => {
          const option = document.createElement("option");
          option.value = sup.id;
          option.textContent = sup.name;
          option.dataset.phone = sup.phone || "";
          supervisorSelect.appendChild(option);
        });
      }
    })
    .catch((error) => console.error("Error loading supervisors:", error));
}

// Update supervisor contact when supervisor is selected
document.addEventListener("DOMContentLoaded", function () {
  // For Add modal
  document
    .getElementById("f-supervisor")
    ?.addEventListener("change", function () {
      const selectedOption = this.options[this.selectedIndex];
      const contact = selectedOption?.dataset?.phone || "";
      document.getElementById("f-sup-contact").value = contact;
    });

  // For Edit modal
  document
    .getElementById("e-supervisor")
    ?.addEventListener("change", function () {
      const selectedOption = this.options[this.selectedIndex];
      const contact = selectedOption?.dataset?.phone || "";
      document.getElementById("e-sup-contact").value = contact;
    });
});

function openEdit(studentId) {
  fetch(`/students/api/${studentId}/`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        const student = data.student;
        document.getElementById("edit-modal-sub").textContent =
          `Editing: ${student.name}`;
        document.getElementById("e-original-id").value = student.id;
        document.getElementById("e-name").value = student.name;
        document.getElementById("e-id").value = student.student_id;
        document.getElementById("e-contact").value = student.contact || "";
        document.getElementById("e-email").value = student.email || "";
        document.getElementById("e-emergency").value =
          student.emergency_contact || "";
        document.getElementById("e-course").value = student.course || "";
        document.getElementById("e-year").value = student.year_of_study || "";
        document.getElementById("e-start").value = student.start_date || "";
        document.getElementById("e-end").value = student.end_date || "";
        document.getElementById("e-notes").value = student.notes || "";

        // Set department
        const dsel = document.getElementById("e-dept");
        dsel.value = student.department || "";

        // Load supervisors for this department
        if (student.department) {
          loadSupervisorsForEdit();
          // After loading, set the supervisor
          setTimeout(() => {
            const ssel = document.getElementById("e-supervisor");
            if (student.supervisor) {
              ssel.value = student.supervisor;
              // Update contact
              const selectedOption = ssel.options[ssel.selectedIndex];
              const contact =
                selectedOption?.dataset?.phone ||
                student.supervisor_contact ||
                "";
              document.getElementById("e-sup-contact").value = contact;
            }
          }, 300);
        }

        // Set status
        const ssel = document.getElementById("e-status");
        ssel.value = student.status || "active";

        document.getElementById("edit-modal").classList.add("open");
      } else {
        showAlert("⚠️ Error loading student data.", "error");
      }
    })
    .catch((error) => {
      showAlert("⚠️ Network error. Please try again.", "error");
    });
}

function openDelete(studentId) {
  deleteTarget = studentId;
  fetch(`/students/api/${studentId}/`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        document.getElementById("delete-name-display").textContent =
          `${data.student.name} (ID: ${data.student.student_id})`;
        document.getElementById("delete-modal").classList.add("open");
      }
    })
    .catch((error) => {
      showAlert("⚠️ Error loading student data.", "error");
    });
}

function showDetail(studentId) {
  window.location.href = `/students/detail/${studentId}/`;
}

// ── ADD STUDENT ─────────────────────────────────────────────────────────────
function StudentIdExists(candidate) {
  // Fallback check if the page does not know existing IDs.
  // The backend also checks for uniqueness, so this is best-effort.
  return false;
}

// ── SAVE EDIT ──────────────────────────────────────────────────────────────
function saveEdit() {
  const origId = document.getElementById("e-original-id").value;
  const name = document.getElementById("e-name").value.trim();
  const sid = document.getElementById("e-id").value.trim();
  const dept = document.getElementById("e-dept").value;
  const start = document.getElementById("e-start").value;
  const end = document.getElementById("e-end").value;

  if (!name || !sid || !dept || !start || !end) {
    showAlert(
      "⚠️ Name, Student ID, Department, Start Date, and End Date are required.",
      "error",
    );
    return;
  }

  const formData = new FormData();
  formData.append("name", name);
  formData.append("student_id", sid);
  formData.append("contact", document.getElementById("e-contact").value);
  formData.append("email", document.getElementById("e-email").value);
  formData.append(
    "emergency_contact",
    document.getElementById("e-emergency").value,
  );
  formData.append("course", document.getElementById("e-course").value);
  formData.append("year_of_study", document.getElementById("e-year").value);
  formData.append("department", dept);
  formData.append("supervisor", document.getElementById("e-supervisor").value);
  formData.append("start_date", start);
  formData.append("end_date", end);
  formData.append("status", document.getElementById("e-status").value);
  formData.append("notes", document.getElementById("e-notes").value);

  fetch(`/students/api/edit/${origId}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRFToken(),
    },
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        closeModal("edit-modal");
        showAlert(`✅ ${data.message}`, "success");
        setTimeout(() => window.location.reload(), 800);
      } else {
        showAlert(`⚠️ ${data.message}`, "error");
      }
    })
    .catch((error) => {
      showAlert("⚠️ Network error. Please try again.", "error");
    });
}

// ── CONFIRM DELETE ──────────────────────────────────────────────────────────
function confirmDelete() {
  if (!deleteTarget) return;

  fetch(`/students/api/delete/${deleteTarget}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRFToken(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        deleteTarget = null;
        closeModal("delete-modal");
        showAlert(`🗑️ ${data.message}`, "info");
        setTimeout(() => window.location.reload(), 800);
      } else {
        showAlert(`⚠️ ${data.message || "Error deleting student"}`, "error");
      }
    })
    .catch((error) => {
      showAlert("⚠️ Network error. Please try again.", "error");
    });
}

// ── EXPORT FUNCTIONS ──────────────────────────────────────────────────────
function exportFilteredCSV() {
  const params = new URLSearchParams(window.location.search);
  params.append("format", "csv");
  params.append("filtered", "true");
  window.location.href = `/students/export/data/?${params.toString()}`;
}

function exportAllCSV() {
  window.location.href = "/students/export/data/?format=csv&all=true";
}

function exportActiveCSV() {
  window.location.href = "/students/export/data/?format=csv&status=active";
}

function exportXLSX() {
  window.location.href = "/students/export/data/?format=xlsx";
}

function exportJSON() {
  window.location.href = "/students/export/data/?format=json";
}

function printRegister() {
  window.print();
}

// ── UTILITY FUNCTIONS ──────────────────────────────────────────────────────
let editingDepartmentId = null;
let editingSupervisorId = null;

function openDepartmentEdit(id, name, description) {
  editingDepartmentId = id;
  document.getElementById("dept-id").value = id;
  document.getElementById("dept-name").value = name;
  document.getElementById("dept-description").value = description;
  document.getElementById("dept-save-btn").textContent = "Update Department";
  document.getElementById("dept-cancel-btn").style.display = "";
}

function cancelDepartmentEdit() {
  editingDepartmentId = null;
  document.getElementById("dept-id").value = "";
  document.getElementById("dept-name").value = "";
  document.getElementById("dept-description").value = "";
  document.getElementById("dept-save-btn").textContent = "Add Department";
  document.getElementById("dept-cancel-btn").style.display = "none";
}

function submitDepartmentForm() {
  const name = document.getElementById("dept-name").value.trim();
  const description = document.getElementById("dept-description").value.trim();

  if (!name) {
    showAlert("⚠️ Department name is required.", "error");
    return;
  }

  const url = editingDepartmentId
    ? `/departments/api/edit/${editingDepartmentId}/`
    : "/departments/api/add/";

  const formData = new FormData();
  formData.append("name", name);
  formData.append("description", description);

  fetch(url, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRFToken(),
    },
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        showAlert(`✅ ${data.message}`, "success");
        setTimeout(() => window.location.reload(), 700);
      } else {
        showAlert(`⚠️ ${data.message}`, "error");
      }
    })
    .catch(() => showAlert("⚠️ Network error. Please try again.", "error"));
}

function deleteDepartment(id) {
  if (!confirm("Delete this department? This cannot be undone.")) return;

  fetch(`/departments/api/delete/${id}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRFToken(),
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        showAlert(`✅ ${data.message}`, "success");
        setTimeout(() => window.location.reload(), 700);
      } else {
        showAlert(`⚠️ ${data.message}`, "error");
      }
    })
    .catch(() => showAlert("⚠️ Network error. Please try again.", "error"));
}

function openSupervisorEdit(id, name, email, phone, departmentId, isActive) {
  editingSupervisorId = id;
  document.getElementById("supervisor-id").value = id;
  document.getElementById("supervisor-name").value = name;
  document.getElementById("supervisor-email").value = email;
  document.getElementById("supervisor-phone").value = phone;
  document.getElementById("supervisor-department").value = departmentId;
  document.getElementById("supervisor-active").checked = isActive;
  document.getElementById("supervisor-save-btn").textContent =
    "Update Supervisor";
  document.getElementById("supervisor-cancel-btn").style.display = "";
}

function cancelSupervisorEdit() {
  editingSupervisorId = null;
  document.getElementById("supervisor-id").value = "";
  document.getElementById("supervisor-name").value = "";
  document.getElementById("supervisor-email").value = "";
  document.getElementById("supervisor-phone").value = "";
  document.getElementById("supervisor-department").value = "";
  document.getElementById("supervisor-active").checked = true;
  document.getElementById("supervisor-save-btn").textContent = "Add Supervisor";
  document.getElementById("supervisor-cancel-btn").style.display = "none";
}

function submitSupervisorForm() {
  const name = document.getElementById("supervisor-name").value.trim();
  const email = document.getElementById("supervisor-email").value.trim();
  const phone = document.getElementById("supervisor-phone").value.trim();
  const department = document.getElementById("supervisor-department").value;
  const isActive = document.getElementById("supervisor-active").checked;

  if (!name || !department) {
    showAlert("⚠️ Name and Department are required.", "error");
    return;
  }

  const url = editingSupervisorId
    ? `/departments/api/supervisor/edit/${editingSupervisorId}/`
    : "/departments/api/supervisor/add/";

  const formData = new FormData();
  formData.append("name", name);
  formData.append("email", email);
  formData.append("phone", phone);
  formData.append("department", department);
  formData.append("is_active", isActive ? "true" : "false");

  fetch(url, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRFToken(),
    },
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        showAlert(`✅ ${data.message}`, "success");
        setTimeout(() => window.location.reload(), 700);
      } else {
        showAlert(`⚠️ ${data.message}`, "error");
      }
    })
    .catch(() => showAlert("⚠️ Network error. Please try again.", "error"));
}

function deleteSupervisor(id) {
  if (!confirm("Delete this supervisor? This cannot be undone.")) return;

  fetch(`/departments/api/supervisor/delete/${id}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRFToken(),
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        showAlert(`✅ ${data.message}`, "success");
        setTimeout(() => window.location.reload(), 700);
      } else {
        showAlert(`⚠️ ${data.message}`, "error");
      }
    })
    .catch(() => showAlert("⚠️ Network error. Please try again.", "error"));
}

function getCSRFToken() {
  return (
    document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
    document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrftoken="))
      ?.split("=")[1] ||
    ""
  );
}

function showAlert(message, type = "info") {
  const el = document.getElementById("alert-box");
  el.className = `alert alert-${type} show`;
  el.textContent = message;

  clearTimeout(el._timeout);
  el._timeout = setTimeout(() => {
    el.classList.remove("show");
  }, 3500);
}

// ── KEYBOARD SHORTCUTS ──────────────────────────────────────────────────────
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") {
    ["detail-modal", "add-modal", "edit-modal", "delete-modal"].forEach(
      (id) => {
        closeModal(id);
      },
    );
  }
});

// ── MODAL OVERLAY CLOSE ON BACKGROUND CLICK ──────────────────────────────
document.querySelectorAll(".modal-overlay").forEach((overlay) => {
  overlay.addEventListener("click", function (e) {
    if (e.target === this) {
      closeModal(this.id);
    }
  });
});

// ── DATE DISPLAY ────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", function () {
  const dateElement = document.getElementById("topbar-date");
  if (dateElement) {
    const now = new Date();
    const options = {
      weekday: "short",
      day: "2-digit",
      month: "short",
      year: "numeric",
    };
    dateElement.textContent = now.toLocaleDateString("en-GB", options);
  }
});
