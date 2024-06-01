const routes = {
//  Route: [file, title, js file name]
    'login': ['pages/login.html', 'Login', 'login.js'],//
    'create': ['pages/create.html', 'Create', 'create.js'],//
    'dashboard': ['pages/dashboard.html', 'Dashboard', 'dashboard.js'],//
    'sessions': ['pages/sessions.html', 'Sessions', 'sessions.js'],//
    '2fa': ['pages/twofa.html', '2FA', '2fa.js'],//
    '2fa-login': ['pages/2fa-login.html', 'Verify 2FA', '2fa-login.js'],//

    '404': ['pages/404.html', '404', '404.js'],//
}

// create element called content to hold the content
const content = document.createElement("div");
content.id = "content";
document.body.appendChild(content);


// get the current route from the url if not in list return none
const currentRoute = routes[window.location.pathname.replace("/", "")] || false;
if (!currentRoute) {
    document.title = routes["404"][1];
    fetch(routes["404"][0]).then(res => res.text()).then(html => {
        document.getElementById("content").innerHTML = html;
        // add the scripts
        if (document.getElementById("page_script")) {
            document.getElementById("page_script").remove(); // fix error after go forward and back again the scripts stop working
        }
        const script = document.createElement("script");
        script.id = "page_script";
        const url_for_js = `/pages/scripts/${routes["404"][2]}`
        script.src = url_for_js;
        document.body.appendChild(script);
    
        // push the state to the history
        window.history.pushState({html: html, pageTitle: window.location.pathname, jsFile: routes["404"][2]}, "", window.location.pathname);
    });
}

window.addEventListener("popstate", (e) => {
    if(e.state){
        document.getElementById("content").innerHTML = e.state.html;
        document.title = e.state.pageTitle;
        // add the scripts
        if (document.getElementById("page_script")) {
            document.getElementById("page_script").remove();
        }
        const script = document.createElement("script");
        script.id = "page_script";
        const url_for_js = `/pages/scripts/${e.state.jsFile}`
        script.src = url_for_js;
        document.body.appendChild(script);
    }
});

if (currentRoute) {
// set the document to the file
    document.title = currentRoute[1];
    fetch(currentRoute[0]).then(res => res.text()).then(html => {
        document.getElementById("content").innerHTML = html;
        // add the scripts
        if (document.getElementById("page_script")) {
            document.getElementById("page_script").remove(); // fix error after go forward and back again the scripts stop working
        }
        const script = document.createElement("script");
        script.id = "page_script";
        const url_for_js = `/pages/scripts/${currentRoute[2]}`
        script.src = url_for_js;
        document.body.appendChild(script);

        // push the state to the history
        window.history.pushState({html: html, pageTitle: currentRoute[1], jsFile: currentRoute[2]}, "", window.location.pathname);
    });
}

const changeUrl = (url) => {
    console.log(url)
    if (!routes[url]) {
        console.log("Route not found");
        return;
    }
    console.log("fetching")
    document.title = routes[url][1];
    fetch(routes[url][0]).then(res => res.text()).then(html => {
        window.history.pushState({html: html, pageTitle: routes[url][1], jsFile: routes[url][2]}, "", url);
        document.getElementById("content").innerHTML = html;
        // add the scripts
        if (document.getElementById("page_script")) {
            document.getElementById("page_script").remove();
        }
        const script = document.createElement("script");
        script.id = "page_script";
        const url_for_js = `/pages/scripts/${routes[url][2]}`
        script.src = url_for_js;
        document.body.appendChild(script);
    });
}