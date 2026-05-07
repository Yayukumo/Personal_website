function formatWithCommas(value) {
    const onlyNumbers = value.replace(/[^\d]/g, "");

    if (!onlyNumbers) {
        return "";
    }

    return Number(onlyNumbers).toLocaleString("en-US");
}

document.querySelectorAll(".money-input").forEach((input) => {
    input.addEventListener("input", function () {
        this.value = formatWithCommas(this.value);
    });

    input.value = formatWithCommas(input.value);
});