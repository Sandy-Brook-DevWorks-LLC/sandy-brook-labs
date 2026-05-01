/**
 * KnowItOwl! — Contact Form (Formspree)
 *
 * Posts the support form to Formspree via fetch and shows the success/error
 * UI without a page reload. Expects:
 *   - <form id="contact-form" action="https://formspree.io/f/...">
 *   - #form-container, #success-message wrapper divs
 *   - #submit-btn with a child <span> for the label text
 */
document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('contact-form');
    if (!form) return;

    var formContainer = document.getElementById('form-container');
    var successMessage = document.getElementById('success-message');
    var submitBtn = document.getElementById('submit-btn');
    var submitText = submitBtn.querySelector('span');

    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        submitBtn.disabled = true;
        var originalText = submitText.textContent;
        submitText.textContent = 'Sending...';

        var formData = new FormData(form);

        try {
            var response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: { 'Accept': 'application/json' },
            });

            if (response.ok) {
                formContainer.classList.add('hidden');
                successMessage.classList.remove('hidden');
                window.scrollTo({ top: successMessage.offsetTop - 100, behavior: 'smooth' });
            } else {
                var data = await response.json();
                if (Object.hasOwn(data, 'errors')) {
                    alert(data.errors.map(function (err) { return err.message; }).join(', '));
                } else {
                    alert('Oops! There was a problem submitting your form');
                }
                submitBtn.disabled = false;
                submitText.textContent = originalText;
            }
        } catch (err) {
            alert('Oops! There was a problem submitting your form');
            submitBtn.disabled = false;
            submitText.textContent = originalText;
        }
    });
});
