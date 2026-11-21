const checkboxes = document.querySelectorAll(".compare input");
const listingCount = document.querySelector("#listing-count");
const defaultCount = listingCount ? listingCount.textContent : "";

function updateListingCount() {
    const selected = [...checkboxes].filter((box) => box.checked).length;
    listingCount.textContent = selected ? `${selected} selected` : defaultCount;
}

if (listingCount) {
    checkboxes.forEach((box) => {
        box.addEventListener("change", updateListingCount);
    });
}
