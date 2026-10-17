function showPayment(type) {

    const cod = document.getElementById("codForm");
    const upi = document.getElementById("upiForm");

    cod.style.display = "none";
    upi.style.display = "none";

    if (type === "cod") {
        cod.style.display = "block";
    }

    if (type === "upi") {
        upi.style.display = "block";
    }
}