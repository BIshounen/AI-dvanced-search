window.onload = function () {

    const input_field = document.getElementById('search-input');

    if (input_field) {

        let clear_button = document.getElementById('clear-button');
        let search_button = document.getElementById('go-button');

        if (input_field.value) {
            clear_button.className = "clear-button";
            search_button.className = "go-button";
        }

        input_field.addEventListener('input', function (e) {
            let current_text = e.target.value;
            if (current_text) {
                clear_button.className = "clear-button";
                search_button.className = "go-button";
            }
            else {
                clear_button.className = "clear-button-invisible";
                search_button.className = "go-button-disabled";
            }
        });

        input_field.addEventListener("keyup", (e) => {
            if (e.key === "Enter") {
                search_redirect(e);
            }
        })
    }

    let search_button = document.getElementById('go-button');

    if (search_button) {
        search_button.addEventListener('click', search_redirect)
    }

    let clear_button = document.getElementById("clear-button")

    if (clear_button) {
        clear_button.addEventListener("click", () => {
            let input_field = document.getElementById("search-input");
            input_field.value = "";

            let clear_button = document.getElementById('clear-button');
            let search_button = document.getElementById('go-button');
            clear_button.className = "clear-button-invisible";
            search_button.className = "go-button-disabled";
        })
    }
}

function search_redirect(e) {
    let input_field = document.getElementById('search-input');
    let current_text = input_field.value;
    if (current_text) {
        disable_search();
        window.location.href = "/search?query=" + current_text;
    }
}

function add_image(url) {
    const parent = document.currentScript.parentElement;
    var img_element = document.createElement('img');
    parent.appendChild(img_element);
    img_element.className = "card-image";
    fetch(url)
        .then(res => { return res.blob() })
        .then(blob => {
            console.log('added image');
            var img = URL.createObjectURL(blob);
            img_element.setAttribute('src', img);
        })
}

let sceneItemsController;
window.vmsApiInit = async function () {
    sceneItemsController = new SceneItemsController();
}

function SceneItemsController() {
    const result = {}
    result.addSceneItem =
        async function (time_ms, resource_id) {
            console.log("pressed")
            if (!resource_id)
                return
            // Create parameters for the "addItem" call
            var settings = {};
            settings.media = {};
            // settings.media.speed = 0.5; // Playback speed
            settings.media.timestampMs = time_ms;

            // Open the item (resourceId) with parameters (settings)
            const result = await vms.tab.addItem(resource_id, settings);
            console.log(`Trying to addItem, result code is ${result.error.code}`);
            return
        }

    return result
}

function disable_search(){
    let input_field = document.getElementById('search-input');
    let clear_button = document.getElementById('clear-button');
    let go_button = document.getElementById('go-button');
    input_field.setAttribute('disabled', true);
    clear_button.className = "clear-button-invisible";
    go_button.classList = "go-button-disabled";

    results_container = document.getElementById('results-container');
    if (results_container) {
        results_container.remove();
    }

    loader = document.createElement('div');
    loader.className = "loader";
    document.body.appendChild(loader);
}

function test() {
    console.log('test');
}
