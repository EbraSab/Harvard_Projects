document.addEventListener('DOMContentLoaded', function() {

  // Your existing button event listeners
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('#compose-form').addEventListener('submit', send_email);


  load_mailbox('inbox');
});


function compose_email() {
  // Show compose view and hide others
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#view_email').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}



function send_email(event) {
  event.preventDefault();

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: document.querySelector('#compose-recipients').value,
      subject: document.querySelector('#compose-subject').value,
      body: document.querySelector('#compose-body').value
    })
  })
  .then(response => response.json())
  .then(result => {
    console.log(result);
    load_mailbox('inbox');  // Redirect to sent mailbox after sending
  })
  .catch(error => console.error('Error:', error));
}



function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#view_email').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
    // Print emails
    console.log(emails);

    // ... do something else with emails ...
    emails.forEach(email => {
      const div = document.createElement('div')
      div.className = email.read ? 'read' : 'unread'; //Set the class 'read' if clicked (change the colors from style.scc)
      div.id = 'email';
      div.innerHTML = `
          <div id="sender"><strong>${email.sender}</strong></div>
          <div id="subject">${email.subject}</div>
          <div id="time">${email.timestamp}</div>
      `
      document.querySelector('#emails-view').append(div)
      div.addEventListener('click', () => view_email(email.id, mailbox));   // ... make it clickable ...
    });
  });
}


function view_email(email_id, mailbox){
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#view_email').style.display = 'block';

  const emailContainer = document.querySelector('#view_email');
  emailContainer.innerHTML = '';

  fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {
      // Mark as read
      if (!email.read) {
        fetch(`/emails/${email_id}`, {
          method: 'PUT',
          body: JSON.stringify({ read: true })
        });
      }

      // Display email details
      emailContainer.innerHTML = `
        <h3>${email.subject}</h3>
        <p><strong>From:</strong> ${email.sender}</p>
        <p><strong>To:</strong> ${email.recipients.join(', ')}</p>
        <p><strong>Timestamp:</strong> ${email.timestamp}</p>
        <hr>
        <p>${email.body}</p>
        <hr>
        <button class="btn btn-sm btn-outline-primary" id="reply">Reply</button>
        ${mailbox !== "sent" ? `<button class="btn btn-sm btn-outline-primary" id="archive">${email.archived ? 'Unarchive' : 'Archive'}</button>` : '' }
      `;
    console.log(email);

    document.querySelector('#reply').addEventListener('click', () => {
      compose_email()
      document.querySelector('#compose-recipients').value = email.sender;
      document.querySelector('#compose-subject').value = email.subject.startsWith("Re: ") ? `${email.subject}` : `Re: ${email.subject}`;
      document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote:\n${email.body}`;
    });

    document.querySelector('#archive').addEventListener('click', () => {
      fetch(`/emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({ archived: !email.archived })
      })
      .then(() => load_mailbox('inbox'));
    });
  });
}