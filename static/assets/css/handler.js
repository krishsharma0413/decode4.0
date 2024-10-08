let letters = "abcdefghijklmnopqrstuvwxyz.";

function hidder(id){
    let x = document.getElementById(id);
    x.style.display = "none";
}

for(x of document.getElementsByClassName("cryptic")){
    x.onmouseover = event => {  
        let interval = null;
        let iteration = 0;
        if( event.target.dataset.value == "none"){
            return;
        }
        clearInterval(interval);
        
        interval = setInterval(() => {
          event.target.innerText = event.target.innerText
            .split("")
            .map((letter, index) => {
              if(index < iteration) {
                return event.target.dataset.value[index];
              }
            
              return letters[Math.floor(Math.random() * 26)]
            })
            .join("");
          
          if(iteration >= event.target.dataset.value.length){ 
            clearInterval(interval);
          }
          
          iteration += 1 / 3;
        }, 30);
      }
}