function logout() {
    const url = "/api/v1/auth/logout";
    const xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.withCredentials = true;
    xhr.onreadystatechange = function() {
        if (xhr.status == 200) {
            window.changeUrl("login");
        }
    }
    xhr.send();
}

function sidebar_funcs() {

    // get user info
    const url = "/api/v1/account/get";
    const xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.withCredentials = true;

    xhr.onreadystatechange = function() {
        if (xhr.status == 200) {
            const data = JSON.parse(xhr.responseText).result;
            // get img with id avatar_needs_src
            document.getElementById("avatar_needs_src").src = data.avatar;
            // get name_of_user and fill with username
            document.getElementById("name_of_user").innerText = data.username;
        } else if (JSON.parse(xhr.responseText).message == "Two-factor authentication verification required prior to accessing any protected routes.") {
            window.changeUrl("2fa-login")
        } else {
            window.changeUrl("login")
        }
    }
    xhr.send();
}

sidebar_funcs();