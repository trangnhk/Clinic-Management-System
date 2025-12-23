function checkDiUng(patientId, medId) {
    fetch('/api/check-allergy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            patient_id: patientId,
            medicine_id: medId
        })
    })
        .then(res => res.json())
        .then(data => {
            const warnBox = document.getElementById("allergyWarning");
            if (!warnBox) return;

            if (data.is_allergic) {
                warnBox.innerHTML =
                    `DỊ ỨNG: ${data.description} (Mức độ: ${data.level})`;
                warnBox.className = "text-danger fw-bold blink_me";
                alert("CẢNH BÁO: Bệnh nhân dị ứng với thuốc này!");
            } else {
                warnBox.innerText = "Không phát hiện dị ứng thuốc này.";
                warnBox.className = "text-success fw-bold";
            }
        })
        .catch(err => {
            console.error("Lỗi kiểm tra dị ứng:", err);
        });
}