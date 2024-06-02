const SIDEBAR_CONTENT_URL = "pages/components/sidebar.html";
const SIDEBAR_SCRIPT_URL = "pages/components/scripts/sidebar.js";

async function get_sidebar_content() {
    
    const res = await fetch(SIDEBAR_CONTENT_URL);
    const html = await res.text();
    
    return html;
}

class Route{
    constructor(route, file, title, js_file, sidebar){
        if (typeof route !== "string") {
            throw new TypeError("route must be a string");
        }
        this.route = route;
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

    set_loading = function(){
        document.getElementById('content').innerHTML = `
            <div class="h-screen w-full">
                <div class="flex items-center justify-center h-full w-full">
                    <div class="w-16 h-16 border-4 border-dashed rounded-full animate-spin border-violet-600"></div>
                </div>
            </div>
        `
    }

    move_to = async function() {
        document.title = this.title;

        // remove the page script if it exists
        if (document.getElementById("page_script")) {
            document.getElementById("page_script").remove();
        }

        if (!this.sidebar) {
            
            // remove the sidebar if it exists
            if (document.getElementById("sidebar")){
                
                document.getElementById("sidebar").remove();
            }
            // remove the sidebar script if it exists
            if (document.getElementById("sidebar_script")) {
                
                document.getElementById("sidebar_script").remove();
            }

            // remove old content if it exists
            if (document.getElementById("content") !== null && document.getElementById("content").nodeName === "MAIN"){
                document.getElementById("content").remove();

                // create a non-sidebar content div
            }
            const content = document.createElement("div");
            content.id = "content";
            document.body.appendChild(content);
        } else {
            
            // remove content if it exists
            if (document.getElementById("content") !== null){
                if (document.getElementById("content").nodeName !== "MAIN"){
                    console.log("removing content :))) it isnt MAIN")
                    document.getElementById("content").remove();
                }
            }

            // check if sidebar exixts
            if (document.getElementById("sidebar") === null) {
                
                const sidebar = document.createElement("div");
                sidebar.id = "sidebar";
                sidebar.innerHTML = await get_sidebar_content();
                document.body.appendChild(sidebar);
            }

            // check if sidebar script exists
            if (document.getElementById("sidebar_script") === null) {
                
                // add the sidebar script
                const sidebar_script = document.createElement("script");
                sidebar_script.id = "sidebar_script";
                sidebar_script.src = SIDEBAR_SCRIPT_URL;
                document.body.appendChild(sidebar_script);
            }
            
            // get every element with the class of sidebar_link
            const sidebar_links = document.getElementsByClassName("sidebar_link");
            
            // loop through the sidebar links and add the active class to the current link
            for (let i = 0; i < sidebar_links.length; i++) {
                
                if (sidebar_links[i].id === this.route) {
                    
                    sidebar_links[i].classList.add("bg-gray-800", "text-gray-50");
                } else {
                    sidebar_links[i].classList.remove("bg-gray-800", "text-gray-50");
                
                }
            }
            
        };
        
        // add the html content to the page
        document.getElementById('content').innerHTML = await this.get_html_content();

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
                route: this.route
            },
            "", this.route
        );
    };

}

const routes = {
    'dashboard': new Route("dashboard", "pages/dashboard.html", "Dashboard", "pages/scripts/dashboard.js", true),
    '404': new Route("404", "pages/404.html", "404", "pages/scripts/404.js", false),
    '2fa': new Route("2fa", "pages/2fa.html", "2FA", "pages/scripts/2fa.js", true),
    'login': new Route("login", "pages/login.html", "Login", "pages/scripts/login.js", false),
    'create': new Route("create", "pages/create.html", "Create", "pages/scripts/create.js", false),
    'sessions': new Route("sessions", "pages/sessions.html", "Sessions", "pages/scripts/sessions.js", true),
    '2fa-login': new Route("2fa-login", "pages/2fa-login.html", "Verify 2FA", "pages/scripts/2fa-login.js", false)
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
    //currentRoute.set_loading();
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