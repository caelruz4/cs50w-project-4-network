document.addEventListener('DOMContentLoaded', function () {
  var editButtons = document.querySelectorAll('.edit-button');

  editButtons.forEach(function (button) {
      button.addEventListener('click', function () {
          var postId = button.getAttribute('data-post-id');
          var postContent = button.closest('article').querySelector('.contenido-post');
          // token
          var csrf_token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
          Swal.fire({
              title: "Edit Post",
              input: "textarea",
              inputValue: postContent.textContent.trim(),
              inputAttributes: {
                  autocapitalize: "off"
              },
              showCancelButton: true,
              confirmButtonText: "Save",
              showLoaderOnConfirm: true,
              preConfirm: async (newContent) => {
                  try {
                      const response = await fetch(`/edit/${postId}`, {
                          method: 'POST',
                          headers: {
                              'Content-Type': 'application/x-www-form-urlencoded',
                              'X-CSRFToken': csrf_token,
                          },
                          body: `new_content=${encodeURIComponent(newContent)}`,
                      });

                      if (response.ok) {
                          return { status: 'success', newContent };
                      } else {
                          throw new Error('Failed to edit post');
                      }
                  } catch (error) {
                      Swal.showValidationMessage(`Request failed: ${error}`);
                  }
              },
              allowOutsideClick: () => !Swal.isLoading()
          }).then((result) => {
              if (result.isConfirmed && result.value.status === 'success') {
                  // Actualizar el contenido del post en el DOM
                  postContent.textContent = result.value.newContent;

                  Swal.fire({
                      title: 'Post edited successfully!',
                      icon: 'success'
                  });
              }
          });
      });
  });
});
