// hide the banners
document.getElementById("sticky_banner").style.display = "none";
document.getElementById("good_sticky_banner").style.display = "none";



// make post request to get user data
const get_user_url = "/api/v1/account/get";
const get_user_xhr = new XMLHttpRequest();
get_user_xhr.open("POST", get_user_url, true);
get_user_xhr.withCredentials = true;
get_user_xhr.onreadystatechange = function () {
    if (get_user_xhr.status == 200) {
        const data = JSON.parse(get_user_xhr.responseText).result;
        const max_sessions = data.max_sessions;
        document.getElementById("number-input").placeholder = max_sessions;
    }
    else {
        window.location.href = "/login.html";
    }
}
get_user_xhr.send();


document.getElementById("update_max_sessions").onsubmit = function (e) {
    e.preventDefault();
    const max_session_edit_shr = new XMLHttpRequest();
    max_session_edit_shr.open("POST", "/api/v1/account/edit/max-sessions", true);
    max_session_edit_shr.withCredentials = true;
    max_session_edit_shr.setRequestHeader("Content-Type", "application/json");
    const number = document.getElementById("number-input").value;
    max_session_edit_shr.onreadystatechange = function () {
        if (max_session_edit_shr.status == 200) {
            document.getElementById("good_sticky_banner").style.display = "block";
            document.getElementById("banner-content").innerText = "Updated!";
            // update form placeholder with new value
            document.getElementById("number-input").placeholder = number;
            // clear form
            document.getElementById("number-input").value = "";
            setTimeout(() => {
                document.getElementById("good_sticky_banner").style.display = "none";
            }, 5000);
        } else {
            document.getElementById("sticky_banner").style.display = "block";
            // get the error .message from the response
            const data = JSON.parse(max_session_edit_shr.responseText);
            document.getElementById("banner-content").innerText = data.message;
            setTimeout(() => {
                document.getElementById("sticky_banner").style.display = "none";
            }, 5000);
        }
    }

    max_session_edit_shr.send(JSON.stringify({ max_sessions: document.getElementById("number-input").value }));
}

let data_loaded = false;

const url = "/api/v1/account/session/get/all";
const xhr = new XMLHttpRequest();
xhr.open("POST", url, true);
xhr.withCredentials = true;
xhr.onreadystatechange = function () {
    if (xhr.status == 200 && !data_loaded) {
        const data = JSON.parse(xhr.responseText).result;
        // iterate over the data and append it to the table
        console.log(data)
        for (let i = 0; i < data.length; i++) {
            const row = document.createElement("tr");
            row.classList.add("bg-white", "border-b", "dark:bg-gray-800", "dark:border-gray-700");
            const ip = document.createElement("th");
            ip.className = "px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white";
            ip.innerText = data[i].creation_ip;
            row.appendChild(ip);

            const created_at = document.createElement("td");
            created_at.className = "px-6 py-4 whitespace-nowrap";
            created_at.innerText = new Date(data[i].created_at).toUTCString();
            row.appendChild(created_at);

            const expires_at = document.createElement("td");
            expires_at.className = "px-6 py-4 whitespace-nowrap";
            expires_at.innerText = new Date(data[i].expiry).toUTCString();
            row.appendChild(expires_at);

            const delete_button = document.createElement("td");
            delete_button.className = "px-6 py-4 whitespace-nowrap";
            const button = document.createElement("button");
            button.className = "bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded";
            button.innerText = "Delete";
            button.onclick = function () {
                const xhr2 = new XMLHttpRequest();
                xhr2.open("POST", "/api/v1/account/session/delete", true);
                xhr2.withCredentials = true;
                xhr2.setRequestHeader("Content-Type", "application/json");
                xhr2.onreadystatechange = function () {
                    if (xhr2.status == 200) {
                        row.remove();
                        document.getElementById("good_sticky_banner").style.display = "block";
                        document.getElementById("banner-content").innerText = "Deleted!";
                        setTimeout(() => {
                            document.getElementById("good_sticky_banner").style.display = "none";
                        }, 5000);
                    } else {
                        document.getElementById("sticky_banner").style.display = "block";
                        document.getElementById("banner-content").innerText = "Error!";
                        setTimeout(() => {
                            document.getElementById("sticky_banner").style.display = "none";
                        }, 5000);

                    }
                }

                xhr2.send(JSON.stringify({ session_id: data[i].session_token }));
            }
            delete_button.appendChild(button);
            row.appendChild(delete_button);

            document.getElementById("fill_here").appendChild(row);
        }
        data_loaded = true;
    } else if (xhr.status != 200) {
        window.location.href = "/login.html";
    }
    else {
        console.log("Data already loaded");
    }
}
xhr.send();

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