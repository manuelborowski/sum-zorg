const context_menu = document.querySelector(".right-click-wrapper");
const share_menu = context_menu.querySelector(".right-click-wrapper .share-menu");
const datatable = document.querySelector("#datatable");
var item_ids = 0;
var item_to_ack = {};

if ('right_click' in table_config) {
    table_config.right_click.menu.forEach(item => {
        if ('ack' in item) {
            item_to_ack[item.item] = item.ack;
        }
    })
}

datatable.addEventListener("contextmenu", e => {
    e.preventDefault();
    e.stopImmediatePropagation();
    var x = e.x, y = e.y,
    win_width = window.innerWidth,
    win_height = window.innerHeight,
    menu_width = context_menu.offsetWidth,
    menu_height = context_menu.offsetHeight;
    if (share_menu !== null) {
        if (x > (win_width - menu_width - share_menu.offsetWidth)) {
            share_menu.style.left = "-200px";
        } else {
            share_menu.style.left = "";
            share_menu.style.right = "-200px";
        }
    }
    x = x > win_width - menu_width ? win_width - menu_width - 5 : x;
    y = y > win_height - menu_height ? e.pageY - menu_height - 5 : e.pageY;
    item_ids = get_id_of_checked_boxes();
    if (item_ids.length === 0) {
        item_ids = [e.target.parentElement.id];
    }
    context_menu.style.left = `${x}px`;
    context_menu.style.top = `${y}px`;
    context_menu.style.visibility = "visible";
});

function item_clicked(item) {
    busy_indication_on();
    if (item in right_click_cbs) {
        right_click_cbs[item](item);
    } else {
        var cont = true;
        if (item in item_to_ack) {
            cont =confirm(item_to_ack[item])
        }
        if (cont) {
            $.getJSON(Flask.url_for(table_config.right_click.endpoint, {'jds': JSON.stringify({item, item_ids})}),
                function (data) {
                    if ("message" in data) {
                        bootbox.alert(data.message);
                    } else if ("redirect" in data) {
                        if (data.redirect.new_tab) {
                            if ("ids" in data.redirect) {
                                data.redirect.ids.forEach(id => window.open(`${data.redirect.url}/[${id}]`, '_blank'))
                            } else {
                                window.open(data.redirect.url, '_blank')
                            }
                        } else {
                            if ('ids' in data.redirect) {
                                window.location = `${data.redirect.url}/[${data.redirect.ids.join(', ')}]`;
                            } else {
                                window.location = data.redirect.url;
                            }
                        }
                    } else {
                        bootbox.alert('Sorry, er is iets fout gegaan');
                    }
                }
            );
        }
    busy_indication_off();
    }
}

var right_click_cbs = {};
function subscribe_right_click(item, cb) {
    right_click_cbs[item] = cb;
}

document.addEventListener("click", () => context_menu.style.visibility = "hidden");
document.addEventListener("contextmenu", () => context_menu.style.visibility = "hidden");

