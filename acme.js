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

var loadCategories;
var loadType;
var loadProducts


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



  category1
    .then(
  function(val){
    category1 = val
    console.log("promise one resolve, ", category1)
    loadCategories =
    `<div class="card col-md-3">
        <ul class="list-group list-group-flush">
          <li class="list-group-item">line1</li>
          <li class="list-group-item">hey</li>
          <li class="list-group-item">line3</li>
        </ul>
    </div>`
    return types2
  }).then(
  function(val){
    types2 = val
    console.log("promise two resolve, ", types2)
    return products3
  }).then(
  function(val){
    products3 = val
    console.log("promise three resolve, ", products3)
    $('#button').append(loadCategories)
  })




// function sendToTheDom(passtheValue)
// // Once all data is loaded, you need to display the products in
//  a Bootstrap grid.
//   Each product must display the string name of
      //  // its product type,
      //  and product category.
      //  Not the integer id value.
