# window.postMessage Receiver

Open `index.htm` in browser and subscribe to URL which you want to check for leaking postAPI message.

It will log leaking messages from child iframe (passed to parent either through `window.parent` or through `window.top`) and from child windows (passed to parent through `window.opener`).

## Demo

You can test this with `kid.htm` - just download both files and open them in the browser. Then take `kid.htm` local address and subscribe to it via UI in `index.htm`. Messages should start coming your way.

You can also try this online:

- [PostMessage Receiver](https://dusekdan.github.io/RandomSecurity/postMessageReceiver/)
- Subscribe to: `https://dusekdan.github.io/RandomSecurity/postMessageReceiver/kid.htm`
