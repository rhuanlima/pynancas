function loadcat (level) {
  var data = new FormData();
  data.append("id", document.getElementById("selectCategory").value);
  fetch("/getcat", { method: "POST", body: data })
  .then(res => res.json())
  .then(cat => {
    let selector = document.getElementById("selectSubCategory");
    selector.innerHTML = "";
    for (let c of cat) {
      let opt = document.createElement("option");
      opt.value = c[0];
      opt.innerHTML = c[1];
      selector.appendChild(opt);
    }
  });
}
