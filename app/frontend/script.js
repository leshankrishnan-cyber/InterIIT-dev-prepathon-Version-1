const API = "http://localhost:8000";

async function calculate() {
    const a = document.getElementById("a").value;
    const b = document.getElementById("b").value;

    const response = await fetch(
        `${API}/calculate?a=${a}&b=${b}`
    );

    const data = await response.json();

    document.getElementById("result").textContent =
        JSON.stringify(data, null, 2);
}

async function loadConstants() {
    const response = await fetch(`${API}/constants`);
    const data = await response.json();

    document.getElementById("constants").textContent =
        JSON.stringify(data, null, 2);
}
