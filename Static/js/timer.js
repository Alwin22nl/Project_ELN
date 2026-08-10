let seconds = 0;
let timer = null;

function updateDisplay(){

    let hrs = Math.floor(seconds / 3600);
    let mins = Math.floor((seconds % 3600) / 60);
    let secs = seconds % 60;
    document.getElementById("timer-display").textContent =
        String(hrs).padStart(2,"0") + ":" +
        String(mins).padStart(2,"0") + ":" +
        String(secs).padStart(2,"0");

}

document
.getElementById("start-timer")
.addEventListener("click", function(){
    if(timer !== null)
        return;
    timer = setInterval(function(){
        seconds++;
        updateDisplay();
    },1000);
});

document
.getElementById("stop-timer")
.addEventListener("click", function(){
    clearInterval(timer);
    timer = null;
});

document
.getElementById("reset-timer")
.addEventListener("click", function(){
    clearInterval(timer);
    timer = null;
    seconds = 0;
    updateDisplay();
});

updateDisplay();