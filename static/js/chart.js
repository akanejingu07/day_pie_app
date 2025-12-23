let chart = null;
let sortable = null;

// 初期表示
document.addEventListener("DOMContentLoaded", () => {
  loadData();
});

// データ取得 & 描画
async function loadData() {
  const res = await fetch("/data");
  const data = await res.json();

  renderList(data);
  renderChart(data);
}

// 一覧表示
function renderList(data) {
  const ul = document.getElementById("activity-list");
  ul.innerHTML = "";

  data.forEach(item => {
    const li = document.createElement("li");
    li.dataset.id = item[0];

    li.innerHTML = `
      <span class="drag-handle">≡</span>
      <span class="name">${item[1]}</span>
      <span class="minutes">${item[2]} 分</span>
      <a href="/delete/${item[0]}" class="delete">削除</a>
    `;

    ul.appendChild(li);
  });

  // Sortable を毎回作り直す
  if (sortable) {
    sortable.destroy();
  }

  sortable = new Sortable(ul, {
    animation: 150,
    ghostClass: "dragging",
    handle: ".drag-handle",
    onEnd: saveOrder
  });
}

// 並び順保存
async function saveOrder() {
  const ids = [...document.querySelectorAll("#activity-list li")]
    .map(li => li.dataset.id);

  await fetch("/reorder", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(ids)
  });

  loadData();
}

// 円グラフ描画
function renderChart(data) {
  const ctx = document.getElementById("pieChart").getContext("2d");

  const totalMinutes = data.reduce((sum, item) => sum + item[2], 0);
  const remaining = Math.max(1440 - totalMinutes, 0);

  const labels = data.map(item => item[1]);
  const minutes = data.map(item => item[2]);

  const colors = data.map((_, index) =>
    `hsl(${index * 60 % 360}, 60%, 65%)`
  );

  if (remaining > 0) {
    labels.push("残り時間");
    minutes.push(remaining);
    colors.push("#e5e7eb");
  }

  const percent = Math.round((totalMinutes / 1440) * 100);
  document.getElementById("total-time").textContent =
    `合計：${totalMinutes} 分 ／ 1440 分（${percent}%）`;

  if (chart) {
    chart.destroy();
  }

  chart = new Chart(ctx, {
    type: "pie",
    data: {
      labels: labels,
      datasets: [{
        data: minutes,
        backgroundColor: colors
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom"
        }
      }
    }    
  });
}
