
  function togglePasswordVisibility() {
    var passwordInput = document.getElementById("password");
    var showHideIcon = document.querySelector(".show-hide");
  
    if (passwordInput.type === "password") {
      passwordInput.type = "text";
      showHideIcon.textContent = "Hide";
    } else {
      passwordInput.type = "password";
      showHideIcon.textContent = "Show";
    }
  }
  