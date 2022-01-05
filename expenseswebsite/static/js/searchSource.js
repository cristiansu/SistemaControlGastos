const searchField=document.querySelector('#searchField');
const paginationContainer=document.querySelector('.pagination-container');
const appTable=document.querySelector('.app-table');
const tableOutput=document.querySelector('.table-output');
tableOutput.style.display='none';
const tbody=document.querySelector('.table-body');


searchField.addEventListener('keyup', (e)=>{

    const searchValue=e.target.value;

    if(searchValue.trim().length>0){

        paginationContainer.style.display='none';
        //console.log('searchValue', searchValue);
        tbody.innerHTML='';

        fetch("/income/search-source",{  //lleva /income/ antes pq así está en la url de la raíz
            body:JSON.stringify({ searchText: searchValue }),
            method:"POST",
        })
        .then(res=>res.json())
        .then(data=>{
            console.log('data',data);

            appTable.style.display='none';

            tableOutput.style.display='block';

            if(data.length===0){
                tableOutput.innerHTML='No hay resultados'


            }else{


                data.forEach(item => {

                    tbody.innerHTML+=`

                    <tr>
                    <td>${item.name}</td>

                    </tr>          
                    `;
                    
                });

            }
        });
    }else{
        tableOutput.style.display='none';
        appTable.style.display='block';
        paginationContainer.style.display='block';

    }

});