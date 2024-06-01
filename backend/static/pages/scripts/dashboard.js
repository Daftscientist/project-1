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

function entry_point(){
    const url = "/api/v1/account/get";
    const xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.withCredentials = true;
    xhr.onreadystatechange = function() {
        if (xhr.status == 200) {
            const data = JSON.parse(xhr.responseText).result;
            if (data.two_factor_authentication_enabled) {
                document.getElementById("2fa_button").className = "";
                document.getElementById("2fa_button").className = "text-white bg-blue-400 dark:bg-blue-500 cursor-not-allowed font-medium rounded-lg text-sm px-5 py-2.5 text-center";
                document.getElementById("2fa_button").disabled = true;
            }
            if (data.discord_account_identifier != null) {
                document.getElementById("discord_oauth_button").className = "";
                document.getElementById("discord_oauth_button").className = "text-white bg-blue-400 dark:bg-blue-500 cursor-not-allowed font-medium rounded-lg text-sm px-5 py-2.5 text-center";
                document.getElementById("discord_oauth_button").disabled = true;
            }
            document.getElementById("data").innerHTML = "";
            for (const key in data) {
                const li = document.createElement("li");
                li.innerHTML = `<b>${key}</b>: ${data[key]}`;
                document.getElementById("data").appendChild(li);
            }
        } else if (JSON.parse(xhr.responseText).message == "Two-factor authentication verification required prior to accessing any protected routes.") {
            window.changeUrl("2fa-login")
        } else {
            window.changeUrl("login")
        }
    }
    xhr.send();
}
entry_point();

// make request to the /api/v1/auth/oauth/discord route to check that it doesnt error
/*const xhr2 = new XMLHttpRequest();
xhr2.withCredentials = true;
xhr2.open("GET", "/api/v1/account/link/discord", true);
xhr2.onreadystatechange = function() {
    if (xhr2.status != 200) {
        document.getElementById("discord_oauth_button").style.display = "none";
    }
}
xhr2.send();*/