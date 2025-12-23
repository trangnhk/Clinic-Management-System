function xemLichSu() {
    console.log("Đã gọi xemLichSu!");

    // 1. Lấy element bệnh nhân đang chọn
    const patientInputEl = document.getElementById("patientIdHidden") || document.getElementById("patientSelect");
    if (!patientInputEl) {
        alert("Vui lòng chọn bệnh nhân trước!");
        return;
    }

    // 2. Lấy patientId và patientName
    const patientId = patientInputEl.value;
    let patientName = "";

    if (patientInputEl.tagName === "INPUT") {
        // Trường hợp Input (đã chọn từ danh sách chờ)
        patientName = patientInputEl.value;
    } else if (patientInputEl.tagName === "SELECT" && patientInputEl.selectedIndex >= 0) {
        // Trường hợp Select dropdown
        patientName = patientInputEl.options[patientInputEl.selectedIndex].text;
    }

    if (!patientId) {
        alert("Vui lòng chọn bệnh nhân trước!");
        return;
    }

    // 3. Hiển thị tên bệnh nhân lên header modal
    const nameEl = document.getElementById("historyPatientName");
    if (nameEl) {
        nameEl.innerText = patientName;
    }

    // 4. Gọi API lấy dữ liệu lịch sử
    fetch(`/doctor/api/patient-history/${patientId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient_id: patientId })
    })
    .then(res => res.json())
    .then(data => {
        const tbody = document.getElementById("historyTableBody");
        if (!tbody) return;

        tbody.innerHTML = ""; // Xóa dữ liệu cũ

        if (Array.isArray(data) && data.length > 0) {
            document.getElementById("noHistoryMsg").style.display = "none";

            data.forEach(item => {
                const row = `
                    <tr>
                        <td class="text-center fw-bold">${item.date || ""}</td>
                        <td class="text-center">${item.doctor || ""}</td>
                        <td>${item.symptoms || ""}</td>
                        <td>${item.diagnosis || ""}</td>
                        <td class="text-center">
                            <button class="btn btn-success btn-sm rounded-pill px-3" onclick="xemChiTietToa('${item.id || ""}')">
                                View
                            </button>
                        </td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
        } else {
            const noMsg = document.getElementById("noHistoryMsg");
            if (noMsg) noMsg.style.display = "block";
        }

        // 5. Mở Modal
        const historyModalEl = document.getElementById('historyModal');
        if (historyModalEl) {
            const myModal = new bootstrap.Modal(historyModalEl);
            myModal.show();
        }
    })
    .catch(err => {
        console.error(err);
        alert("Lỗi khi tải lịch sử bệnh nhân!");
    });
}
