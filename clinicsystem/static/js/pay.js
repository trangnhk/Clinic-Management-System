let currentBillId = null;

// 1. Hàm gọi API lấy chi tiết
function loadBillDetail(billId) {
    currentBillId = billId;
    console.log("Bill ID:", billId);
    fetch(`/cashier/api/bill-detail/${billId}`)
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                // Ẩn màn hình chờ
                document.getElementById('invoice-placeholder').style.setProperty('display', 'none', 'important');

                // Hiện hóa đơn
                document.getElementById('invoice-area').style.setProperty('display', 'flex', 'important');

                // 1. Mã hóa đơn
                const billIdEl = document.getElementById('bill-id-display');
                if(billIdEl) billIdEl.innerText = billId;

                // 2. Ngày lập
                const dateEl = document.getElementById('bill-date');
                if(dateEl) dateEl.innerText = new Date().toLocaleDateString('vi-VN');

                // 3. Thông tin bệnh nhân
                document.getElementById('p-name').innerText = data.patient_name;
                document.getElementById('p-diagnosis').innerText = data.diagnosis;

                // 4. Tiền tệ
                document.getElementById('fee-med').innerText = data.med_fee.toLocaleString() + " VND";
                document.getElementById('fee-exam').innerText = data.exam_fee.toLocaleString() + " VND";
                document.getElementById('total-money').innerText = data.total.toLocaleString() + " VND";

                // 5. Bảng thuốc
                let tableHtml = "";
                if (data.medicines && data.medicines.length > 0) {
                    data.medicines.forEach((m, index) => {
                        tableHtml += `
                            <tr>
                                <td>${index + 1}</td>
                                <td class="text-start fw-bold">${m.name}</td>
                                <td>${m.unit}</td>
                                <td>${m.qty}</td>
                                <td>${m.price.toLocaleString()}</td>
                                <td class="fw-bold text-danger">${m.amount.toLocaleString()}</td>
                            </tr>
                        `;
                    });
                } else {
                    tableHtml = '<tr><td colspan="6" class="text-center text-muted">Không có thuốc</td></tr>';
                }
                document.getElementById('medicine-table-body').innerHTML = tableHtml;
            } else {
                alert("Không lấy được thông tin hóa đơn!");
            }
        })
        .catch(err => {
            console.error("Lỗi:", err);
            alert("Có lỗi xảy ra khi tải dữ liệu.");
        });
}

// 2. Hàm thanh toán
function processPayment() {
    if(!currentBillId) return;
    if(!confirm("Xác nhận thanh toán hóa đơn " + currentBillId + "?")) return;

    fetch('/cashier/api/pay', {
        method: 'POST',
        body: JSON.stringify({ 'bill_id': currentBillId }),
        headers: { 'Content-Type': 'application/json' }
    }).then(res => res.json())
      .then(data => {
          if (data.success) {
              alert("Thanh toán thành công!");
              location.reload();
          } else {
              alert("Lỗi thanh toán: " + (data.msg || "Không xác định"));
          }
      })
      .catch(err => console.error(err));
}