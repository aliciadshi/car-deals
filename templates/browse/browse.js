const form = document.querySelector("#filter-form");
const resetButton = document.querySelector("#reset-filters");
const listings = document.querySelectorAll(".listing");
const emptyState = document.querySelector("#empty-state");

function numbersIn(value) {
    const matches = value.replace(/,/g, "").match(/\d+/g);
    return matches ? matches.map(Number) : [];
}

function isOpenChoice(value, fallback) {
    const text = value.trim().toLowerCase();
    return text === "" || text === fallback;
}

function matchesText(filterValue, rowValue, openChoice) {
    if (isOpenChoice(filterValue, openChoice)) {
        return true;
    }
    return rowValue.toLowerCase().includes(filterValue.trim().toLowerCase());
}

function matchesRange(filterValue, rowValue) {
    const bounds = numbersIn(filterValue);
    if (bounds.length === 0) {
        return true;
    }
    if (bounds.length === 1) {
        return rowValue <= bounds[0];
    }
    return rowValue >= bounds[0] && rowValue <= bounds[1];
}

function applyFilters() {
    const data = new FormData(form);
    let visibleCount = 0;

    listings.forEach((listing) => {
        const visible =
            matchesText(data.get("make"), listing.dataset.make, "any make") &&
            matchesText(data.get("model"), listing.dataset.model, "any model") &&
            matchesRange(data.get("year"), Number(listing.dataset.year)) &&
            matchesRange(data.get("price"), Number(listing.dataset.price)) &&
            matchesRange(data.get("mileage"), Number(listing.dataset.mileage));

        listing.hidden = !visible;
        if (visible) {
            visibleCount += 1;
        }
    });

    emptyState.hidden = visibleCount > 0;
}

form.addEventListener("submit", (event) => {
    event.preventDefault();
    applyFilters();
});

resetButton.addEventListener("click", () => {
    form.reset();
    applyFilters();
});
