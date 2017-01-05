// // console.log("the javascript")
// // $("body").html("hey")
// Create a simple user interface for your product catalog where a user
// can select a category from a dropdown.
// When a category is selected, you must use Promises to read, first,
// from the
// categories.json
// to load that array of objects,
// then load types.json,
//  then products.json.
// var category1;
// var types2;
// var products3;
var loadFireworks;
var loadDemolition;


// ===============================xhr request========================


var category1 = new Promise(function(resolve, reject){
  var xml = new XMLHttpRequest();
  xml.addEventListener("load", function(){
    var list = JSON.parse(xml.responseText)
    resolve(list)
  })
  xml.open("GET", "categories.json")
  xml.send()
})
var types2 = new Promise(function(resolve, reject){
  var xml = new XMLHttpRequest();
  xml.addEventListener("load", function(){
    var list = JSON.parse(xml.responseText)
    resolve(list)
  })
 xml.open("GET", "types.json")
  xml.send()
})

var products3 = new Promise(function(resolve, reject){
  var xml = new XMLHttpRequest();
  xml.addEventListener("load", function(){
    var list = JSON.parse(xml.responseText)
    resolve(list)
  })
  xml.open("GET", "products.json")
  xml.send()
})



var theProductName;
var theTypeIdMatcher;
var theCategoryMatcher;
 // ==========================promises================================
function fireTheFireworks() {


  category1
    .then(
  function(val){
    category1 = val
    console.log("promise one resolve, ", category1)
    return types2
  }).then(
  function(val){
    types2 = val
    console.log("promise two resolve, ", types2.types)
    for (var t in types2.types){
        console.log( types2.types[t].categoryid)

      // console.log(t)
      // theCategoryMatcher = types2.types[i];
      // console.log(theCategoryMatcher)
    }
    return products3
  }).then(
  function(val){
    products3 = val
    for (var p in products3.products[0]) {

//saving data
      theProductName = p;
      theTypeIdMatcher = products3.products[0][p].typeid;

      // console.log(theCategoryMatcher)
// if(theTypeIdMatcher === 0)
      //send data to DOM
      $('#data').append(`<div class="fireworks col-md-3">${theProductName}</div> <divclass="fireworks">type id: ${theTypeIdMatcher}</div>`)

}
    console.log("promise three resolve, ", products3)
    // $('#button').append(loadCategories)
  })

}

// how do i associate this thing with that thing



// =====================clicking a selection======================



 $('#fireworks').click( function(){
        fireTheFireworks()
 })


 $('#demolition').click( function(){
        fireTheFireworks()
  })
