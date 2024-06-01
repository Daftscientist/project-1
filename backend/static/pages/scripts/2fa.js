// make a request to /account/enable/two-factor-authentication
function entry_point() {
    const url = "/api/v1/account/enable/two-factor-authentication";
    const xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.withCredentials = true;
    xhr.onreadystatechange = function () {
        if (xhr.status == 200) {
            const data = JSON.parse(xhr.responseText).result;
            console.log(data);
            document.getElementById("insert_image").innerHTML = `<img src="data:image/png;base64,${data.qr_image}" alt="QR Code">`;
            document.getElementById("secret").innerText = data.secret_token;
        } else {
            alert("An error occurred");
        }
    }
    xhr.send();

    // when continue button is clicked, show the form
    document.getElementById("continue").addEventListener("click", function () {
        document.getElementById("form_container").classList.remove("hidden");
    });

    // when the form is submitted, make a request to /account/verify/two-factor-authentication
    document.getElementById("our_form").addEventListener("submit", function (e) {
        e.preventDefault();
        const second_url = "/api/v1/account/verify/two-factor-authentication";
        const second_xhr = new XMLHttpRequest();
        second_xhr.open("POST", second_url, true);
        second_xhr.withCredentials = true;
        second_xhr.onreadystatechange = function () {
            if (second_xhr.status == 200) {
                const data = JSON.parse(second_xhr.responseText);
                window.changeUrl("dashboard");
            }
        }
        // need to send two_factor_authentication_otp_code
        const code = document.querySelector("input[name=code]").value;
        second_xhr.setRequestHeader("Content-Type", "application/json");
        second_xhr.send(JSON.stringify({ two_factor_authentication_otp_code: code }));
    });
}

entry_point();