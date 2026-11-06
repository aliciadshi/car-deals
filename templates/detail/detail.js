const checkboxes = document.querySelectorAll(".compare input");
const listingCount = document.querySelector("#listing-count");
const totalListings = checkboxes.length;

function updateListingCount() {
    const selected = [...checkboxes].filter((box) => box.checked).length;
    listingCount.textContent = selected
        ? `${selected} selected`
        : `${totalListings} sample listings`;
}

checkboxes.forEach((box) => {
    box.addEventListener("change", updateListingCount);
});
