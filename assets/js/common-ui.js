// Shared UI helpers used across modules.
window.AppCommonUi = {
    createCommonUi({ getState, setState }) {
        function updateBookingsBadge() {
            const badge = document.getElementById('bookingsBadge');
            const { bookingCount } = getState();
            if (bookingCount > 0) {
                badge.textContent = bookingCount;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }

        function closeModal() {
            document.getElementById('confirmModal').classList.remove('show');
            setState({ pendingBooking: null });
        }

        function toggleScrollTopButton() {
            const button = document.getElementById('scrollTopBtn');
            if (!button) return;
            button.classList.toggle('visible', window.scrollY > 320);
        }

        function initScrollTopButton() {
            const button = document.getElementById('scrollTopBtn');
            if (!button) return;

            button.addEventListener('click', () => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });

            window.addEventListener('scroll', toggleScrollTopButton, { passive: true });
            toggleScrollTopButton();
        }

        function showAlert(message, type) {
            const alert = document.getElementById('bookingAlert');
            alert.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
            setTimeout(() => {
                alert.innerHTML = '';
            }, 5000);
        }

        return {
            updateBookingsBadge,
            closeModal,
            initScrollTopButton,
            showAlert
        };
    }
};
