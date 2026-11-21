const form = document.querySelector("#filter-form");
const resetButton = document.querySelector("#reset-filters");
const listingsRoot = document.querySelector("#listings");
const emptyState = document.querySelector("#empty-state");

function numbersIn(value) {
  const matches = String(value).replace(/,/g, "").match(/\d+/g);
  return matches ? matches.map(Number) : [];
}

function isOpenChoice(value, fallback) {
  const text = value.trim().toLowerCase();
  return text === "" || text === fallback;
}

function matchesRange(filterValue, rowValue) {
  if (rowValue == null || rowValue === "") {
    return false;
  }
  const bounds = numbersIn(filterValue);
  const value = Number(rowValue);
  if (bounds.length === 0) {
    return true;
  }
  if (bounds.length === 1) {
    return value <= bounds[0];
  }
  return value >= bounds[0] && value <= bounds[1];
}

function money(value) {
  if (value == null || value === "") {
    return "—";
  }
  return Number(value).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });
}

function miles(value) {
  if (value == null || value === "") {
    return "—";
  }
  return `${Number(value).toLocaleString("en-US")} mi`;
}

function searchParams(data) {
  const params = new URLSearchParams();
  const zip = String(data.get("zip") || "").trim();
  const make = String(data.get("make") || "").trim();
  const model = String(data.get("model") || "").trim();
  const priceBounds = numbersIn(data.get("price"));

  if (zip) {
    params.set("zip_code", zip);
  }
  if (!isOpenChoice(make, "any make")) {
    params.set("make", make);
  }
  if (!isOpenChoice(model, "any model")) {
    params.set("model", model);
  }
  if (priceBounds.length) {
    params.set("max_price", String(Math.max(...priceBounds)));
  }
  return params;
}

function matchesLocalFilters(car, data) {
  return (
    matchesRange(data.get("year"), car.year) &&
    matchesRange(data.get("price"), car.price) &&
    matchesRange(data.get("mileage"), car.mileage)
  );
}

function renderListings(cars) {
  listingsRoot.querySelectorAll(".listing").forEach((row) => row.remove());
  cars.forEach((car) => {
    const row = document.createElement("a");
    row.className = "listing";
    row.href = `/detail?vin=${encodeURIComponent(car.vin)}`;
    [
      car.year,
      car.make,
      car.model,
      money(car.price),
      miles(car.mileage),
      car.location || "—",
    ].forEach((text) => {
      const cell = document.createElement("span");
      cell.textContent = text ?? "—";
      row.append(cell);
    });
    listingsRoot.append(row);
  });
  emptyState.hidden = cars.length > 0;
}

async function applyFilters() {
  const data = new FormData(form);
  emptyState.hidden = false;
  emptyState.textContent = "Loading cars…";
  renderListings([]);

  const params = searchParams(data);
  console.log("Filters from the form:", Object.fromEntries(data.entries()));
  console.log("Query before search:", params.toString());

  let cars = [];
  try {
    const response = await fetch(`/api/cars?${params}`);
    if (!response.ok) {
      throw new Error(`Search failed (${response.status})`);
    }
    cars = await response.json();
  } catch (error) {
    emptyState.textContent = "Could not load cars.";
    return;
  }

  const forSale = cars.filter(
    (car) => car.vin && matchesLocalFilters(car, data),
  );
  emptyState.textContent = "No cars match these filters.";
  renderListings(forSale);
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  applyFilters();
});

resetButton.addEventListener("click", () => {
  form.reset();
  applyFilters();
});

applyFilters();
