document.addEventListener("DOMContentLoaded", function () {
    const likeButtons = document.querySelectorAll('.like-button');
    // token
    const csrf_token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    likeButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            const postId = button.getAttribute('data-post-id');
            const likeStatus = button.closest('article').getAttribute('data-like-status');
            const likeText = button.querySelector('.like-text');
            const svgIcon = button.querySelector('.svg-icon');

            fetch(`/toggle_like/${postId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrf_token,
                },
            })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        console.error('Error al procesar la solicitud de like/dislike');
                    } else {
                        // Actualizar el texto y estilo del botón
                        likeText.textContent = data.total_likes;
                        button.closest('article').setAttribute('data-like-status', data.liked.toString());

                        // Actualizar la clase del ícono SVG
                        if (data.liked) {
                            svgIcon.classList.add('text-red-200');
                        } else {
                            svgIcon.classList.remove('liked-icon');
                        }
                    }
                })
                .catch(error => console.error('Error en la solicitud AJAX:', error));
        });
    });
});
