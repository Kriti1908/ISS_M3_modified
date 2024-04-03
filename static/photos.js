const dropArea = document.querySelector('.drop-section')
const listSection = document.querySelector('.list-section')
const listContainer = document.querySelector('.list')
const fileSelector = document.querySelector('.file-selector')
const fileSelectorInput = document.querySelector('.file-selector-input')
const uploaded_files=[]


fileSelector.onclick = () => fileSelectorInput.click()
fileSelectorInput.onchange = () => {
    [...fileSelectorInput.files].forEach((file) => {
        if(typeValidation(file.type)){
            uploadFile(file)
        }
    })
}

dropArea.ondragover = (e) => {
    e.preventDefault();
    e.stopPropagation();
    [...e.dataTransfer.items].forEach((item) => {
        if(typeValidation(item.type)){
            dropArea.classList.add('drag-over-effect')
        }
    })
}

dropArea.ondragleave = () => {
    dropArea.classList.remove('drag-over-effect')
}

dropArea.ondrop = (e) => {
    e.preventDefault();
    dropArea.classList.remove('drag-over-effect')
    if(e.dataTransfer.items){
        [...e.dataTransfer.items].forEach((item) => {
            if(item.kind === 'file'){
                const file = item.getAsFile();
                if(typeValidation(file.type)){
                    uploadFile(file)
                }
            }
        })
    }else{
        [...e.dataTransfer.files].forEach((file) => {
            if(typeValidation(file.type)){
                uploadFile(file)
            }
        })
    }
}

function typeValidation(type){
    var splitType = type.split('/')[0]
    if(type == 'application/pdf' || splitType == 'image' || splitType == 'video'){
        return true
    }
}

function uploadFile(file){
    listSection.style.display = 'block'
    var li = document.createElement('li')
    li.classList.add('in-prog')
    li.innerHTML = `
        <div class="col">
            <img src="../static/${iconSelector(file.type)}" alt="img">
        </div>
        <div class="col">
            <div class="file-name">
                <div class="name">${file.name}</div>
                <span>100%</span>
            </div>
            <div class="file-size">${(file.size/(1024*1024)).toFixed(2)} MB</div>
        </div>
        <div class="col">
            <svg xmlns="http://www.w3.org/2000/svg" class="tick" height="20" width="20"><path d="m8.229 14.438-3.896-3.917 1.438-1.438 2.458 2.459 6-6L15.667 7Z"/></svg>
        </div>
    `
    listContainer.prepend(li)
    console.log(file.name)
    uploaded_files.push({fileName:file.name,fileObject:file})
}


function iconSelector(type){
    var splitType = (type.split('/')[0] == 'application') ? type.split('/')[1] : type.split('/')[0];
    return splitType + '.png'
}

// var username = "{{ username }}";

function uploadFiles() {
    var formData = new FormData();
    uploaded_files.forEach((file, index) => {
        formData.append(`uploaded_files[]`, uploaded_files[index]['fileObject']);
    });

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/recieve", true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                console.log("Array sent successfully!");
            } else {
                console.log("Error sending array:", xhr.status);
            }
        }
    };
    xhr.send(formData);
}

document.getElementById('upload_btn').addEventListener('click', function() {
    uploadFiles();
});

document.getElementById('vid_btn').addEventListener('click', function() {
window.location.href = '/videos';
});