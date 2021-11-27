
window.onload = function() {
  route=window.location.pathname
  setActiveNavLink(route);
  hideOrShowViewAllBtn(window.location.pathname, window.location.search);
  hideOldDatesInExpiryInput(window.location.pathname)
  hideOrShowLogoutButton(window.location.pathname)
};

function hideOrShowLogoutButton(windowLocationPath){
    if(windowLocationPath != '/login'){
        document.getElementById('logout-btn').classList.add("visible")
    }
}

function hideOldDatesInExpiryInput(windowLocationPath){
    if(windowLocationPath == '/stock') {
        var date = new Date();
        var minDate = new Date(date.setDate(date.getDate() + 1)).toISOString().split('T')[0];
        document.getElementById('expiryDate').setAttribute('min', minDate);  
    }

}

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
    case '/':
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

function showErrorMessage(message){
    Swal.fire({
        icon: 'error',
        title: message,
        showConfirmButton: false,
        timer: 2500
    })
}

function showInfoMessage(message){
    Swal.fire({
        icon: 'info',
        title: message,
        showConfirmButton: false,
        timer: 2500
    })
}

function confirmLogout(e, logout_url){
    e.preventDefault()
    Swal.fire({
        title: 'Do You really wish to logout?',
        text: "You will need to login again to use the application.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, Logout!'
    }).then((result) => {
        if (result.isConfirmed) {
        window.location.replace(logout_url)
        }
    })
}