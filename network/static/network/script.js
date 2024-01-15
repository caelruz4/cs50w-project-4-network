document.addEventListener("DOMContentLoaded", function () {
  const createPostForm = document.getElementById("create-post-form");

  createPostForm.addEventListener("submit", function (event) {
    event.preventDefault();
    const content = document.getElementById("content").value;
    
    fetch("{% url 'post' %}", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": "{{ csrf_token }}"
      },
      body: `content=${encodeURIComponent(content)}`
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          const p = document.createElement("p");
          p.textContent = data.content;
          const div = document.getElementById("all-posts");
          // Insertar antes del último.
          div.insertBefore(p, div.firstChild);
          document.getElementById("content").value = "";
        } else {
          console.error("Error al procesar la solicitud");
        }
      })
      .catch(error => console.error("Error en la solicitud AJAX:", error));
  });
});
