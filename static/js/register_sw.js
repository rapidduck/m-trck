console.log("loaded script")
    if ('serviceWorker' in navigator) {
      addEventListener('load', async () => {
      console.log("before await");
        let sw = await navigator.serviceWorker.register('/sw.js');
        console.log("await finished");
        console.log(sw);
    });
  }