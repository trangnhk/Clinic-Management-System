const keywordInput = document.getElementById("medKeyword");
const resultBox = document.getElementById("medResults");

if (keywordInput && resultBox) {
    const LIMIT = 10;
    let loading = false;
    let debounceTimer = null;

    // INPUT SEARCH
    keywordInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            resultBox.dataset.page = "1";
            resultBox.dataset.hasMore = "true";
            searchMedicines(true);
        }, 300);
    });

    // SCROLL LOAD MORE
    resultBox.addEventListener("scroll", () => {
        const nearBottom =
            resultBox.scrollTop + resultBox.clientHeight >= resultBox.scrollHeight - 5;

        if (nearBottom && resultBox.dataset.hasMore === "true") {
            searchMedicines(false);
        }
    });

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
    // SEARCH FUNCTION
    function searchMedicines(reset) {
        if (loading) return;

        const kw = keywordInput.value.trim();
        if (!kw) {
            resultBox.style.display = "none";
            return;
        }

        let page = parseInt(resultBox.dataset.page || "1");
        loading = true;

        fetch(`/doctor/api/medicines?kw=${encodeURIComponent(kw)}&page=${page}&limit=${LIMIT}`)
            .then(res => {
                if (!res.ok) throw new Error("API error");
                return res.json();
            })
            .then(result => {
                if (reset) resultBox.innerHTML = "";

                const medicines = result.data || [];
                if (medicines.length === 0) {
                    resultBox.dataset.hasMore = "false";
                    return;
                }

                medicines.forEach(m => {
                    const li = document.createElement("li");
                    li.className = "list-group-item list-group-item-action";
                    li.style.cursor = "pointer";
                    li.innerHTML = `
                        <div class="d-flex justify-content-between">
                            <strong>${m.name}</strong>
                            <span class="badge bg-info">Tồn: ${m.stock}</span>
                        </div>
                        <small class="text-muted">${m.unit} - ${Number(m.price).toLocaleString()} VNĐ</small>
                    `;
                    li.onclick = () => selectMedicine(m.id, m.name, m.unit);
                    resultBox.appendChild(li);
                });

                resultBox.style.display = "block";
                resultBox.dataset.page = (page + 1).toString();
                resultBox.dataset.hasMore = result.has_more ? "true" : "false";
            })
            .catch(err => {
                console.error("Lỗi tìm thuốc:", err);
            })
            .finally(() => {
                loading = false;
            });
    }

    // CHỌN THUỐC
    function selectMedicine(id, name, unit) {
        document.getElementById("selectedMedId").value = id;
        document.getElementById("selectedMedName").value = name;
        document.getElementById("selectedMedUnit").value = unit;

        keywordInput.value = name;
        resultBox.style.display = "none";

        // CHECK DỊ ỨNG
        const patientInput = document.getElementById("patientIdHidden") || document.getElementById("patientSelect");
        if (patientInput && patientInput.value) {
            checkDiUng(patientInput.value, id);
        }
    }

    // Ẩn dropdown khi click ra ngoài
    document.addEventListener("click", (e) => {
        if (!resultBox.contains(e.target) && e.target !== keywordInput) {
            resultBox.style.display = "none";
        }
    });
}
