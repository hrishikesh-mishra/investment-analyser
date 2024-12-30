(function() {
  var targetXPath = "(//table[contains(@class,'hrishi-dd')])[1]";

  var table = document.evaluate(targetXPath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;

  if (table) {
    var csvContent = "";

    var rows = table.querySelectorAll('tr#Pt11');
    rows.forEach(function(row) {
      var cells = row.querySelectorAll('td, th');

      foundCells = []
      cells.forEach(function(cell, index) {

          if(index == 2 || index ==6 || index == 3 || index==4) {
          
          
          cellData = cell.textContent.trim().replace(/"/g, '') 

          if(cellData.toLowerCase().includes("regular") ){
              cellData = "Regular"
          } else if (cellData.toLowerCase().includes("direct") ){
              cellData = "Direct"
          } else if (cellData.toLowerCase().includes("systematic") ){
              cellData = "SIP"
            } else if(cellData.toLowerCase().includes("online")   || cellData.toLowerCase().includes("mfcentral")  ){
              cellData = "Lumpsum"
            }

          foundCells.push(cellData);
       

          }


          
      });

      csvContent += foundCells.toString() + "\n";

        
    });


      console.log(csvContent);
  } else {
    alert('No table found with the specified XPath on this webpage.');
  }
})();