const SIDEBAR_CONTENT_URL = "pages/components/sidebar.html";

async function get_sidebar_content() {
    const res = await fetch(SIDEBAR_CONTENT_URL);
    const html = await res.text();
    return html;
}

class Route{
    constructor(file, title, js_file, sidebar){
        if (typeof file !== "string") {
            throw new TypeError("file must be a string");
        }
        this.file = file;
        if (typeof title !== "string") {
            throw new TypeError("title must be a string");
        }
        this.title = title;
        if (typeof js_file !== "string") {
            throw new TypeError("js_file must be a string");
        }
        this.js_file = js_file;
        if (typeof sidebar !== "boolean") {
            throw new TypeError("sidebar must be a boolean");
        }
        this.sidebar = sidebar;

        this.current = false;
    };

    get_html_content = async function(){
        const res = await fetch(this.file);
        const html = await res.text();
        return html;
    }
    
    get_js_content = async function(){
        const res = await fetch(this.js_file);
        const js = await res.text();
        return js;
    }

    move_to = async function() {
        document.title = this.title;

        // remove the page script if it exists
        if (document.getElementById("page_script")) {
            document.getElementById("page_script").remove();
        }

        if (!this.sidebar) {
            // remove the sidebar if it exists
            if (document.getElementById("sidebar") && document.getElementById("sidebar").nodeName === "MAIN"){
                document.getElementById("sidebar").remove();
            }
            // remove the sidebar script if it exists
            if (document.getElementById("sidebar_script")) {
                document.getElementById("sidebar_script").remove();
            }
            // create a non-sidebar content div
            const content = document.createElement("div");
            content.id = "content";
            document.body.appendChild(content);
        } else {
            // remove content if it exists
            if (document.getElementById("content") && document.getElementById("content").nodeName === "DIV") {
                document.getElementById("content").remove();
            }

            // check if sidebar exixts
            if (!document.getElementById("sidebar")) {
                const sidebar = document.createElement("div");
                sidebar.id = "sidebar";
                sidebar.innerHTML = await get_sidebar_content();
                document.body.appendChild(sidebar);
            }

            // check if sidebar script exists
            if (!document.getElementById("sidebar_script")) {
                // add the sidebar script
                const sidebar_script = document.createElement("script");
                sidebar_script.id = "sidebar_script";
                sidebar_script.src = this.js_file;
                document.body.appendChild(sidebar_script);
            }
        };

        // add the html content to the page
        document.getElementById(this.sidebar ? "sidebar" : "content").innerHTML = await this.get_html_content();

        // add the js script to the page
        const page_script = document.createElement("script");
        page_script.id = "page_script";
        page_script.src = this.js_file;
        document.body.appendChild(page_script);

        this.current = true;

        // push the state to the history
        window.history.pushState(
            {
                html: await this.get_html_content(),
                pageTitle: this.title,
                jsFile: this.js_file,
                route: window.location.pathname.replace("/", "")
            },
            "", window.location.pathname.replace("/", "")
        );
    };

}

const routes = {
    'dashboard': new Route("pages/dashboard.html", "Dashboard", "pages/scripts/dashboard.js", true),
    '404': new Route("pages/404.html", "404", "pages/scripts/404.js", false),
    '2fa': new Route("pages/2fa.html", "2FA", "pages/scripts/2fa.js", true),
    'login': new Route("pages/login.html", "Login", "pages/scripts/login.js", false),
    'create': new Route("pages/create.html", "Create", "pages/scripts/create.js", false),
    'sessions': new Route("pages/sessions.html", "Sessions", "pages/scripts/sessions.js", true),
    '2fa-login': new Route("pages/2fa-login.html", "Verify 2FA", "pages/scripts/2fa-login.js", false)
}

const currentRoute = routes[window.location.pathname.replace("/", "")] || false;

(async function() {
    if (currentRoute) {
        await currentRoute.move_to();
    } else {
        await routes["404"].move_to();
    }

})();

function changeUrl(url) {
    // get the new route from the url if not in list return none
    const new_url = routes[url] || false;
    if (new_url) {
        // if the current route is not the new route
        if (currentRoute) {
            // set the current route to false as we are moving to a new route
            currentRoute.current = false;
        }
        new_url.move_to().then(() => {
            // handle successful navigation
        }).catch((error) => {
            // handle error during navigation
            // raise the error
            console.error(error);
        });
    } else {
        routes["404"].move_to().then(() => {
            // handle successful navigation
        }).catch((error) => {
            // handle error during navigation
            console.error(error);
        });
    }
}

window.onpopstate = async function(event) {
    if (event.state) {
        // get the route from the event state
        const route = routes[event.state.route] || false;
        if (route) {
            
            if (!currentRoute === route) {
                // set the current route to false as we are moving to a new route
                currentRoute.current = false;
            }
            route.move_to().then(() => {
                // handle successful navigation
            }).catch((error) => {
                // handle error during navigation
                console.error(error);
            });

        } else {
            routes["404"].move_to().then(() => {
                // handle successful navigation
            }).catch((error) => {
                // handle error during navigation
                console.error(error);
            });
        }
    } else {
        routes["404"].move_to().then(() => {
            // handle successful navigation
        }).catch((error) => {
            // handle error during navigation
            console.error(error);
        });
    }
}