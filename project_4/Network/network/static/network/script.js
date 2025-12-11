document.addEventListener('DOMContentLoaded', () => {

  // Like buttons
  document.querySelectorAll('#like-btn').forEach(button => {
    button.onclick = () => {
      const postId = button.dataset.postId;
      fetch('/like_post/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `post_id=${postId}`
      })
      .then(response => response.json())
      .then(data => {
        if(!data.error) {
          const icon = button.querySelector('i');
          const countSpan = button.querySelector('.like-count');
          countSpan.textContent = data.likes_count;
          if(data.liked) {
            icon.classList.remove('fa-regular');
            icon.classList.add('fa-solid', 'liked');
          } else {
              icon.classList.remove('fa-solid', 'liked');
              icon.classList.add('fa-regular');
          }
        }
      });
    };
  });


  // Follow buttons
  document.querySelectorAll('#follow-btn').forEach(button => {
      button.addEventListener('click', () => {
          const userId = button.dataset.userId;

          fetch('/follow/', {
              method: 'POST',
              headers: {
                  'X-CSRFToken': getCookie('csrftoken'),  // your CSRF getter function
                  'Content-Type': 'application/x-www-form-urlencoded',
              },
              body: `user_id=${userId}`
          })
          .then(response => response.json())
          .then(data => {
              if (!data.error) {
                  // Update button text & icon
                  if (data.following) {
                      button.innerHTML = '<span class="fa fa-check-circle"></span> Unfollow';
                  } else {
                      button.innerHTML = '<span class="fa fa-plus-circle"></span> Follow';
                  }

                  // Find the follower and following count elements related to this user
                  // Assuming you have some container elements with IDs or classes to update
                  // For example:
                  const followersCountElem = document.querySelector('#followers h2 strong');

                  if (followersCountElem) {
                      followersCountElem.textContent = data.followers_count;
                  }

              }
          });
      });
  });


    // Edit buttons
    document.querySelectorAll('#edit-btn').forEach(button => {
        button.onclick = () => {
            const postDiv = button.closest('.post');
            const postId = button.dataset.postId;
            const contentElem = postDiv.querySelector('.content');

            if (button.value === 'Edit') {
                contentElem.contentEditable = "true";
                contentElem.focus();
                button.value = "Save";
            } else {
                const newContent = contentElem.innerText.trim();

                fetch('/edit_post/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `post_id=${postId}&content=${encodeURIComponent(newContent)}`
                })
                .then(response => {
                    if(!response.ok) throw new Error('Not authorized to edit this post');
                    return response.json();
                })
                .then(data => {
                    contentElem.textContent = data.content;
                    contentElem.contentEditable = "false";
                    contentElem.style.border = "none";
                    button.value = "Edit";
                })
                .catch(error => alert(error));
            }
        };
    });
});

//Translate
async function translateContent(elem, langSelectId) {
    // Works for both posts and comments
    const container = elem.closest('.post') || elem.closest('.comment');
    const contentElem = container?.querySelector('.content');
    const langSelect = document.getElementById(langSelectId);
    const targetLang = langSelect?.value;

    if (!contentElem || !targetLang) {
        console.error("Missing content element or language selection");
        return;
    }

    // Store original once
    if (!contentElem.dataset.original) {
        contentElem.dataset.original = contentElem.textContent.trim();
    }

    const text = contentElem.dataset.original;

    try {
        const response = await fetch('/translate_content/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({ text, lang: targetLang }),
        });

        const data = await response.json();
        if (data.translation) {
            contentElem.textContent = data.translation;
        } else {
            alert(`Error: ${data.error || "Unknown error"}`);
        }
    } catch (error) {
        console.error("Translation error:", error);
        alert("An error occurred while translating.");
    }
}


// Helper function to get CSRF token cookie (Django docs recommended method)          |WHY???|
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
