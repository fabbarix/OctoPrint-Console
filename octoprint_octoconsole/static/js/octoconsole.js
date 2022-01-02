const socketUrl = `${location.protocol === 'http:' ? 'ws:' : 'wss:'}//${location.hostname}:${window.octoconsole.ws_port}`;

function authenticate(ws) {
    ws.send(`AUTH:${window.octoconsole.ws_token}`);
}

function attachSocket() {
    return new Promise(function (resolve, reject) {
        try {
            const ws = new WebSocket(socketUrl);
            
            ws.onerror = function(evt) {
                console.error('Failed to connect to console', evt);
            }

            ws.onopen = function(evt) {
                console.log('[octoconsole] Socket Connected');
                authenticate(ws);
                resolve(ws);
            }

        } catch (ex) {
            console.error(`Failed to connect: ${ex.message}`, ex);
            reject(ex);
        }
    });
}

console.log(`Starting OctoConsole - WS: ${socketUrl} - WS Token: ${window.octoconsole.ws_token}`);
const octoconsole = new Terminal({convertEol: true});
const fitter = new FitAddon.FitAddon();
octoconsole.loadAddon(fitter);
octoconsole.open(document.getElementById('octoconsole_terminal'));
fitter.fit();
attachSocket()
    .then(function (ws) {
        const attach = new AttachAddon.AttachAddon(ws);
        octoconsole.loadAddon(attach);
    })
    .catch(function (ex) {
        console.log(ex);
    });

