function egginator9000() {
    let inputbar = document.getElementById("egg-input");
    let answer = inputbar.value;
    let answerLower = answer.toLowerCase();
    let answerLowerTrim = answerLower.trim();

    let success = document.getElementById("sucess-dialog");
    let error = document.getElementById("error-dialog");

    try {
        let tokencookie = document.cookie;
        let token = tokencookie.split("=");
        let tokenValue = token[1];
        if (tokenValue == undefined) {
            throw TypeError;
        }

        // make a post request
        let xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/easter-egg", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(JSON.stringify(
            {
                "egg": answerLowerTrim,
                "token": tokenValue
            }
        ));

        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4 && xhr.status == 200) {
                let response = JSON.parse(xhr.responseText);
                console.log(response);
                let code = response["code"];
                if (code == 69) {
                    let errorMessage = document.getElementById("error-message");
                    errorMessage.innerHTML = response["status"];
                    error.style.display = "block";

                    setTimeout(() => {
                        error.style.display = "none";
                    }, 2000);

                } else if (code == 420) {
                    let sucessMessage = document.getElementById("sucess-message");
                    sucessMessage.innerHTML = response["status"];
                    success.style.display = "block";

                    setTimeout(() => {
                        success.style.display = "none";
                    }, 2000);
                }
            }
        }


    } catch {
        console.log("Error getting token from cookie");
        error.style.display = "block";
        let errorMessage = document.getElementById("error-message");
        errorMessage.innerHTML = "You are not logged in.";

        setTimeout(() => {
            error.style.display = "none";
        }, 2000);
        return;
    }


}