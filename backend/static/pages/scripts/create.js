// set sticky-banner to hidden
const banner = document.getElementById("sticky_banner");
banner.style.display = "none";

// set good sticky banner to hidden
const goodBanner = document.getElementById("good_sticky_banner");
goodBanner.style.display = "none";

// function to show error
function showError(error) {
    banner.style.display = "block";
    banner.style.zIndex = "1000";
    document.getElementById("banner-content").innerText = error;
}

// function to show good sticky banner
function showGoodBanner() {
    goodBanner.style.display = "block";
    goodBanner.style.zIndex = "1000";
}

const form = document.getElementById("my_form");
form.addEventListener("submit", function (e) {
    e.preventDefault();
    const username = document.querySelector("#username").value;
    const email = document.querySelector("#email").value;
    const password = document.querySelector("#password").value;
    const rpassword = document.querySelector("#rpassword").value;
    if (password !== rpassword) {
        alert("Passwords do not match");
        return;
    }
    const url = "/api/v1/auth/create";
    const xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.status == 200) {
            showGoodBanner();
            setTimeout(() => {
                window.location.href = "/login.html";
            }, 3000);
        } else {
            const data = JSON.parse(xhr.responseText);
            showError(data.message);
            setTimeout(() => {
                banner.style.display = "none";
            }, 10000);
        }
    }
    xhr.send(JSON.stringify({
        username: username,
        email: email,
        password: password,
        repeated_password: rpassword
    }));
});