function loadChart(skills){

let scores=[];

for(let i=0;i<skills.length;i++){
scores.push(Math.floor(Math.random()*100));
}

var ctx=document.getElementById("skillChart");

new Chart(ctx,{
type:"bar",
data:{
labels:skills,
datasets:[{
label:"Skill Performance",
data:scores
}]
}
});

}