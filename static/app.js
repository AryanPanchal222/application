async function searchMedicine() {
  const q = document.getElementById("searchInput").value;
  const lang = document.getElementById("language").value;
  const useAI = document.getElementById("aiCheck").checked;
  const resultDiv = document.getElementById("result");

  if (!q.trim()) {
    resultDiv.innerHTML = "<p>Please type a medicine name or symptom.</p>";
    return;
  }

  resultDiv.innerHTML = "<p>Searching...</p>";

  try {
    const params = new URLSearchParams({
      q: q,
      lang: lang,
      ai: useAI ? "1" : "0"
    });

    const res = await fetch(`/api/medicine?${params.toString()}`);
    if (!res.ok) {
      resultDiv.innerHTML = "<p>No matching medicine found in your database.</p>";
      return;
    }

    const data = await res.json();
    if (!data.items || data.items.length === 0) {
      resultDiv.innerHTML = "<p>No results.</p>";
      return;
    }

    let html = "";
    data.items.forEach(item => {
      const usesText = item.uses && item.uses.length ? item.uses.join(", ") : "N/A";
      html += `
        <div class="card">
          <h2>${item.name}</h2>
          <p>${item.description}</p>
          <p><strong>Uses:</strong> ${usesText}</p>
          <p><strong>Approx. Price:</strong> ₹${item.price}</p>
        </div>
      `;
    });

    resultDiv.innerHTML = html;

  } catch (err) {
    console.error(err);
    resultDiv.innerHTML = "<p>Server error. Try again later.</p>";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const searchBtn = document.getElementById("searchBtn");
  const searchInput = document.getElementById("searchInput");

  searchBtn.addEventListener("click", searchMedicine);
  searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      searchMedicine();
    }
  });
});
