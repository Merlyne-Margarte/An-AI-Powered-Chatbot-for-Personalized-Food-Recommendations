const chatbot=document.querySelector(".chatbot")
const toggler=document.getElementById("chatbot-toggler")
const closeBtn=document.getElementById("close-btn")
const chatBody=document.getElementById("chatBody")
const userInput=document.getElementById("userInput")
const sendBtn=document.getElementById("sendBtn")

/* Toggle */

toggler.onclick=()=>{
chatbot.style.display="flex"
setTimeout(()=>userInput.focus(),300)
}

closeBtn.onclick=()=>{
chatbot.style.display="none"
}

/* Send message */

sendBtn.onclick=sendMessage

userInput.addEventListener("keydown",(e)=>{
if(e.key==="Enter"){
e.preventDefault()
sendMessage()
}
})

/* Quick suggestion chips */

document.querySelectorAll(".chip").forEach(chip=>{
chip.onclick=()=>{
let text = chip.innerText.toLowerCase()

if(text==="meal plan") text="plan"
if(text==="nutrition summary") text="nutrition summary"
if(text==="benefits") text="benefits"

userInput.value=text

sendMessage()
}
})

function sendMessage(){

const msg=userInput.value.trim()

if(!msg) return

addMessage(msg,"user")

userInput.value=""

setTimeout(()=>botReply(msg),600)
}

function addMessage(text, sender) {

const div = document.createElement("div")
div.className = `message ${sender}`

/* Detect food recommendation */

if(sender === "bot" && text.includes("🍽️ Try")){

const nameMatch = text.match(/🍽️ Try (.*)/)
const cuisineMatch = text.match(/Cuisine: (.*)/)
const caloriesMatch = text.match(/Calories: (.*)/)
const proteinMatch = text.match(/Protein: (.*)/)

const name = nameMatch ? nameMatch[1].split("(")[0] : ""
const cuisine = cuisineMatch ? cuisineMatch[1] : ""
const calories = caloriesMatch ? caloriesMatch[1] : ""
const protein = proteinMatch ? proteinMatch[1] : ""

if(name){

div.innerHTML = `
<div class="food-card">

<div class="food-title">🍽 ${name}</div>

<div class="food-detail">🍜 Cuisine: ${cuisine}</div>

<div class="food-detail">🔥 Calories: ${calories}</div>

<div class="food-detail">💪 Protein: ${protein}</div>

<span class="food-badge">Chef Recommended</span>

</div>
`

}

}
else{

div.innerHTML = text.replace(/\n/g,"<br>")

}

chatBody.appendChild(div)

chatBody.scrollTop = chatBody.scrollHeight
}
/* Typing animation */

function showTyping(){

const typing=document.createElement("div")

typing.className="typing"
typing.id="typing"

typing.innerHTML=`
<div class="dot"></div>
<div class="dot"></div>
<div class="dot"></div>
`

chatBody.appendChild(typing)

chatBody.scrollTop=chatBody.scrollHeight
}

function botReply(input){

showTyping()

fetch("/chat", {
  method:"POST",
  headers:{"Content-Type":"application/json"},
  body:JSON.stringify({message:input})
})
.then(res=>res.json())
.then(data=>{
  document.getElementById("typing").remove();
  addMessage(data.reply,"bot");
})
.catch(()=>{
  document.getElementById("typing").remove();
  addMessage("⚠️ Server error. Please try again.","bot");
});


}

window.onload=()=>{
chatbot.style.display="flex"
}