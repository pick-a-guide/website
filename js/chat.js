function get_messages() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET','/get_messages',true);
    var data = new FormData();
    xhr.onreadystatechange = function() {
        if(this.status == 200 && this.readyState == 4) {
            var response = JSON.parse(this.responseText);
            response.forEach(function(each) {
                var destination;
                if(window.location.pathname == "/dashboardGuia") destination = each["guiado"];
                else destination = each["guia"];
		if(document.getElementById(destination) == null) {
                    var inbox = document.getElementsByClassName("inbox_chat")[0];
                    var copy = document.getElementById("chat_category").content.children[0].cloneNode(true);
		    copy.id = destination;
		    if(window.location.pathname == "/dashboardGuia") copy.children[0].children[0].children[0].src = "assets/pfp/guiado/"+destination;
		    else copy.children[0].children[0].children[0].src = "assets/pfp/guia/"+destination;
		    copy.children[0].children[1].children[0].innerHTML = each[destination] + copy.children[0].children[1].children[0].innerHTML;
		    copy.children[0].children[1].children[0].children[0].textContent = each["last_message"];
		    inbox.insertBefore(copy,inbox.firstChild);
		    copy = document.getElementById("msg_history").content.children[0].cloneNode(true);
		    copy.id = destination+"_chat";
		    inbox = document.getElementsByClassName("mesgs")[0];
		    inbox.insertBefore(copy,inbox.firstChild);
		}
		var chat = document.getElementById(destination+"_chat");
		var messages = each["messages"].slice(chat.children.length,each["messages"].length);
		messages.forEach(function(message) {
		    var template;
		    if(message["destination"] == destination) {
			template = document.getElementById("outgoing_message").content.children[0].cloneNode(true);
			template.children[0].children[0].textContent = message["content"];
			template.children[0].children[1].textContent = message["date"];
		    }
		    else {
		        template = document.getElementById("incoming_message").content.children[0].cloneNode(true);
			if(window.location.pathname == "/dashboardGuia") template.children[0].children[0].src = "assets/pfp/guiado/"+destination;
			else template.children[0].children[0].src = "assets/pfp/guia/"+destination;
			template.children[1].children[0].children[0].textContent = message["content"];
			template.children[1].children[0].children[1].textContent = message["date"];
		    }
		    chat.append(template);
		    chat.scrollTop = chat.scrollHeight;
		});		
            });
        }
	var last = document.getElementsByClassName("active_chat")[0];
	if(last != undefined) return;
	var a = document.getElementsByClassName("chat_list")[0];
	if(a == undefined) return;
	change_chat(a);
    }
    xhr.send();
}

function post_message() {
    var message = document.getElementById("message").value;
    if(message == "") return;
    var xhr = new XMLHttpRequest();
    xhr.open('POST','/post_message',true);
    var data = new FormData();
    data.append("message",message);
    data.append("user",document.getElementsByClassName("active_chat")[0].id);
    xhr.onreadystatechange = function() {
        if(this.status == 200) {
            get_messages();
        }
    }
    document.getElementById("message").value = "";
    xhr.send(data);
}

function change_chat(e) {
    var last = document.getElementsByClassName("active_chat")[0];
    if(last == e) return;
    if(last != undefined) {
        last.classList.remove("active_chat");
        document.getElementById(last.id+"_chat").hidden = true;
    }
    e.classList.add("active_chat");
    var chat = document.getElementById(e.id+"_chat");
    chat.hidden = false;
    chat.scrollTop = chat.scrollHeight;
}

function update() {
    get_messages();
    setInterval(get_messages,1000);
}

function update_list(e) {
    var list = [].slice.call(document.getElementsByClassName("chat_list"));
    name = e.value.toLowerCase();
    list.forEach(function(item) {
	if(item.id.toLowerCase().includes(name) || item.children[0].children[1].children[0].textContent.split("\n")[0].toLowerCase().includes(name)) item.hidden = false;
	else item.hidden = true;
    });
}
