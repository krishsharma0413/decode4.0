let inputbar = document.getElementById("answer-input");

inputbar.addEventListener("keyup", function(event){
    if (event.keyCode === 13){
        event.preventDefault();
        validator();
    }
});

function validator(){
    let inputbar = document.getElementById("answer-input");
    let answer = inputbar.value;
    let answerLower = answer.toLowerCase();
    let answerLowerTrim = answerLower.trim();
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);

    let tokencookie = document.cookie;
    let token = tokencookie.split("=");
    let tokenValue = token[1];

    // make a post request
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/check-answer", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify(
        {
            "answer": answerLowerTrim,
            "token": tokenValue,
            "attempt": {"experiment": urlParams.get('experiment'), "level": urlParams.get('level')}
        }
    ));

    xhr.onreadystatechange = function(){
        if (xhr.readyState == 4 && xhr.status == 200){
            let response = JSON.parse(xhr.responseText);
            
            if(response["code"] == 69){
                let errorMessage = document.getElementById("error-message");
                errorMessage.innerHTML = response["status"];
                let error = document.getElementById("error-dialog");
                error.style.display = "block";
                inputbar.value = "";
                setTimeout(() => {
                    error.style.display = "none";
                }, 2000);

            }else if(response["code"] == 420){
                window.location.href = "/level-selector";
            }
            // else if(response["code"] == 111){
            //     window.location.href = "/thank-you";
            // }

        }
    }

}