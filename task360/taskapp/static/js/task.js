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
        'notify': notify,
        'group_id': localStorage.getItem('recent_grp_id')
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
        'notify': notify,
    })
    
    postData(`${CREATE_TASK_URL}?task_id=${edit_task_btn.parentElement.parentElement.parentElement.id}`, taskbody)
    window.location.href = window.location.href

})


delete_task.addEventListener('click', (event) => {
    window.location.href = `${window.location.href}/delete_task/${delete_task.parentElement.parentElement.parentElement.id}`
})

const selected = document.querySelector('.selected')
const dropdown = document.querySelector('.dropdown-menu')
const select_p_tag = document.querySelector(".selected p:nth-child(1)")
const caret = document.querySelector(".caret")
const current_grp = document.querySelector(".current-grp")
const grouplist = document.querySelectorAll('.groups-list li')

const tasklist = document.querySelector('.tasklist')
const all_task = document.querySelector('.all-task')


current_grp.innerText = localStorage.getItem('recent_grp')
select_p_tag.innerText = localStorage.getItem('recent_grp')

selected.addEventListener('click', (event) => {
    dropdown.classList.toggle('active')
    caret.classList.toggle('active')
})

async function show_tasks() {
    const response  = await fetch(`${window.location.href}/show_tasks/${localStorage.getItem('recent_grp_id')}`)
    const data = await response.json()
    
    if (data.length == 0) {
        tasklist.removeChild(all_task)
    }

    if (data.length == all_task.children.length) {
        tasklist.appendChild(all_task)
    }


    if (all_task.children.length < data.length) {
        for(let i = 0; i < data.length; i++) {
            const div_task = document.createElement("div")
            div_task.setAttribute('class', 'task')
            div_task.setAttribute('id', data[i]['id'])
            div_task.dataset.description = data[i]['description']
            div_task.dataset.status = data[i]['status']
            div_task.dataset.period = data[i]['period']
            div_task.dataset.notify = data[i]['notify']


            tasklist.appendChild(all_task)
            all_task.appendChild(div_task)

            const div_name = document.createElement("div")
            div_name.setAttribute('class', 'name')
            div_name.innerHTML = data[i]['title']

            div_task.appendChild(div_name)

            div_name.addEventListener('click', (event) => {
                console.log("click")
                const dataset = div_task.dataset
                create_task_btn.style.display = "none"
                edit_task_btn.style.display = "block"
                delete_task.style.display = "block"

                if (create_edit_box.classList.length == 2){ 
                title_h1.innerText = div_name.innerHTML
                create_edit_box.setAttribute('id', div_task.id)
                desc.value = dataset.description
                period.value = dataset.period
                task_status.value = dataset.status
                notify.value = dataset.notify
                title_h1.innerText = task.innerHTML
                }

                else {
                    create_edit_box.classList.toggle('active')
                    create_edit_box.setAttribute('id', div_task.id)
                    desc.value = dataset.description
                    period.value = dataset.period
                    task_status.value = dataset.status
                    notify.value = dataset.notify
                    title_h1.innerText = div_name.innerHTML
                    task_title.appendChild(title_h1)
                }
            })
        }
    }

}

show_tasks()

grouplist.forEach((li) => {
    li.addEventListener('click', (event) => {
        select_p_tag.innerHTML = li.innerText
        current_grp.innerText = li.innerText
        localStorage.setItem("recent_grp", current_grp.innerText)
        localStorage.setItem("recent_grp_id", li.id)
        dropdown.classList.toggle('active')
        caret.classList.toggle('active')
        show_tasks()
        show_members()
    })
})


const members_list = document.querySelector(".all-members ul")
const all_members = document.querySelector('.all-members')

async function show_members(){
    const response = await fetch(`${window.location.href}/show_members/${localStorage.getItem('recent_grp_id')}`)
    const data = response.json()

    const members = data.then(member => {
        if (member['groupusers'].length == 0) {
            all_members.removeChild(members_list)
        }

        if (member['groupusers'].length == members_list.children.length) {
            all_members.appendChild(members_list)
        }

        member['groupusers'].forEach((m) => {
            if (members_list.children.length < member['groupusers'].length){
            const member_li = document.createElement('li')
            member_li.innerHTML = m 
            members_list.appendChild(member_li)
            }
        })
    })
}

show_members()

const add_member = document.querySelector(".add-member")



add_member.addEventListener("click", (event) => {
    const member_input = document.createElement('input')
    member_input.setAttribute("class", "add-member-input")
    member_input.setAttribute('placeholder', 'Add New Member')

    const li_elem = document.createElement("li")

    all_members.appendChild(member_input)

    member_input.addEventListener("keypress", async (event) => {

        if(event.key === "Enter") {
            const url = `${window.location.href}/add_member/${localStorage.getItem('recent_grp_id')}`
            postData(url, body=JSON.stringify({'email': member_input.value}))
            li_elem.innerHTML = member_input.value
            members_list.appendChild(li_elem)
        }
    })
})









