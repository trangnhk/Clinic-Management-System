// Danh sách thuốc kê đơn
let danhSachThuoc = [];

function themThuocVaoList() {
    const id = document.getElementById("selectedMedId").value;
    const name = document.getElementById("selectedMedName").value;
    const unit = document.getElementById("selectedMedUnit").value;
    const sl = parseInt(document.getElementById("quantity").value);
    const cachDung = document.getElementById("usage").value.trim();

    if (!id) {
        alert("Vui lòng chọn thuốc!");
        return;
    }

    if (!cachDung) {
        alert("Vui lòng nhập cách dùng!");
        return;
    }

    if (sl <= 0 || isNaN(sl)) {
        alert("Số lượng không hợp lệ!");
        return;
    }

    if (danhSachThuoc.some(m => m.id === id)) {
        alert("Thuốc này đã có trong đơn!");
        return;
    }

    const thuoc = {
        id: id,
        name: name,
        unit: unit,
        quantity: sl,
        cach_dung: cachDung
    };

    danhSachThuoc.push(thuoc);

    // Ẩn message rỗng
    document.getElementById("emptyMsg").style.display = "none";

    // Render thêm 1 dòng
    renderDongThuoc(thuoc);

    // Reset input
    document.getElementById("medKeyword").value = "";
    document.getElementById("selectedMedId").value = "";
    document.getElementById("selectedMedName").value = "";
    document.getElementById("selectedMedUnit").value = "";
    document.getElementById("usage").value = "";
    document.getElementById("quantity").value = 1;
}

function renderDongThuoc(thuoc) {
    const tbody = document.getElementById("prescriptionTable");

    const tr = document.createElement("tr");
    tr.setAttribute("data-id", thuoc.id);

    tr.innerHTML = `
        <td class="text-center fw-bold"></td>
        <td class="fw-bold text-primary">${thuoc.name}</td>
        <td class="text-center">${thuoc.quantity}</td>
        <td class="text-center">${thuoc.unit}</td>
        <td>${thuoc.cach_dung}</td>
        <td class="text-center">
            <button class="btn btn-outline-danger btn-sm rounded-circle"
                    onclick="xoaDong(this)">
                <i class="fa-solid fa-trash"></i>
            </button>
        </td>
    `;

    tbody.appendChild(tr);
    capNhatSTT();
}

function xoaDong(btn) {
    const row = btn.closest("tr");
    const medId = row.getAttribute("data-id");

    // Xóa trong mảng
    danhSachThuoc = danhSachThuoc.filter(m => m.id !== medId);

    // Xóa trên UI
    row.remove();

    // Cập nhật STT
    capNhatSTT();

    // Nếu không còn thuốc
    if (danhSachThuoc.length === 0) {
        document.getElementById("emptyMsg").style.display = "block";
    }
}

function capNhatSTT() {
    const rows = document.querySelectorAll("#prescriptionTable tr");
    rows.forEach((row, index) => {
        row.children[0].innerText = index + 1;
    });
}

// 5. Lưu phiếu
function luuPhieuKham() {

    let patientId = document.getElementById("patientIdHidden")?.value || document.getElementById("patientSelect")?.value;

    if (!patientId) {
        alert("Chưa chọn bệnh nhân!");
        return;
    }

    if (danhSachThuoc.length === 0) {
        alert("Chưa kê thuốc nào!");
        return;
    }

    const data = {
        "patient_id": patientId,
        "symptom": document.getElementById("symptom").value,
        "diagnosis": document.getElementById("diagnosis").value,
        "medicines": danhSachThuoc
    };

    fetch(`/doctor/api/save-prescription/${patientId}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(res => res.json())
      .then(res => {
          if (res.status === 200) {
              alert("Đã lưu phiếu khám thành công!");
              window.location.href = "/doctor/waiting-list";
          } else {
              alert("Lỗi: " + res.msg);
          }
      });
}

