    document.addEventListener('DOMContentLoaded', function () {
        var likeButtons = document.querySelectorAll('.like-button');

        likeButtons.forEach(function (button) {
            button.addEventListener('click', function () {
                var postId = button.getAttribute('data-post-id');
                var numberOfLikes = button.closest('article').querySelector('.number-of-likes');
                var csrf_token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

                // Solicitud AJAX al servidor
                var xhr = new XMLHttpRequest();
                xhr.open('POST', `/toggle_like/${postId}/`, true);
                xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                xhr.setRequestHeader('X-CSRFToken', csrf_token);

                xhr.onreadystatechange = function () {
                    if (xhr.readyState === 4) {
                        if (xhr.status === 200) {
                            var response = JSON.parse(xhr.responseText);

                            if (response.liked) {
                                var heartIcon = button.querySelector('.heart-icon');
                                if (heartIcon) {
                                    heartIcon.style.fill = '#db2777';
                                    heartIcon.style.stroke = '#db2777';
                                }
                            } else {
                                var heartIcon = button.querySelector('.heart-icon');
                                if (heartIcon) {
                                    heartIcon.style.fill = 'none';
                                    heartIcon.style.stroke = 'currentColor';
                                }
                            }

                            numberOfLikes.textContent = response.likes_count + ' Likes';
                        } else {
                            console.error('Error en la solicitud al servidor:', xhr.status);
                        }
                    }
                };

                xhr.send(''); // Puedes enviar datos si es necesario
            });
        });
    });
