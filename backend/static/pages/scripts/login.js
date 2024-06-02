
// set sticky-banner to hidden
// function to show error




function entry_point() {
        const banner = document.getElementById("sticky_banner");
    banner.style.display = "none";

    // set good sticky banner to hidden
    const goodBanner = document.getElementById("good_sticky_banner");
    goodBanner.style.display = "none";

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
        const email = document.querySelector("#email").value;
        const password = document.querySelector("#password").value;
        //const twofacode = document.querySelector("#twofacode").value;
        //const backupcode = document.querySelector("#backupcode").value;
        const url = "/api/v1/auth/login";
        const xhr = new XMLHttpRequest();
        // make sure the cookie can be saved (the cookie being returned from the server)
        xhr.withCredentials = true;
        xhr.open("POST", url, true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.status == 200) {
                // send to dashboard
                showGoodBanner();
                var changed_url = false
                setTimeout(() => {
                    console.log("working")
                    if (changed_url === false) {
                        changed_url = true
                        window.location.href = "/dashboard";
                    }
                    console.log("apparently not")
                }, 2000);
            } else {
                const data = JSON.parse(xhr.responseText);
                showError(data.message);
                setTimeout(() => {
                    banner.style.display = "none";
                }, 10000);
            }
        }
        xhr.send(JSON.stringify({
            email: email,
            password: password,
            //twofacode: twofacode,
            //backupcode: backupcode
        }));
    });
}

entry_point();