

function showLogin() {
    document.querySelector('.screen-login').classList.add('active');
    document.querySelector('.screen-register').classList.remove('active');
    document.querySelector('.screen-password').classList.remove('active');
}
function showRegister() {
    document.querySelector('.screen-register').classList.add('active');
    document.querySelector('.screen-login').classList.remove('active');
}
function closeModal() {
    document.querySelector('.screen-login').classList.remove('active');
    document.querySelector('.screen-register').classList.remove('active');
    document.querySelector('.screen-password').classList.remove('active');
    document.querySelector('.screen-reset').classList.remove('active');
}
function forgotPassword() {
    document.querySelector('.screen-password').classList.add('active');
    document.querySelector('.screen-login').classList.remove('active');
}
function resetPassword() {
    document.querySelector('.screen-reset').classList.add('active');
    document.querySelector('.screen-password').classList.remove('active');
}

// Hiển thị modal thành công
function showSuccessModal() {
    document.getElementById('successModal').style.display = 'block';
}

// Chuyển hướng đến trang đăng nhập
function redirectToLogin() {
    closeModal();
    document.getElementById('successModal').style.display = 'none';
    showLogin();
}

// Hiển thị modal thành công
function showForgotPasswordSuccessModal() {
    document.getElementById('forgotPasswordSuccessModal').style.display = 'block';
}

// Đóng modal thành công
function closeForgotPasswordSuccessModal() {
    document.getElementById('forgotPasswordSuccessModal').style.display = 'none';
}

// Hiển thị modal lỗi
function showForgotPasswordErrorModal() {
    document.getElementById('forgotPasswordErrorModal').style.display = 'block';
}

// Đóng modal lỗi
function closeForgotPasswordErrorModal() {
    document.getElementById('forgotPasswordErrorModal').style.display = 'none';
}

// Chuyển hướng đến form reset password
function redirectedToReset() {
    closeModal();
    closeForgotPasswordSuccessModal();
    resetPassword();
}