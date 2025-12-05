# ROC vessel handover webapp

## Dependencies

- npm
- Cargo (+ rust compiler)

## How to run the app

### 1. Enter the project directory

*The directory where this README.md file is located, you might already be here...*

```bash 
cd frontend/drafts/emil1
```

### 2. Install dependencies

```bash
npm ci
```

### 3. Start the development server

```bash
npm start
```

This should open a browser window/tab automatically. The app needs to be hosted on a web server, the files cannot be opened in the browser directly. (javascript modules security restrictions)

---


### 4. Start a zenoh router with websocket support
To allow the app to communicate with a zenoh network, a zenoh router with websocket support must be running and reachable. Start this new in a **separate terminal**, and keep it running while using the app. 

```bash
git submodule update --init
cd zenoh-ts/zenoh-bridge-remote-api
cargo run
```

When the websocket zenoh router is running, the app is practically part of the zenoh network and can publish/subscribe to zenoh resources.