
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