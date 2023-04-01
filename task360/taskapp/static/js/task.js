const tasks = document.querySelectorAll('.name')
const task_title = document.querySelector('.task_title')

const title_h1 = document.createElement('h1')
const tasktitle_input = document.createElement("input")

tasktitle_input.setAttribute('placeholder', 'Task Name')
tasktitle_input.setAttribute('class', 'taskname')


const delete_task = document.querySelector(".delete-task")
const create_task_btn = document.querySelector('.create-task')
const edit_task_btn = document.querySelector('.edit-task')


const csrf_token = document.querySelector('input[name="csrfmiddlewaretoken"]').value


const create_edit_box = document.querySelector('.create_edit_box')
const assignee = document.querySelector('select#asignee')
const due_date = document.querySelector('input[name="duedate"]')
const desc = document.querySelector('.description textarea.desc')
const period = document.querySelector('select#period')
const task_status = document.querySelector("body > div > div.create_edit_box > div > div.status > select")
const notify = document.querySelector('input[name="notify"]')

const goal_header_p = document.querySelector(".goal-headers p") //#add task button

async function postData(url="", body={}){

    const response  = await fetch(url, {
        method: "POST",
        mode: "same-origin", 
        cache: "no-cache", 
        credentials: "same-origin", 
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token,
        }, 
        referrerPolicy: "no-referrer", 
        body: JSON.stringify(body), 
    })

    const resp = response.json()
    return resp
}



tasks.forEach((task) => {
    task.addEventListener('click', (event) => {
        const dataset = task.parentElement.dataset
        create_task_btn.style.display = "none"
        edit_task_btn.style.display = "block"
        delete_task.style.display = "block"

        if (create_edit_box.classList.length == 2) {
            title_h1.innerText = task.innerHTML
            create_edit_box.setAttribute('id', task.parentElement.id)
            desc.value = dataset.description
            period.value = dataset.period
            task_status.value = dataset.status
            notify.value = dataset.notify
            title_h1.innerText = task.innerHTML
        }
        else {
            create_edit_box.classList.toggle('active')
            create_edit_box.setAttribute('id', task.parentElement.id)
            desc.value = dataset.description
            period.value = dataset.period
            task_status.value = dataset.status
            notify.value = dataset.notify
            title_h1.innerText = task.innerHTML
            task_title.appendChild(title_h1)
        }
    })
})


create_edit_box.addEventListener('mouseleave', (event) => {
    create_edit_box.classList.remove('active')
})

title_h1.addEventListener('click', (event) => {
    task_title.appendChild(tasktitle_input)
    title_h1.style.display = "none"
    tasktitle_input.style.display = "block"
})

tasktitle_input.addEventListener('keyup', (event) => {
    title_h1.innerText = tasktitle_input.value
    title_h1.style.display = "block"

    if (event.key === "Enter") {
        tasktitle_input.style.display = "none"
    }
})



goal_header_p.addEventListener('click', (event) => {
    edit_task_btn.style.display = "none"
    create_task_btn.style.display = "block"
    delete_task.style.display = "none"

    title_h1.innerText = "New Task"
    task_title.appendChild(title_h1)
    create_edit_box.classList.toggle('active')
    desc.value = ""
    period.value = "days"
    task_status.value = "Notdone"
    notify.value = "0"
})

CREATE_TASK_URL = `${window.location.href}/create_task`

create_task_btn.addEventListener('click', (event) => {
    const assignee = document.querySelector('#asignee').value
    const due_date = document.querySelector('#due').value
    const description = document.querySelector('.description > textarea').value
    const period = document.querySelector('#period').value
    const status = document.querySelector('.status-select').value
    const notify = document.querySelector('input[name="notify"]').value

    var taskbody = JSON.stringify({
        'title': title_h1.innerText, 
        'assignee': assignee,
        'due_date': due_date, 
        'description': description,
        'status': status, 
        'period': period, 
        'notify': notify
    })
    
    postData(CREATE_TASK_URL, taskbody)
    window.location.href = window.location.href

})

edit_task_btn.addEventListener('click', (event) => {
    const assignee = document.querySelector('#asignee').value
    const due_date = document.querySelector('#due').value
    const description = document.querySelector('.description > textarea').value
    const period = document.querySelector('#period').value
    const notify = document.querySelector('input[name="notify"]').value
    const status = document.querySelector('.status-select').value

    var taskbody = JSON.stringify({
        'title': title_h1.innerText, 
        'assignee': assignee,
        'due_date': due_date, 
        'description': description, 
        'status': status,
        'period': period, 
        'notify': notify
    })
    
    postData(`${CREATE_TASK_URL}?task_id=${edit_task_btn.parentElement.parentElement.parentElement.id}`, taskbody)
    window.location.href = window.location.href

})


delete_task.addEventListener('click', (event) => {
    window.location.href = `${window.location.href}/delete_task/${delete_task.parentElement.parentElement.parentElement.id}`
})
