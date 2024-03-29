const api_url = 
      "http://api.midax.co.uk/api/v1/getcity?country=GBR";
 
// Defining async function
async function getapi(url) {
   
    // Storing response
    const response = await fetch(url);
   
    // Storing data in form of JSON
    var data = await response.json();
    console.log(data);
    if (response) {
        hideloader();
    }
    show(data);
}
// Calling that async function
getapi(api_url);
 
// Function to hide the loader
function hideloader() {
    document.getElementById('loading').style.display = 'none';
}
// Function to define innerHTML for HTML table
function show(data) {
    let tab = 
        `<tr>
          <th>Country Code</th>
          <th>City</th>
          <th>Town</th>
          <th>Population</th>
         </tr>`;
   
    // Loop to access all rows 
    for (let r of data.list) {
        tab += `<tr> 
    <td></td>
    <td></td>
    <td></td> 
    <td>${r.Population}</td>          
</tr>`;
    }
    // Setting innerHTML as tab variable
    //document.getElementById("employees").innerHTML = tab;
}