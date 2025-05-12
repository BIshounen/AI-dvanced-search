let selected_item;
let sceneItemsController;

let current_timestamp;

let drawing = {
    'is_drawing': false,
    'x1': 0,
    'y1': 0,
    'x2': 0,
    'y2': 0
}

if (!String.prototype.format) {
    String.prototype.format = function() {
      var args = arguments;
      return this.replace(/{(\d+)}/g, function(match, number) { 
        return typeof args[number] != 'undefined'
          ? args[number]
          : match
        ;
      });
    };
  }

window.vmsApiInit = async function () {
    initResourcesUI();
}

window.onload = function () {
    grab_button = document.getElementById('grab-button');
    grab_button.addEventListener('click', () => get_current_frame(selected_item));

    search_button = document.getElementById('search-selection-button');
    search_button.addEventListener('click', () => search_redirect());
}


function add_device(item){
    const list = document.getElementById('side-panel');
    let device_item = document.createElement('div');
    device_item.addEventListener('click', () => select_item(item))
    device_item.setAttribute('id', item.id);
    device_item.className = "device-item";
    device_item.innerText = item.resource.name;
    list.appendChild(device_item);
}

function remove_device(resource_id){
    console.log(resource_id)
    let device_item = document.getElementById(resource_id);
    device_item.remove();
}

async function initResourcesUI(){
    const current_tab = vms.tabs.current;
    const state = await current_tab.state();

    state.items.forEach(item => {
        if (item.resource.type === "camera")
            {
                console.log(item);
                add_device(item);
            }
        })

    current_tab.itemAdded.connect(item => add_device(item))
    current_tab.itemRemoved.connect(resource_id => remove_device(resource_id))
}

function select_item(item){
    if(selected_item){
        element = document.getElementById(selected_item.id);
        element.className = "device-item";
    }
    selected_item = item;
    element = document.getElementById(item.id);
    element.className = "device-item selected";
    get_current_frame(item);
}

async function get_current_timestamp(item){
    const updated_item = await vms.tab.item(item.id);
    console.log(updated_item.item.params.media.timestampMs);
    current_timestamp = updated_item.item.params.media.timestampMs;
    return current_timestamp;
}

async function get_current_frame(item){
    console.log('grabbing');
    const old_image = document.getElementById('image-canvas');
    if(old_image){
        old_image.remove();
    }
    const old_canvas = document.getElementById('drawing-canvas');
    if(old_canvas){
        old_canvas.remove();
    }
    canvas_element = document.getElementById('work-area-image');

    timestamp = await get_current_timestamp(item);
    device_id = item.resource.id.split('.')[1];
    console.log(item);
    url = get_frame_url.format(device_id) + `?timestamp=${timestamp}`;
    console.log(url);
    img = new Image();
    await new Promise(r => img.onload=r, img.src=url);
    let canvas = document.createElement('canvas');
    canvas.className = "image-canvas";
    canvas.id = "image-canvas";
    let ctx = canvas.getContext("2d");
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);
    canvas_element.appendChild(canvas);

    console.log('adding canvas')
    let canvas2 = document.createElement('canvas');
    canvas2.style.position = "absolute";
    canvas_rect = canvas.getBoundingClientRect()
    canvas2.style.left = canvas_rect.left + 'px';
    canvas2.style.top = canvas_rect.top + 'px';
    canvas2.width = img.width;
    canvas2.height = img.height;
    canvas2.id = "drawing-canvas";
    canvas_element.appendChild(canvas2);

    canvas2.onclick = (event) => place_point(event);
    canvas2.addEventListener("mousemove", (event) =>  draw(event));
}

function place_point(event){
    console.log('clicked');
    let canvas = document.getElementById("drawing-canvas");
    let rect = canvas.getBoundingClientRect();
    let mouse_coord = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
    }
    if(!drawing.is_drawing){
        drawing.is_drawing = true;

        drawing.x1 = mouse_coord.x;
        drawing.y1 = mouse_coord.y;
    }
    else{
        drawing.is_drawing = false;

        drawing.x2 = mouse_coord.x;
        drawing.y2 = mouse_coord.y;
    }
}

function draw(event){
    console.log('drawing');
    if(drawing.is_drawing){
        let canvas = document.getElementById("drawing-canvas");
        let ctx = canvas.getContext("2d");
        let rect = canvas.getBoundingClientRect();
        let mouse_coord = {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top
        }
    
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.beginPath();
        ctx.lineWidth = "3";
        ctx.strokeStyle = "magenta";
        ctx.rect(drawing.x1, drawing.y1, - drawing.x1 + mouse_coord.x, - drawing.y1 + mouse_coord.y);
        ctx.stroke();
    }
}

function search_redirect() {
    url = get_frame_url.format(device_id) + `?timestamp=${timestamp}` ;
    console.log(url)
    canvas = document.getElementById("drawing-canvas");
    window.location.href = '/search?query=' + url + '%26rect=' + `(${drawing.x1/canvas.width}, ${drawing.y1/canvas.height}, ${drawing.x2/canvas.width}, ${drawing.y2/canvas.height})` + '&is_image=true';
}
