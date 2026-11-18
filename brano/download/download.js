// Fills in the version, size and SHA-256 of the current packages from the
// manifest the release workflow publishes next to them. The download links
// work without this script; it only adds the details.
(function () {
  var manifest = "https://downloads.onpu.dev/brano/latest/latest.json";
  function megabytes(bytes) {
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  }
  fetch(manifest, { cache: "no-cache" })
    .then(function (response) {
      if (!response.ok) throw new Error("manifest " + response.status);
      return response.json();
    })
    .then(function (data) {
      document.querySelectorAll("[data-version]").forEach(function (node) {
        node.textContent = data.version;
      });
      Object.keys(data.files || {}).forEach(function (key) {
        var file = data.files[key];
        var card = document.querySelector('[data-file="' + key + '"]');
        if (!card) return;
        var name = file.url.split("/").pop();
        card.querySelector("[data-name]").textContent = name;
        card.querySelector("[data-size]").textContent = megabytes(file.size);
        card.querySelector("[data-sha256]").textContent = file.sha256;
        card.querySelector(".meta").hidden = false;
      });
    })
    .catch(function () {
      /* Details stay hidden; the links still download the latest packages. */
    });
})();
