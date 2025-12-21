function getQueryParam(param){
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param);
}

const examDateInput = document.getElementById("exam-date");
const hasAllergyRadio = document.getElementById("has-allergy");
const hasNoAllergyRadio = document.getElementById("has-no-allergy");
const allergyBox = document.getElementById("allergy-box");

const examDateFromUrl = getQueryParam("exam_date");
if (examDateFromUrl) {
    examDateInput.value = examDateFromUrl;
} else {
    const today = new Date().toISOString().split("T")[0];
    examDateInput.value = today;
}

function toggleAllergyBox(){
    if(hasAllergyRadio.checked){
        allergyBox.style.display = "block";
    }
    else{
        allergyBox.style.display = "none";
        allergyBox.querySelectorAll("input[type='checkbox']").forEach(cb => cb.checked = false);
    }
}
hasAllergyRadio.addEventListener("change", toggleAllergyBox);
hasNoAllergyRadio.addEventListener("change", toggleAllergyBox);

