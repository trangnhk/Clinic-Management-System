const API = "/nurse/api/examination-list";
let currentDate = null;
let currentStatus = "UNSUBMITTED";

function updateAddPatientLink(){
    const addLink = document.getElementById("add-patient-link");
    if (!currentDate) return;

    addLink.href = `/nurse/add-patient?exam_date=${currentDate}&next=/nurse/examination-list?date=${currentDate}`;
}

function updateUI(data) {
    const body = document.getElementById("exam-body");
    const status = document.getElementById("exam-status");
    const total = document.getElementById("total-count");
    const addBtn = document.querySelector("a[id='add-patient-link']");
    const submitBtn = document.querySelector("button[type='submit']");
    const emptyRow = document.getElementById("empty-row");
    const template = document.getElementById("row-template");

    // reset
    body.innerHTML = "";
    addBtn.style.display = "inline-block";
    submitBtn.disabled = false;

    if (!data.exists) {
        status.innerText = "UNSUBMITTED";
        total.innerText = "Tổng cộng: 0";
        body.appendChild(emptyRow.cloneNode(true));

        return;
    }

    currentStatus = data.status;
    status.innerText = currentStatus;

    // disable btn
    if (currentStatus === "SUBMIITED") {
        addBtn.style.display = "none";
        submitBtn.disabled = true;
    }

    total.innerText = `Tổng cộng: ${data.patients.length}`;

    data.patients.forEach((p, i) => {
        const fragment = template.content.cloneNode(true);
        const tr = fragment.querySelector("tr");
        tr.id = `appointment-${p.appointment_id}`;

        tr.querySelector("[data-field='col-index']").innerText = i + 1;
        tr.querySelector("[data-field='col-patient-id']").innerText = p.patient_id;
        tr.querySelector("[data-field='col-fullname']").innerText = p.fullname;
        tr.querySelector("[data-field='col-medical-id']").innerText = p.medical_id;
        tr.querySelector("[data-field='col-dob']").innerText = p.dob;
        tr.querySelector("[data-field='col-phone']").innerText = p.phone;
        tr.querySelector("[data-field='col-address']").innerText = p.address;

        const removeBtn = tr.querySelector(".btn-remove");
        removeBtn.style.display = currentStatus === "UNSUBMITTED" ? "inline-block" : "none";
        removeBtn.onclick = () => removePatient(p.appointment_id);

        body.appendChild(tr);
    });
    updateAddPatientLink();
}


function loadByDate(date) {
    fetch(`${API}?date=${date}`)
        .then(res => res.json())
        .then(data => updateUI(data));
}

function removePatient(id) {
    if (!confirm("Bạn chắc chắn xóa bệnh nhân này?")) return;

    fetch(`/nurse/api/examination-list/${id}`, {
        method: "DELETE"
    })
    .then(res => res.json())
    .then(data => {

        const row = document.getElementById(`appointment-${id}`);
        if (row) row.style.display = "none";

        document.getElementById("total-count").innerText =
            `Tổng cộng: ${data.total}`;

        if (data.total === 0) {
            document.getElementById("exam-body")
                .appendChild(document.getElementById("empty-row").cloneNode(true));
        }
    });
}

function submitList() {
    if (!confirm("Nộp danh sách?")) return;

    fetch(`${API}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date: currentDate })
    }).then(() => loadByDate(currentDate));
}

document.addEventListener("DOMContentLoaded", () => {
    const dateInput = document.querySelector("input[name='date-of-examination']");

    // Lấy date từ URL
    const params = new URLSearchParams(window.location.search);
    const urlDate = params.get("date");

    // Ưu tiên date trên URL, nếu không có thì dùng hôm nay
    currentDate = urlDate
        ? urlDate
        : new Date().toISOString().split("T")[0];

    dateInput.value = currentDate;

    updateAddPatientLink();
    loadByDate(currentDate);

    dateInput.onchange = () => {
        currentDate = dateInput.value;

        // Cập nhật URL cho đồng bộ
        window.history.replaceState(
            null,
            "",
            `/nurse/examination-list?date=${currentDate}`
        );

        updateAddPatientLink();
        loadByDate(currentDate);
    };

    document
        .querySelector("button[type='submit']")
        .addEventListener("click", submitList);
});

