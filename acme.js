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


var theTypeId =[];
var theCategoryId;
 // ==========================promises================================




function fireTheFireworks(numberId) {


  category1
    .then(
  function(val){
    category1 = val
    console.log("promise one resolve, ", category1)


  return types2
  }).then(
  function(val){
    types2 = val
    // console.log("promise two resolve, ", types2.types)

//loop thru types
    for (var t in types2.types){
      if (numberId === types2.types[t].categoryid) {
        //sending types to array:theTypeid[] --->using this to compare product typeid in next promise
        theTypeId.push(types2.types[t].id)
      }

    }
    return products3
  }).then(
  function(val){
    products3 = val
//looping thru products
    for (var p in products3.products[0]) {

//checking if types array includes the same id as the product
      if(theTypeId.includes(products3.products[0][p].typeid)){
         theProductName = p;
         theTypeIdMatcher = products3.products[0][p].typeid;

        $('#data').append(`<li class="fireworks col-md-12">${theProductName}</li>`)
      }

//saving data
      theProductName = p;
      theTypeIdMatcher = products3.products[0][p].typeid;

      //send data to DOM

        whatIsTheCatAndTypeId(theCategoryId, theTypeId)
  } //-->end for loop

  })

}   //---> end fireTheFireworks


//if type cat id = 0 then print all products with this type id
function whatIsTheCatAndTypeId(category, type) {
  if(category === type) {
    console.log(type)

    // print products which have type id === type
    }
}
// one that compares catid with typeid



// typeid with product typeid


// =====================clicking a selection======================



 $('#fireworks').click( function(){
        fireTheFireworks(0)
 })


 $('#demolition').click( function(){
        fireTheFireworks(1)
  })
