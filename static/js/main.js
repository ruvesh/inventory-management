
window.onload = function() {
  route=window.location.pathname
  setActiveNavLink(route);
  hideOrShowViewAllBtn(window.location.pathname, window.location.search);
};

function hideOrShowViewAllBtn(windowLocationPath, windowLocationSearch){
    if((windowLocationPath == '/inventory' || windowLocationPath == '/reports') 
        && windowLocationSearch.includes('search') 
        && !windowLocationSearch.includes('all')){
        document.getElementsByClassName("view-all-btn")[0].classList.add("visible");
    }
}

function setActiveNavLink(route){
    
  switch (route) {
    case '/stock':
        document.getElementById("add-stock-nav-link").classList.add("active");
        break;
    case '/inventory':
        document.getElementById("inventory-nav-link").classList.add("active");
        break;
    case '/reports':
        document.getElementById("reports-nav-link").classList.add("active");
        break;
    default:
        break;
  }
}

function confirmDelete(e, delete_url){
    e.preventDefault()
    Swal.fire({
        title: 'Are you sure?',
        text: "Your stock entry will be deleted!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, delete it!'
    }).then((result) => {
        if (result.isConfirmed) {
        window.location.replace(delete_url)
        }
    })
}

function showSuccessMessage(message){
    Swal.fire({
        icon: 'success',
        title: message,
        showConfirmButton: false,
        timer: 2500
    })
}