function entry_point() {
    document.getElementById("my_form_otp").addEventListener('submit', function(e) {
        e.preventDefault();
        var code = document.getElementById('otp_code').value;
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/v1/auth/verify/otp-code", true);
        xhr.withCredentials = true;
        xhr.onreadystatechange = function() {
            if (xhr.status == 200) {
                window.changeUrl("dashboard");
            } else {
                alert("Invalid OTP code");
            }
        }
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(JSON.stringify({
            otp_code: code
        }));
    });

    document.getElementById('my_form_backup').addEventListener('submit', function(e) {
        e.preventDefault();
        var code = document.getElementById('backup_code').value;
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/v1/auth/verify/backup-code", true);
        xhr.withCredentials = true;
        xhr.onreadystatechange = function() {
            if (xhr.status == 200) {
                window.changeUrl("dashboard");
            } else {
                alert("Invalid backup code");
            }
        }
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(JSON.stringify({
            backup_code: code
        }));
    });
}

entry_point();